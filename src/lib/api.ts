import type { Project, AnalysisResult } from '@/types/project';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_URL}/projects`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to fetch projects');
  }

  return response.json();
}

export async function getProject(id: string): Promise<Project | null> {
  const response = await fetch(`${API_URL}/projects/${id}`, {
    headers: getAuthHeaders(),
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to fetch project');
  }

  return response.json();
}

export async function createProject(startupIdea: string, targetMarket?: string): Promise<Project> {
  const response = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      startup_idea: startupIdea,
      target_market: targetMarket || null,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to create project');
  }

  return response.json();
}

export async function updateProjectStatus(id: string, status: Project['status']): Promise<void> {
  const response = await fetch(`${API_URL}/projects/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to update project status');
  }
}

export async function updateProjectAnalysis(id: string, analysis: AnalysisResult): Promise<void> {
  const response = await fetch(`${API_URL}/projects/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      market_analysis: analysis.marketAnalysis,
      cost_prediction: analysis.costPrediction,
      business_strategy: analysis.businessStrategy,
      monetization: analysis.monetization,
      legal_considerations: analysis.legalConsiderations,
      tech_stack: analysis.techStack,
      strategist_critique: analysis.strategistCritique,
      status: 'completed',
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to update project analysis');
  }
}

export async function deleteProject(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/projects/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Failed to delete project');
  }
}

export async function analyzeStartup(
  startupIdea: string,
  targetMarket: string | undefined,
  projectId: string
): Promise<AnalysisResult> {
  const payload = {
    startupIdea,
    targetMarket,
    projectId,
  };

  const fetchWithTimeout = async (
    url: string,
    options: RequestInit,
    timeoutMs: number
  ): Promise<Response> => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
      return await fetch(url, {
        ...options,
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }
  };

  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  // 1) Pre-wake backend
  try {
    await fetchWithTimeout(`${API_URL}/health`, { method: 'GET' }, 12000);
  } catch {
    // If wake fails, we still attempt analyze
  }

  // 2) Analyze (retry once to survive cold starts)
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const response = await fetchWithTimeout(
        `${API_URL}/analyze`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify(payload),
        },
        180000
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error analyzing startup:', response.status, errorData);

        if (attempt === 1 && response.status >= 500) {
          await sleep(8000);
          continue;
        }

        throw new Error(
          errorData.error ||
            `Analysis failed (${response.status}). If the backend was sleeping, wait ~30s and try again.`
        );
      }

      const data = await response.json();
      if (!data?.success) throw new Error(data?.error || 'Analysis failed');

      return data.analysis as AnalysisResult;
    } catch (e) {
      console.warn('Analyze request failed:', e);
      if (attempt === 1) {
        await sleep(8000);
        continue;
      }
      throw new Error(
        e instanceof Error
          ? e.message
          : 'Analysis failed (backend unreachable)'
      );
    }
  }

  throw new Error('Analysis failed');
}

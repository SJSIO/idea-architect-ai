import { supabase } from '@/integrations/supabase/client';

export async function getProjects() {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error fetching projects:', error);
    throw error;
  }

  return data;
}

export async function getProject(id) {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    console.error('Error fetching project:', error);
    throw error;
  }

  return data;
}

export async function createProject(startupIdea, targetMarket) {
  const { data, error } = await supabase
    .from('projects')
    .insert({
      startup_idea: startupIdea,
      target_market: targetMarket || null,
      status: 'pending',
    })
    .select()
    .single();

  if (error) {
    console.error('Error creating project:', error);
    throw error;
  }

  return data;
}

export async function updateProjectStatus(id, status) {
  const { error } = await supabase
    .from('projects')
    .update({ status })
    .eq('id', id);

  if (error) {
    console.error('Error updating project status:', error);
    throw error;
  }
}

export async function updateProjectAnalysis(id, analysis) {
  const { error } = await supabase
    .from('projects')
    .update({
      market_analysis: analysis.marketAnalysis,
      cost_prediction: analysis.costPrediction,
      business_strategy: analysis.businessStrategy,
      monetization: analysis.monetization,
      legal_considerations: analysis.legalConsiderations,
      tech_stack: analysis.techStack,
      strategist_critique: analysis.strategistCritique,
      status: 'completed',
    })
    .eq('id', id);

  if (error) {
    console.error('Error updating project analysis:', error);
    throw error;
  }
}

const DJANGO_API_URL = 'https://idea-architect-ai-1.onrender.com';

export async function analyzeStartup(startupIdea, targetMarket, projectId) {
  // Use only the Django backend (Groq/LangGraph) for analysis.
  // Render deployments often "sleep"; we pre-wake via /health and retry once.

  const payload = {
    startupIdea,
    targetMarket,
    projectId,
  };

  const fetchWithTimeout = async (url, options, timeoutMs) => {
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

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // 1) Pre-wake backend (no CORS preflight for simple GET)
  try {
    await fetchWithTimeout(`${DJANGO_API_URL}/health`, { method: 'GET' }, 12000);
  } catch {
    // If wake fails, we still attempt analyze; retry logic below may recover.
  }

  // 2) Analyze (retry once to survive cold starts)
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const response = await fetchWithTimeout(
        `${DJANGO_API_URL}/analyze`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        },
        // Give enough time for a cold start + analysis.
        120000
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error analyzing startup (Django):', response.status, errorData);

        // Cold start often returns 502/503/504 briefly.
        if (attempt === 1 && response.status >= 500) {
          await sleep(8000);
          continue;
        }

        throw new Error(
          errorData.error ||
            `Analysis failed (Django ${response.status}). If the backend was sleeping, wait ~30s and try again.`
        );
      }

      const data = await response.json();
      if (!data?.success) throw new Error(data?.error || 'Analysis failed');

      return data.analysis;
    } catch (e) {
      console.warn('Django analyze request failed:', e);
      if (attempt === 1) {
        await sleep(8000);
        continue;
      }
      throw new Error(
        e instanceof Error
          ? e.message
          : 'Analysis failed (Django backend unreachable)'
      );
    }
  }

  // Unreachable
  throw new Error('Analysis failed');
}


export async function deleteProject(id) {
  const { error } = await supabase
    .from('projects')
    .delete()
    .eq('id', id);

  if (error) {
    console.error('Error deleting project:', error);
    throw error;
  }
}

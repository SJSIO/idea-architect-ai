import { supabase } from '@/integrations/supabase/client';
import type { Project, AnalysisResult } from '@/types/project';

export async function getProjects(): Promise<Project[]> {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error fetching projects:', error);
    throw error;
  }

  return data as Project[];
}

export async function getProject(id: string): Promise<Project | null> {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    console.error('Error fetching project:', error);
    throw error;
  }

  return data as Project;
}

export async function createProject(startupIdea: string, targetMarket?: string): Promise<Project> {
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

  return data as Project;
}

export async function updateProjectStatus(id: string, status: Project['status']): Promise<void> {
  const { error } = await supabase
    .from('projects')
    .update({ status })
    .eq('id', id);

  if (error) {
    console.error('Error updating project status:', error);
    throw error;
  }
}

export async function updateProjectAnalysis(id: string, analysis: AnalysisResult): Promise<void> {
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

export async function analyzeStartup(
  startupIdea: string,
  targetMarket: string | undefined,
  projectId: string
): Promise<AnalysisResult> {
  // Use the Django backend with Groq Cloud for analysis
  const response = await fetch(`${DJANGO_API_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      startupIdea,
      targetMarket,
      projectId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    console.error('Error analyzing startup:', errorData);
    throw new Error(errorData.error || 'Analysis failed - Django backend may be waking up, please try again in 30 seconds');
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Analysis failed');
  }

  return data.analysis as AnalysisResult;
}

export async function deleteProject(id: string): Promise<void> {
  const { error } = await supabase
    .from('projects')
    .delete()
    .eq('id', id);

  if (error) {
    console.error('Error deleting project:', error);
    throw error;
  }
}

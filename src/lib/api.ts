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

export async function analyzeStartup(
  startupIdea: string,
  targetMarket: string | undefined,
  projectId: string
): Promise<AnalysisResult> {
  const { data, error } = await supabase.functions.invoke('analyze-startup', {
    body: {
      startupIdea,
      targetMarket,
      projectId,
    },
  });

  if (error) {
    console.error('Error analyzing startup:', error);
    throw error;
  }

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

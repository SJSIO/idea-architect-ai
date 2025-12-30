import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { ArrowLeft, Trash2, Clock, Loader2, RefreshCw, Download } from 'lucide-react';
import { exportToPDF } from '@/lib/pdf-export';
import { Header } from '@/components/Header';
import { AgentResultCard } from '@/components/AgentResultCard';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { getProject, deleteProject, analyzeStartup, updateProjectAnalysis, updateProjectStatus } from '@/lib/api';
import { AGENT_CARDS } from '@/types/project';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: project, isLoading, error, refetch } = useQuery({
    queryKey: ['project', id],
    queryFn: () => getProject(id),
    enabled: !!id,
    refetchInterval: (query) => {
      // Refetch every 2 seconds while analyzing
      return query.state.data?.status === 'analyzing' ? 2000 : false;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast({ title: 'Project deleted' });
      navigate('/');
    },
    onError: () => {
      toast({ variant: 'destructive', title: 'Failed to delete project' });
    },
  });

  const retryMutation = useMutation({
    mutationFn: async () => {
      if (!project) throw new Error('No project');
      await updateProjectStatus(project.id, 'analyzing');
      const analysis = await analyzeStartup(
        project.startup_idea,
        project.target_market || undefined,
        project.id
      );
      await updateProjectAnalysis(project.id, analysis);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      toast({ title: 'Analysis complete!' });
    },
    onError: (error) => {
      updateProjectStatus(id, 'failed');
      toast({
        variant: 'destructive',
        title: 'Analysis failed',
        description: error instanceof Error ? error.message : 'Something went wrong',
      });
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-20 text-center">
          <p className="text-destructive mb-4">Project not found</p>
          <Button variant="outline" asChild>
            <Link to="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  const analysisData = {
    marketAnalysis: project.market_analysis,
    costPrediction: project.cost_prediction,
    businessStrategy: project.business_strategy,
    monetization: project.monetization,
    legalConsiderations: project.legal_considerations,
    techStack: project.tech_stack,
    strategistCritique: project.strategist_critique,
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Back button and actions */}
        <div className="flex items-center justify-between mb-6 animate-fade-in">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </Button>

          <div className="flex items-center gap-2">
            {project.status === 'completed' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  exportToPDF(project);
                  toast({ title: 'PDF downloaded', description: 'Your analysis report has been saved.' });
                }}
              >
                <Download className="h-4 w-4 mr-2" />
                Export PDF
              </Button>
            )}
            
            {project.status === 'failed' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => retryMutation.mutate()}
                disabled={retryMutation.isPending}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${retryMutation.isPending ? 'animate-spin' : ''}`} />
                Retry Analysis
              </Button>
            )}
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete this project?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action cannot be undone. All analysis data will be permanently deleted.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => deleteMutation.mutate()}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Project header */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm mb-8 animate-slide-up">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <Badge
                  variant="secondary"
                  className={
                    project.status === 'completed'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : project.status === 'analyzing'
                      ? 'bg-primary/20 text-primary'
                      : project.status === 'failed'
                      ? 'bg-destructive/20 text-destructive'
                      : 'bg-muted text-muted-foreground'
                  }
                >
                  {project.status === 'analyzing' && (
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  )}
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </Badge>
                <CardTitle className="text-2xl mt-3">{project.startup_idea}</CardTitle>
                {project.target_market && (
                  <p className="text-muted-foreground mt-2">
                    Target Market: {project.target_market}
                  </p>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Analysis progress or results */}
        {project.status === 'analyzing' || retryMutation.isPending ? (
          <AnalysisProgress isAnalyzing={true} />
        ) : project.status === 'pending' ? (
          <Card className="border-border/50 bg-card/30 text-center py-12">
            <CardContent>
              <p className="text-muted-foreground">Analysis has not started yet.</p>
            </CardContent>
          </Card>
        ) : project.status === 'failed' ? (
          <Card className="border-destructive/50 bg-destructive/5 text-center py-12">
            <CardContent>
              <p className="text-destructive mb-4">Analysis failed. Please try again.</p>
              <Button
                variant="outline"
                onClick={() => retryMutation.mutate()}
                disabled={retryMutation.isPending}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry Analysis
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4 animate-fade-in">
              Analysis Results
            </h2>
            {AGENT_CARDS.map((agent, index) => (
              <AgentResultCard
                key={agent.id}
                agent={agent}
                content={analysisData[agent.id]}
                index={index}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

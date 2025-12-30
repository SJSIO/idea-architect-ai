import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Rocket, Sparkles, ArrowRight } from 'lucide-react';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { BackendStatus } from '@/components/BackendStatus';
import { useToast } from '@/hooks/use-toast';
import { createProject, analyzeStartup, updateProjectAnalysis, updateProjectStatus } from '@/lib/api';

export default function NewAnalysis() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  const [startupIdea, setStartupIdea] = useState('');
  const [targetMarket, setTargetMarket] = useState('');
  const [backendReady, setBackendReady] = useState(false);

  const analyzeMutation = useMutation({
    mutationFn: async () => {
      // Step 1: Create the project
      const project = await createProject(startupIdea, targetMarket);
      
      // Step 2: Update status to analyzing
      await updateProjectStatus(project.id, 'analyzing');
      
      try {
        // Step 3: Run the analysis
        const analysis = await analyzeStartup(startupIdea, targetMarket || undefined, project.id);
        
        // Step 4: Save the results
        await updateProjectAnalysis(project.id, analysis);
        
        return project.id;
      } catch (error) {
        // Mark as failed if analysis fails
        await updateProjectStatus(project.id, 'failed');
        throw error;
      }
    },
    onSuccess: (projectId) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast({
        title: 'Analysis Complete',
        description: 'Your startup idea has been analyzed by 6 AI agents.',
      });
      navigate(`/project/${projectId}`);
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Analysis Failed',
        description: error instanceof Error ? error.message : 'Something went wrong',
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!startupIdea.trim()) {
      toast({
        variant: 'destructive',
        title: 'Missing Information',
        description: 'Please describe your startup idea.',
      });
      return;
    }
    analyzeMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary/10 mb-6 glow-effect">
            <Rocket className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-3">
            Analyze Your <span className="gradient-text">Startup Idea</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            Our AI agents will analyze your idea across 6 key dimensions, 
            then debate and refine the strategy for maximum insight.
          </p>
        </div>

        <Card className="border-border/50 bg-card/50 backdrop-blur-sm animate-slide-up">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Startup Details
            </CardTitle>
            <CardDescription>
              Provide as much detail as possible for better analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="idea">Startup Idea *</Label>
                <Textarea
                  id="idea"
                  placeholder="Describe your startup idea in detail. What problem does it solve? Who are your customers? What makes it unique?"
                  value={startupIdea}
                  onChange={(e) => setStartupIdea(e.target.value)}
                  className="min-h-[150px] bg-background/50 border-border/50 focus:border-primary/50"
                  disabled={analyzeMutation.isPending}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="market">Target Market (Optional)</Label>
                <Input
                  id="market"
                  placeholder="e.g., Small business owners in North America, Gen Z consumers in Asia"
                  value={targetMarket}
                  onChange={(e) => setTargetMarket(e.target.value)}
                  className="bg-background/50 border-border/50 focus:border-primary/50"
                  disabled={analyzeMutation.isPending}
                />
              </div>

              <BackendStatus onStatusChange={setBackendReady} />

              <AnalysisProgress isAnalyzing={analyzeMutation.isPending} />

              <Button
                type="submit"
                variant="hero"
                size="lg"
                className="w-full"
                disabled={analyzeMutation.isPending || !startupIdea.trim() || !backendReady}
              >
                {analyzeMutation.isPending ? (
                  <>
                    <Sparkles className="h-5 w-5 animate-pulse" />
                    AI Agents Working...
                  </>
                ) : !backendReady ? (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Waiting for Backend...
                  </>
                ) : (
                  <>
                    Start Analysis
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="mt-8 grid grid-cols-3 gap-4 opacity-0 animate-fade-in stagger-3">
          {[
            { icon: '🤖', label: '6 AI Agents', desc: 'Specialized analysis' },
            { icon: '⚔️', label: 'Debate Loop', desc: 'Strategist vs Critic' },
            { icon: '📊', label: 'Comprehensive', desc: 'Market to Tech' },
          ].map((feature) => (
            <Card key={feature.label} className="bg-card/30 border-border/30 text-center p-4">
              <span className="text-2xl mb-2 block">{feature.icon}</span>
              <h3 className="font-semibold text-sm">{feature.label}</h3>
              <p className="text-xs text-muted-foreground">{feature.desc}</p>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { Loader2, Sparkles, Brain, CheckCircle2, Zap } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const ANALYSIS_STEPS = [
  { id: 0, label: 'Orchestrator', icon: '🎭', duration: 5, description: 'Evaluating idea & selecting agents' },
  { id: 1, label: 'Market Analyst', icon: '📈', duration: 10, description: 'Analyzing market opportunity' },
  { id: 2, label: 'Cost Predictor', icon: '💰', duration: 10, description: 'Estimating costs & funding' },
  { id: 3, label: 'Business Strategist', icon: '🎯', duration: 10, description: 'Building go-to-market strategy' },
  { id: 4, label: 'Legal Advisor', icon: '⚖️', duration: 10, description: 'Reviewing compliance & IP' },
];

interface AnalysisProgressProps {
  isAnalyzing: boolean;
  orchestratorData?: {
    selectedAgents?: string[];
    reasoning?: string;
    startupCategory?: string;
    complexityScore?: number;
  };
}

export function AnalysisProgress({ isAnalyzing, orchestratorData }: AnalysisProgressProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isAnalyzing) {
      setCurrentStep(0);
      setProgress(0);
      return;
    }

    // Simulate progress through steps
    let stepIndex = 0;
    let stepProgress = 0;
    
    const interval = setInterval(() => {
      if (stepIndex >= ANALYSIS_STEPS.length) {
        clearInterval(interval);
        return;
      }

      const step = ANALYSIS_STEPS[stepIndex];
      const stepDuration = step.duration * 10; // Convert to intervals (100ms each)
      
      stepProgress += 1;
      const totalStepsComplete = (stepIndex / ANALYSIS_STEPS.length) * 100;
      const currentStepProgress = (stepProgress / stepDuration) * (100 / ANALYSIS_STEPS.length);
      
      setProgress(Math.min(totalStepsComplete + currentStepProgress, 95));
      setCurrentStep(stepIndex);

      if (stepProgress >= stepDuration) {
        stepIndex += 1;
        stepProgress = 0;
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isAnalyzing]);

  if (!isAnalyzing) return null;

  const activeStep = ANALYSIS_STEPS[currentStep] || ANALYSIS_STEPS[0];

  return (
    <Card className="border-primary/30 bg-card/50 backdrop-blur-sm overflow-hidden animate-fade-in">
      <CardContent className="pt-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="relative">
            <div className="h-12 w-12 rounded-xl bg-primary/20 flex items-center justify-center animate-pulse-glow">
              <Brain className="h-6 w-6 text-primary animate-pulse" />
            </div>
            <Sparkles className="absolute -top-1 -right-1 h-4 w-4 text-primary animate-bounce" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">AI Agents Analyzing...</h3>
            <p className="text-sm text-muted-foreground">
              Orchestrator + specialist agents + strategist/critic debate
            </p>
          </div>
        </div>

        {/* Orchestrator Info */}
        {currentStep === 0 && (
          <div className="mb-4 p-3 rounded-lg bg-primary/10 border border-primary/20">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">Orchestrator Deciding...</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Analyzing your startup idea to determine which specialist agents are most relevant
            </p>
          </div>
        )}

        {/* Show orchestrator results if available */}
        {orchestratorData?.selectedAgents && orchestratorData.selectedAgents.length > 0 && (
          <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span className="text-sm font-medium text-emerald-400">Orchestrator Decision</span>
              {orchestratorData.startupCategory && (
                <Badge variant="secondary" className="text-xs">
                  {orchestratorData.startupCategory}
                </Badge>
              )}
              {orchestratorData.complexityScore && (
                <Badge variant="outline" className="text-xs">
                  Complexity: {orchestratorData.complexityScore}/10
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-1 mb-2">
              {orchestratorData.selectedAgents.map((agent) => (
                <Badge key={agent} variant="secondary" className="text-xs bg-primary/20">
                  {agent.replace('_', ' ')}
                </Badge>
              ))}
            </div>
            {orchestratorData.reasoning && (
              <p className="text-xs text-muted-foreground">{orchestratorData.reasoning}</p>
            )}
          </div>
        )}

        <Progress value={progress} className="h-2 mb-6" />

        {/* Current step highlight */}
        <div className="mb-4 p-3 rounded-lg bg-muted/30">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{activeStep.icon}</span>
            <div>
              <p className="font-medium">{activeStep.label}</p>
              <p className="text-sm text-muted-foreground">{activeStep.description}</p>
            </div>
            <Loader2 className="h-5 w-5 animate-spin ml-auto text-primary" />
          </div>
        </div>

        <div className="grid grid-cols-5 gap-2 sm:grid-cols-5">
          {ANALYSIS_STEPS.map((step, index) => (
            <div
              key={step.id}
              className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-all ${
                index < currentStep
                  ? 'bg-primary/20 text-primary'
                  : index === currentStep
                  ? 'bg-primary/10 text-foreground ring-1 ring-primary/50'
                  : 'bg-muted/30 text-muted-foreground'
              }`}
            >
              <span className="text-lg">{step.icon}</span>
              <span className="text-[10px] font-medium text-center leading-tight">{step.label}</span>
              {index < currentStep && (
                <CheckCircle2 className="h-3 w-3 text-primary" />
              )}
              {index === currentStep && (
                <Loader2 className="h-3 w-3 animate-spin" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

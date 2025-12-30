import { useEffect, useState } from 'react';
import { Loader2, Sparkles, Brain, CheckCircle2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';

const ANALYSIS_STEPS = [
  { id: 1, label: 'Market Analyst', icon: '📈', duration: 8 },
  { id: 2, label: 'Cost Predictor', icon: '💰', duration: 8 },
  { id: 3, label: 'Business Strategist', icon: '🎯', duration: 8 },
  { id: 4, label: 'Monetization Expert', icon: '💳', duration: 8 },
  { id: 5, label: 'Legal Advisor', icon: '⚖️', duration: 8 },
  { id: 6, label: 'Tech Architect', icon: '💻', duration: 8 },
  { id: 7, label: 'Strategic Synthesis', icon: '🔮', duration: 15 },
  { id: 8, label: 'Critic Review', icon: '🔍', duration: 10 },
  { id: 9, label: 'Final Refinement', icon: '✨', duration: 10 },
];

export function AnalysisProgress({ isAnalyzing }) {
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
              6 specialized agents + strategist/critic debate
            </p>
          </div>
        </div>

        <Progress value={progress} className="h-2 mb-6" />

        <div className="grid grid-cols-3 gap-2">
          {ANALYSIS_STEPS.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center gap-2 p-2 rounded-lg transition-all ${
                index < currentStep
                  ? 'bg-primary/20 text-primary'
                  : index === currentStep
                  ? 'bg-primary/10 text-foreground animate-pulse'
                  : 'bg-muted/30 text-muted-foreground'
              }`}
            >
              <span className="text-lg">{step.icon}</span>
              <span className="text-xs font-medium truncate">{step.label}</span>
              {index < currentStep && (
                <CheckCircle2 className="h-3 w-3 text-primary ml-auto" />
              )}
              {index === currentStep && (
                <Loader2 className="h-3 w-3 animate-spin ml-auto" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

import { Link } from 'react-router-dom';
import { Rocket, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
      <div className="relative mb-8">
        <div className="h-24 w-24 rounded-3xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center glow-effect">
          <Rocket className="h-12 w-12 text-primary" />
        </div>
        <Sparkles className="absolute -top-2 -right-2 h-6 w-6 text-primary animate-bounce" />
      </div>
      
      <h2 className="text-2xl font-bold mb-3">No projects yet</h2>
      <p className="text-muted-foreground max-w-md mb-8">
        Start by analyzing your first startup idea. Our AI agents will provide 
        comprehensive insights across market, costs, strategy, and more.
      </p>

      <Button variant="hero" size="lg" asChild>
        <Link to="/new" className="flex items-center gap-2">
          Analyze Your First Idea
          <ArrowRight className="h-5 w-5" />
        </Link>
      </Button>
    </div>
  );
}

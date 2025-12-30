import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { ArrowRight, Clock, CheckCircle2, Loader2, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const statusConfig = {
  pending: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-muted text-muted-foreground',
  },
  analyzing: {
    label: 'Analyzing',
    icon: Loader2,
    className: 'bg-primary/20 text-primary',
  },
  completed: {
    label: 'Completed',
    icon: CheckCircle2,
    className: 'bg-emerald-500/20 text-emerald-400',
  },
  failed: {
    label: 'Failed',
    icon: XCircle,
    className: 'bg-destructive/20 text-destructive',
  },
};

export function ProjectCard({ project, index }) {
  const status = statusConfig[project.status];
  const StatusIcon = status.icon;

  return (
    <Link to={`/project/${project.id}`}>
      <Card 
        className={`group relative overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm hover:bg-card/80 hover:border-primary/30 transition-all duration-300 cursor-pointer opacity-0 animate-slide-up stagger-${Math.min(index + 1, 6)}`}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-4">
            <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-primary transition-colors">
              {project.startup_idea.length > 80 
                ? `${project.startup_idea.substring(0, 80)}...` 
                : project.startup_idea}
            </h3>
            <Badge variant="secondary" className={status.className}>
              <StatusIcon className={`h-3 w-3 mr-1 ${project.status === 'analyzing' ? 'animate-spin' : ''}`} />
              {status.label}
            </Badge>
          </div>
        </CardHeader>

        <CardContent>
          {project.target_market && (
            <p className="text-sm text-muted-foreground mb-3 line-clamp-1">
              Target: {project.target_market}
            </p>
          )}
          
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
            </span>
            <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all text-primary" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

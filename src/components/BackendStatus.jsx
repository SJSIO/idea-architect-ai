import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const DJANGO_API_URL = 'https://idea-architect-ai-1.onrender.com';

export function BackendStatus({ onStatusChange }) {
  const [status, setStatus] = useState('checking');
  const [retryCount, setRetryCount] = useState(0);

  const checkHealth = async () => {
    setStatus('checking');
    
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(`${DJANGO_API_URL}/health`, {
        method: 'GET',
        signal: controller.signal,
      });
      
      clearTimeout(timeout);
      
      if (response.ok) {
        setStatus('ready');
        onStatusChange?.(true);
      } else {
        setStatus('waking');
        onStatusChange?.(false);
        // Retry after a delay
        setTimeout(() => setRetryCount(c => c + 1), 5000);
      }
    } catch {
      // If it's a network error, the backend is likely sleeping
      setStatus('waking');
      onStatusChange?.(false);
      // Retry after a delay
      setTimeout(() => setRetryCount(c => c + 1), 5000);
    }
  };

  useEffect(() => {
    checkHealth();
  }, [retryCount]);

  // Stop retrying after 6 attempts (30 seconds)
  useEffect(() => {
    if (retryCount >= 6 && status === 'waking') {
      setStatus('offline');
      onStatusChange?.(false);
    }
  }, [retryCount, status, onStatusChange]);

  const handleRetry = () => {
    setRetryCount(0);
    checkHealth();
  };

  const statusConfig = {
    checking: {
      icon: <Loader2 className="h-4 w-4 animate-spin" />,
      text: 'Checking backend...',
      color: 'text-muted-foreground',
      bgColor: 'bg-muted/50',
      borderColor: 'border-border/50',
    },
    ready: {
      icon: <CheckCircle2 className="h-4 w-4" />,
      text: 'Backend Ready (Groq/LangGraph)',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/30',
    },
    waking: {
      icon: <Loader2 className="h-4 w-4 animate-spin" />,
      text: 'Waking up backend...',
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/30',
    },
    offline: {
      icon: <XCircle className="h-4 w-4" />,
      text: 'Backend unavailable',
      color: 'text-destructive',
      bgColor: 'bg-destructive/10',
      borderColor: 'border-destructive/30',
    },
  };

  const config = statusConfig[status];

  return (
    <div
      className={cn(
        'flex items-center justify-between gap-3 px-4 py-3 rounded-lg border transition-all duration-300',
        config.bgColor,
        config.borderColor
      )}
    >
      <div className={cn('flex items-center gap-2', config.color)}>
        {config.icon}
        <span className="text-sm font-medium">{config.text}</span>
      </div>
      
      {(status === 'offline' || status === 'waking') && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRetry}
          className="h-7 px-2 text-xs"
        >
          <RefreshCw className="h-3 w-3 mr-1" />
          Retry
        </Button>
      )}
      
      {status === 'waking' && (
        <span className="text-xs text-muted-foreground">
          Attempt {Math.min(retryCount + 1, 6)}/6
        </span>
      )}
    </div>
  );
}

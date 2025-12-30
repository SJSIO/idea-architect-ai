import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatContentForDisplay } from '@/lib/format-content';

export function AgentResultCard({ agent, content, index }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  // Format content to remove asterisks
  const formattedContent = content ? formatContentForDisplay(content) : null;

  const handleCopy = async () => {
    if (!formattedContent) return;
    await navigator.clipboard.writeText(formattedContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!content) {
    return (
      <Card className={`border-border/50 bg-card/30 opacity-0 animate-slide-up stagger-${Math.min(index + 1, 6)}`}>
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-lg">
            <span className="text-2xl">{agent.icon}</span>
            <span className="text-muted-foreground">{agent.title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm italic">Analysis not available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className={cn(
        'border-border/50 bg-card/50 backdrop-blur-sm overflow-hidden opacity-0 animate-slide-up',
        `stagger-${Math.min(index + 1, 6)}`,
        `bg-gradient-to-br ${agent.color}`
      )}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3 text-lg">
            <span className="text-2xl">{agent.icon}</span>
            <div>
              <span className="text-foreground">{agent.title}</span>
              <p className="text-xs text-muted-foreground font-normal mt-0.5">
                {agent.description}
              </p>
            </div>
          </CardTitle>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={handleCopy}
            >
              {copied ? (
                <Check className="h-4 w-4 text-emerald-400" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-2">
          <div className="prose prose-sm prose-invert max-w-none">
            <div className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">
              {formattedContent}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

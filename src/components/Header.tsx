import { Link, useLocation } from 'react-router-dom';
import { Rocket, LayoutDashboard, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors">
            <Rocket className="h-5 w-5 text-primary" />
          </div>
          <span className="text-xl font-bold tracking-tight">
            Startup<span className="text-primary">AI</span>
          </span>
        </Link>

        <nav className="flex items-center gap-2">
          <Button
            variant={location.pathname === '/' ? 'secondary' : 'ghost'}
            size="sm"
            asChild
          >
            <Link to="/" className="flex items-center gap-2">
              <LayoutDashboard className="h-4 w-4" />
              Dashboard
            </Link>
          </Button>
          <Button
            variant={location.pathname === '/new' ? 'default' : 'outline'}
            size="sm"
            asChild
          >
            <Link to="/new" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Analysis
            </Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}

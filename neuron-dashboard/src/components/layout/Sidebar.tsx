import { Link, useLocation } from 'react-router-dom';
import { 
  FolderGit2, 
  Bot, 
  GitBranch, 
  ScrollText, 
  Settings, 
  LogOut,
  Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

const navItems = [
  { icon: FolderGit2, label: 'Projects', path: '/dashboard' },
  { icon: Bot, label: 'Agents', path: '/dashboard/agents' },
  { icon: GitBranch, label: 'Pipeline', path: '/dashboard/pipeline' },
  { icon: ScrollText, label: 'Logs', path: '/dashboard/logs' },
  { icon: Settings, label: 'Settings', path: '/dashboard/settings' },
];

export const Sidebar = () => {
  const location = useLocation();
  const { logout, user } = useAuth();

  return (
    <aside className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-sidebar-border">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <Zap className="w-5 h-5 text-primary-foreground" />
        </div>
        <span className="font-semibold text-lg text-sidebar-foreground">Neuron</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3">
        <ul className="space-y-1">
          {navItems.map(({ icon: Icon, label, path }) => {
            const isActive = location.pathname === path || 
              (path === '/dashboard' && location.pathname === '/dashboard');
            
            return (
              <li key={path}>
                <Link
                  to={path}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    isActive 
                      ? 'bg-sidebar-accent text-sidebar-primary' 
                      : 'text-sidebar-foreground hover:bg-sidebar-accent/50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <Separator className="bg-sidebar-border" />

      {/* User section */}
      <div className="p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
            {user?.email?.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">
              {user?.email}
            </p>
          </div>
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          className="w-full justify-start text-muted-foreground hover:text-destructive"
          onClick={logout}
        >
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </aside>
  );
};

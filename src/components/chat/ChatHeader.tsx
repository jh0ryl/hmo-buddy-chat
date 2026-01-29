import { Activity, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';

interface ChatHeaderProps {
  onClearChat?: () => void;
}

export const ChatHeader = ({ onClearChat }: ChatHeaderProps) => {
  return (
    <header className="border-b border-border bg-card px-6 py-4">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">HMO Assistant</h1>
            <p className="text-sm text-muted-foreground">Employee Support Portal</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {onClearChat && (
            <Button variant="ghost" size="sm" onClick={onClearChat}>
              Clear Chat
            </Button>
          )}
          <Button variant="outline" size="sm">
            Log in
          </Button>
          <Button size="sm">
            Sign up
          </Button>
          <ThemeToggle />
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};

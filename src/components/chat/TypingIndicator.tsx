import { Bot } from 'lucide-react';

export const TypingIndicator = () => {
  return (
    <div className="flex gap-3 p-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground">
        <Bot className="h-5 w-5" />
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-card border border-border px-4 py-3 shadow-sm">
        <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.3s]" />
        <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:-0.15s]" />
        <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" />
      </div>
    </div>
  );
};

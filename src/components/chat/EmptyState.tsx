import { MessageSquare, FileText, Users, Calendar } from 'lucide-react';

const suggestions = [
  {
    icon: FileText,
    title: 'Policy Questions',
    description: 'Ask about coverage details and benefits',
  },
  {
    icon: Users,
    title: 'Member Support',
    description: 'Help with member inquiries and claims',
  },
  {
    icon: Calendar,
    title: 'Appointments',
    description: 'Scheduling and availability info',
  },
];

export const EmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary mb-6">
        <MessageSquare className="h-8 w-8" />
      </div>
      <h2 className="text-2xl font-semibold text-foreground mb-2">
        How can I help you today?
      </h2>
      <p className="text-muted-foreground mb-8 max-w-md">
        I'm your HMO employee assistant. Ask me about policies, member support, claims processing, or any other work-related questions.
      </p>
      <div className="grid gap-4 sm:grid-cols-3 max-w-2xl w-full">
        {suggestions.map((suggestion) => (
          <div
            key={suggestion.title}
            className="flex flex-col items-center gap-2 p-4 rounded-xl bg-card border border-border hover:border-primary/50 transition-colors cursor-pointer"
          >
            <suggestion.icon className="h-6 w-6 text-primary" />
            <span className="font-medium text-foreground">{suggestion.title}</span>
            <span className="text-xs text-muted-foreground">{suggestion.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

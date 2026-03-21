import { ReactNode } from 'react';
import { Card, CardContent, Button } from '@encypher/design-system';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="py-16 text-center">
        {icon ? (
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
            {icon}
          </div>
        ) : null}
        <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-2">{title}</h3>
        {description && (
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">{description}</p>
        )}
        {actionLabel && onAction && (
          <Button variant="primary" onClick={onAction}>
            {actionLabel}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

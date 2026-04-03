/**
 * Encypher EmptyState Component
 * Centered empty state with icon, title, description, and optional action
 */

import * as React from 'react';
import { cn } from '../utils/cn';
import { Button } from './button';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void; href?: string };
  className?: string;
}

export const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ icon, title, description, action, className }, ref) => {
    const actionButton = action ? (
      <Button variant="primary" onClick={action.onClick}>
        {action.label}
      </Button>
    ) : null;

    const wrappedAction = action?.href ? (
      <a href={action.href}>{actionButton}</a>
    ) : (
      actionButton
    );

    return (
      <div
        ref={ref}
        className={cn(
          'flex flex-col items-center justify-center text-center py-12 gap-4',
          className,
        )}
      >
        {icon && (
          <div className="w-16 h-16 bg-gradient-to-br from-columbia-blue/20 to-blue-ncs/20 rounded-2xl flex items-center justify-center">
            <div className="w-10 h-10 bg-gradient-to-br from-columbia-blue to-blue-ncs rounded-xl flex items-center justify-center text-white">
              {icon}
            </div>
          </div>
        )}
        <h3 className="text-lg font-semibold text-delft-blue dark:text-white">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-muted-foreground max-w-sm">{description}</p>
        )}
        {wrappedAction}
      </div>
    );
  }
);

EmptyState.displayName = 'EmptyState';

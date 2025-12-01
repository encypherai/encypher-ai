/**
 * Encypher Badge Component
 * 
 * Used for status indicators, tags, and permission labels
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /**
   * Badge variant
   * - default: Muted background
   * - primary: Blue NCS
   * - secondary: Light gray
   * - success: Green
   * - warning: Yellow/Orange
   * - destructive: Red
   * - outline: Border only
   */
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline';
  
  /**
   * Badge size
   */
  size?: 'sm' | 'md' | 'lg';
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          // Base styles
          'inline-flex items-center font-medium rounded-full',
          
          // Size styles
          size === 'sm' && 'px-2 py-0.5 text-xs',
          size === 'md' && 'px-2.5 py-0.5 text-xs',
          size === 'lg' && 'px-3 py-1 text-sm',
          
          // Variant styles
          variant === 'default' && 'bg-muted text-muted-foreground',
          variant === 'primary' && 'bg-blue-ncs/10 text-blue-ncs',
          variant === 'secondary' && 'bg-secondary text-secondary-foreground',
          variant === 'success' && 'bg-success/10 text-success',
          variant === 'warning' && 'bg-warning/10 text-warning',
          variant === 'destructive' && 'bg-destructive/10 text-destructive',
          variant === 'outline' && 'border border-current bg-transparent',
          
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

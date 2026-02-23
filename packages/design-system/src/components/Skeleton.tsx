/**
 * Encypher Skeleton Component
 * Flexible skeleton loader for any shape
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, variant = 'rectangular', width, height, lines = 1, style, ...props }, ref) => {
    const sizeStyle: React.CSSProperties = {
      ...style,
      width: width !== undefined ? (typeof width === 'number' ? `${width}px` : width) : undefined,
      height: height !== undefined ? (typeof height === 'number' ? `${height}px` : height) : undefined,
    };

    if (variant === 'text' && lines > 1) {
      return (
        <div ref={ref} className={cn('space-y-2', className)} {...props}>
          {Array.from({ length: lines }, (_, i) => (
            <div
              key={i}
              className={cn(
                'bg-muted animate-pulse rounded h-4',
                i === lines - 1 && 'w-3/4',
              )}
              style={i === lines - 1 ? undefined : sizeStyle}
            />
          ))}
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          'bg-muted animate-pulse',
          variant === 'text' && 'rounded h-4',
          variant === 'circular' && 'rounded-full',
          variant === 'rectangular' && 'rounded-lg',
          className,
        )}
        style={sizeStyle}
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';

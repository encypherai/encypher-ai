/**
 * Encypher Avatar Component
 * User avatar - shows image if available, falls back to initials
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface AvatarProps {
  name?: string;
  src?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'w-6 h-6 text-xs',
  md: 'w-8 h-8 text-sm',
  lg: 'w-10 h-10 text-base',
  xl: 'w-14 h-14 text-xl',
} as const;

function getInitials(name: string): string {
  const words = name.trim().split(/\s+/);
  if (words.length >= 2) {
    return (words[0][0] + words[words.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ name, src, size = 'md', className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'relative inline-flex shrink-0 rounded-full overflow-hidden',
          sizeClasses[size],
          !src && 'bg-gradient-to-br from-blue-ncs to-delft-blue items-center justify-center text-white font-semibold',
          className,
        )}
      >
        {src ? (
          <img
            src={src}
            alt={name || 'Avatar'}
            className="rounded-full object-cover w-full h-full"
          />
        ) : (
          <span>{name ? getInitials(name) : '?'}</span>
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';

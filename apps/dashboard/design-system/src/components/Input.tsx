/**
 * Encypher Input Component
 * Form input with consistent styling
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Input variant
   */
  variant?: 'default' | 'filled';
  
  /**
   * Input size
   */
  inputSize?: 'sm' | 'md' | 'lg';
  
  /**
   * Error state
   */
  error?: boolean;
  
  /**
   * Success state
   */
  success?: boolean;
  
  /**
   * Icon before input
   */
  leftIcon?: React.ReactNode;
  
  /**
   * Icon after input
   */
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      variant = 'default',
      inputSize = 'md',
      error = false,
      success = false,
      leftIcon,
      rightIcon,
      ...props
    },
    ref
  ) => {
    const hasIcons = leftIcon || rightIcon;

    return (
      <div className="relative w-full">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {leftIcon}
          </div>
        )}
        
        <input
          type={type}
          className={cn(
            'flex w-full rounded-lg border bg-background px-3 py-2',
            'text-sm ring-offset-background',
            'file:border-0 file:bg-transparent file:text-sm file:font-medium',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'transition-colors',
            
            // Variant styles
            {
              'border-input': variant === 'default',
              'border-transparent bg-muted': variant === 'filled',
            },
            
            // Size styles
            {
              'h-8 text-xs': inputSize === 'sm',
              'h-10 text-sm': inputSize === 'md',
              'h-12 text-base': inputSize === 'lg',
            },
            
            // Icon padding
            {
              'pl-10': leftIcon,
              'pr-10': rightIcon,
            },
            
            // State styles
            {
              'border-destructive focus-visible:ring-destructive': error,
              'border-success focus-visible:ring-success': success,
            },
            
            className
          )}
          ref={ref}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {rightIcon}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

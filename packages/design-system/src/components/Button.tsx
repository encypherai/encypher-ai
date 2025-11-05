/**
 * Encypher Button Component
 * 
 * Primary variant uses Columbia Blue (#b7d5ed) with white text
 * for high contrast and excellent CTA visibility
 */

import * as React from 'react';
import { cn } from '../utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button variant
   * - primary: Columbia Blue with white text (HIGH CONTRAST - best for CTAs)
   * - secondary: Light gray background
   * - outline: Border only
   * - ghost: Transparent background
   * - destructive: Red for dangerous actions
   * - success: Green for positive actions
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success';
  
  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  
  /**
   * Full width button
   */
  fullWidth?: boolean;
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Icon before text
   */
  leftIcon?: React.ReactNode;
  
  /**
   * Icon after text
   */
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      loading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center gap-2',
          'font-medium transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50',
          'rounded-lg',
          
          // Variant styles
          {
            // PRIMARY: Columbia Blue with white text - HIGH CONTRAST for CTAs
            'bg-columbia-blue text-white hover:bg-columbia-blue/90 active:bg-columbia-blue/80': 
              variant === 'primary',
            'focus-visible:ring-columbia-blue': variant === 'primary' || variant === 'outline',
            
            // SECONDARY: Light background
            'bg-secondary text-secondary-foreground hover:bg-secondary/80': 
              variant === 'secondary',
            'focus-visible:ring-secondary': variant === 'secondary',
            
            // OUTLINE: Border with transparent background
            'border-2 border-columbia-blue text-columbia-blue bg-transparent': 
              variant === 'outline',
            'hover:bg-columbia-blue hover:text-white': variant === 'outline',
            
            // GHOST: Transparent background
            'text-delft-blue hover:bg-muted': variant === 'ghost',
            'focus-visible:ring-muted': variant === 'ghost',
            
            // DESTRUCTIVE: Red for dangerous actions
            'bg-destructive text-destructive-foreground hover:bg-destructive/90': 
              variant === 'destructive',
            'focus-visible:ring-destructive': variant === 'destructive',
            
            // SUCCESS: Green for positive actions
            'bg-success text-success-foreground hover:bg-success/90': 
              variant === 'success',
            'focus-visible:ring-success': variant === 'success',
          },
          
          // Size styles
          {
            'h-8 px-3 text-sm': size === 'sm',
            'h-10 px-4 text-base': size === 'md',
            'h-12 px-6 text-lg': size === 'lg',
            'h-14 px-8 text-xl': size === 'xl',
          },
          
          // Full width
          fullWidth && 'w-full',
          
          className
        )}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {!loading && leftIcon && <span className="inline-flex">{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span className="inline-flex">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';

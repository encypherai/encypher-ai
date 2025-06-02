import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  fullScreen?: boolean;
  text?: string;
}

export default function Loading({ 
  size = 'md', 
  className = '', 
  fullScreen = false,
  text
}: LoadingProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const spinner = (
    <div className={`animate-spin rounded-full border-t-2 border-b-2 border-primary-500 ${sizeClasses[size]} ${className}`} />
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white/80 dark:bg-gray-900/80 z-50">
        {spinner}
        {text && <p className="mt-4 text-sm text-gray-600 dark:text-gray-300">{text}</p>}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-6">
      {spinner}
      {text && <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{text}</p>}
    </div>
  );
}

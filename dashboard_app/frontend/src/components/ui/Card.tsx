import React from 'react';

interface CardProps {
  title?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerContent?: React.ReactNode;
}

export default function Card({ title, children, className = '', headerContent }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {(title || headerContent) && (
        <div className="mb-4">
          {title && <h2 className="text-md sm:text-lg font-medium text-gray-900 dark:text-white">{title}</h2>}
          {headerContent && <div className="mt-2">{headerContent}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

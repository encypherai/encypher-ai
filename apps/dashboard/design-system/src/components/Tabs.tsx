/**
 * Encypher Tabs Component
 * Compound tabs with underline and pills variants
 */

import * as React from 'react';
import { cn } from '../utils/cn';

// -- Context --

interface TabsContextValue {
  value: string;
  onChange: (v: string) => void;
  variant: 'underline' | 'pills';
}

const TabsContext = React.createContext<TabsContextValue | null>(null);

function useTabsContext(): TabsContextValue {
  const ctx = React.useContext(TabsContext);
  if (!ctx) {
    throw new Error('Tabs compound components must be used within <Tabs>');
  }
  return ctx;
}

// -- Tabs root --

export interface TabsProps {
  value: string;
  onChange: (v: string) => void;
  children: React.ReactNode;
  className?: string;
}

export const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ value, onChange, children, className }, ref) => {
    return (
      <TabsContext.Provider value={{ value, onChange, variant: 'underline' }}>
        <div ref={ref} className={className}>
          {children}
        </div>
      </TabsContext.Provider>
    );
  }
);

Tabs.displayName = 'Tabs';

// -- TabList --

export interface TabListProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'underline' | 'pills';
}

export const TabList = React.forwardRef<HTMLDivElement, TabListProps>(
  ({ children, className, variant = 'underline' }, ref) => {
    const ctx = useTabsContext();

    return (
      <TabsContext.Provider value={{ ...ctx, variant }}>
        <div
          ref={ref}
          role="tablist"
          className={cn(
            'flex gap-1',
            variant === 'underline' && 'border-b border-border',
            className,
          )}
        >
          {children}
        </div>
      </TabsContext.Provider>
    );
  }
);

TabList.displayName = 'TabList';

// -- Tab --

export interface TabProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
}

export const Tab = React.forwardRef<HTMLButtonElement, TabProps>(
  ({ value, children, disabled = false }, ref) => {
    const { value: activeValue, onChange, variant } = useTabsContext();
    const isActive = value === activeValue;

    return (
      <button
        ref={ref}
        type="button"
        role="tab"
        aria-selected={isActive}
        disabled={disabled}
        onClick={() => onChange(value)}
        className={cn(
          'px-3 py-2 text-sm font-medium transition-all duration-200',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          'disabled:pointer-events-none disabled:opacity-50',
          variant === 'underline' && [
            '-mb-px',
            isActive
              ? 'border-b-2 border-blue-ncs text-blue-ncs'
              : 'text-muted-foreground hover:text-foreground',
          ],
          variant === 'pills' && [
            'rounded-lg',
            isActive
              ? 'bg-blue-ncs text-white'
              : 'text-muted-foreground hover:bg-muted',
          ],
        )}
      >
        {children}
      </button>
    );
  }
);

Tab.displayName = 'Tab';

// -- TabPanel --

export interface TabPanelProps {
  value: string;
  active: string;
  children: React.ReactNode;
  className?: string;
}

export const TabPanel = React.forwardRef<HTMLDivElement, TabPanelProps>(
  ({ value, active, children, className }, ref) => {
    if (value !== active) return null;

    return (
      <div ref={ref} role="tabpanel" className={className}>
        {children}
      </div>
    );
  }
);

TabPanel.displayName = 'TabPanel';

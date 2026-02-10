'use client';

import { ThemeProvider } from 'next-themes';
import { ToastProvider } from '@/components/ui/use-toast';
import { useEffect, useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  // Add this to prevent hydration mismatch during initial render
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <ThemeProvider 
      attribute="class" 
      defaultTheme="system" 
      enableSystem
      disableTransitionOnChange
    >
      <ToastProvider>
        {mounted ? children : <div style={{ visibility: 'hidden' }}>{children}</div>}
      </ToastProvider>
    </ThemeProvider>
  );
}
'use client';

import { usePathname } from 'next/navigation';
import { Navbar } from '@/components/layout/navbar';
import { Footer } from '@/components/layout/footer';
import React from 'react';

export function ConditionalLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isEmbedRoute = pathname.startsWith('/ai-demo/embed') || pathname.startsWith('/publisher-demo/embed');
  const showMainLayout = !pathname.startsWith('/investor/view/') && !isEmbedRoute;

  return (
    <div className="relative flex min-h-screen flex-col">
      {showMainLayout && <Navbar />}
      <main className="flex-1">{children}</main>
      {showMainLayout && <Footer />}
    </div>
  );
}

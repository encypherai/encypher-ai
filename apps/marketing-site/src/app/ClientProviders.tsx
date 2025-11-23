"use client";
import { ToastProvider } from "@/components/ui/use-toast";
import { SessionProvider } from "@/components/SessionProvider";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const queryClient = new QueryClient();

export function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <ToastProvider>{children}</ToastProvider>
      </SessionProvider>
    </QueryClientProvider>
  );
}

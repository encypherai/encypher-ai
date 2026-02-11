'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import InspectTool from '@/components/admin/InspectTool';
import {
  BeakerIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

export default function AdminToolsPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!user?.is_superuser) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <ShieldCheckIcon className="mx-auto h-12 w-12 text-red-400" />
          <h3 className="mt-2 text-lg font-medium text-red-800 dark:text-red-200">
            Access Denied
          </h3>
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            Admin tools are only available to superusers.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <BeakerIcon className="h-7 w-7 text-indigo-500" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Admin Tools
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Experimental tools for inspecting and debugging Encypher embeddings.
          </p>
        </div>
        <span className="ml-auto badge badge-warning text-[10px] uppercase tracking-wider">
          Superuser Only
        </span>
      </div>

      <InspectTool />
    </div>
  );
}

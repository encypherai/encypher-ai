'use client';

import React, { ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Loader2 } from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { Separator } from '@/components/ui/separator';

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  // Check if user is authenticated and has admin role
  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-lg">Loading admin panel...</span>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (status === 'unauthenticated') {
    router.push('/auth/signin?callbackUrl=/admin');
    return null;
  }

  // Check if user has admin role
  const isAdmin = session?.user?.role === 'admin' || session?.user?.email?.endsWith('@encypher.com');

  if (!isAdmin) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6 text-center">
          You don't have permission to access the admin panel.
        </p>
        <Button asChild>
          <Link href="/">Return to Home</Link>
        </Button>
      </div>
    );
  }

  // Navigation items
  const navItems = [
    { name: 'Dashboard', href: '/admin' },
    { name: 'Investor Requests', href: '/admin/investor-requests' },
    { name: 'Users', href: '/admin/users' },
    { name: 'Settings', href: '/admin/settings' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow pt-5 overflow-y-auto bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="flex items-center flex-shrink-0 px-4">
            <Link href="/admin" className="text-xl font-bold text-gray-900 dark:text-white">
              Encypher Admin
            </Link>
          </div>
          <div className="mt-5 flex-1 flex flex-col">
            <nav className="flex-1 px-2 pb-4 space-y-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-gray-100 dark:bg-gray-700 text-primary'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {session?.user?.name || 'Admin User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {session?.user?.email || 'admin@example.com'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <Link href="/admin" className="text-xl font-bold text-gray-900 dark:text-white">
          Encypher Admin
        </Link>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              <span className="sr-only">Open menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <SheetHeader>
              <SheetTitle>Encypher Admin</SheetTitle>
            </SheetHeader>
            <Separator className="my-4" />
            <nav className="flex flex-col space-y-4">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`px-2 py-2 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-gray-100 dark:bg-gray-700 text-primary'
                        : 'text-gray-600 dark:text-gray-300'
                    }`}
                  >
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </SheetContent>
        </Sheet>
      </div>

      {/* Main Content */}
      <div className="flex flex-col flex-1">
        <main className="flex-1 p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

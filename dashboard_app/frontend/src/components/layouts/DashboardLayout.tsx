'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/lib/auth';
import { useTheme } from '@/lib/theme';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { User } from '@/types/user';

// Icons - we need to install heroicons
import { 
  HomeIcon, 
  ChartBarIcon, 
  DocumentTextIcon, 
  CogIcon, 
  UserIcon,
  BeakerIcon,
  ArrowLeftOnRectangleIcon as LogoutIcon,
  Bars3Icon as MenuIcon,
  XMarkIcon as XIcon
} from '@heroicons/react/24/outline';

interface NavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

const NavItem: React.FC<NavItemProps> = ({ href, icon, label, active, onClick }) => (
  <Link 
    href={href}
    className={`flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors ${
      active 
        ? 'bg-primary-700 text-white' 
        : 'text-gray-300 hover:bg-primary-700/50 hover:text-white'
    }`}
    onClick={onClick}
  >
    <div className="mr-3 h-5 w-5">{icon}</div>
    {label}
  </Link>
);

interface DashboardLayoutProps {
  children: React.ReactNode;
  currentPath: string;
}

export default function DashboardLayout({ children, currentPath }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: <HomeIcon className="h-5 w-5" /> },
    { name: 'Reports', href: '/dashboard/reports', icon: <ChartBarIcon className="h-5 w-5" /> },
    { name: 'Signing', href: '/dashboard/signing', icon: <DocumentTextIcon className="h-5 w-5" /> },
    { name: 'Scanning', href: '/dashboard/signing/scan', icon: <DocumentTextIcon className="h-5 w-5" /> },
    { name: 'Demo', href: '/dashboard/demo', icon: <DocumentTextIcon className="h-5 w-5" /> },
    { name: 'Audit Logs', href: '/dashboard/audit-logs', icon: <DocumentTextIcon className="h-5 w-5" /> },
    { name: 'Settings', href: '/dashboard/settings', icon: <CogIcon className="h-5 w-5" /> },
    { name: 'Profile', href: '/dashboard/profile', icon: <UserIcon className="h-5 w-5" /> },
    // TEAM_166: Admin tools — superuser only, rendered conditionally below
    ...(user?.is_superuser
      ? [{ name: 'Admin Tools', href: '/dashboard/admin/tools', icon: <BeakerIcon className="h-5 w-5" /> }]
      : []),
  ];

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100 dark:bg-gray-900">
      {/* Mobile sidebar */}
      <div 
        className={`fixed inset-0 flex z-40 md:hidden ${sidebarOpen ? 'block' : 'hidden'}`}
        onClick={() => setSidebarOpen(false)}
      >
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" aria-hidden="true"></div>
        
        <div className="relative flex-1 flex flex-col max-w-xs w-full pt-5 pb-4 bg-primary-800 dark:bg-gray-800">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              type="button"
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sr-only">Close sidebar</span>
              <XIcon className="h-6 w-6 text-white" aria-hidden="true" />
            </button>
          </div>
          
          <div className="flex-shrink-0 flex items-center px-4">
            <Image
              src="/horizontal-logo-nobg.png"
              alt="Encypher Logo"
              width={180}
              height={40}
              className="h-8 w-auto"
            />
          </div>
          
          <div className="mt-5 flex-1 h-0 overflow-y-auto">
            <nav className="px-2 space-y-1">
              {navigation.map((item) => (
                <NavItem
                  key={item.name}
                  href={item.href}
                  icon={item.icon}
                  label={item.name}
                  active={currentPath === item.href}
                  onClick={() => setSidebarOpen(false)}
                />
              ))}
              
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-300 rounded-md hover:bg-primary-700/50 hover:text-white transition-colors"
              >
                <LogoutIcon className="mr-3 h-5 w-5" />
                Logout
              </button>
            </nav>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-primary-800 dark:bg-gray-800">
            <div className="flex items-center h-16 flex-shrink-0 px-4 bg-primary-900 dark:bg-gray-900">
              <Image
                src="/horizontal-logo-nobg.png"
                alt="Encypher Logo"
                width={180}
                height={40}
                className="h-8 w-auto"
              />
            </div>
            
            <div className="flex-1 flex flex-col overflow-y-auto">
              <nav className="flex-1 px-2 py-4 space-y-1">
                {navigation.map((item) => (
                  <NavItem
                    key={item.name}
                    href={item.href}
                    icon={item.icon}
                    label={item.name}
                    active={currentPath === item.href}
                  />
                ))}
                
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center px-4 py-3 text-sm font-medium text-gray-300 rounded-md hover:bg-primary-700/50 hover:text-white transition-colors"
                >
                  <LogoutIcon className="mr-3 h-5 w-5" />
                  Logout
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="relative z-10 flex-shrink-0 flex h-16 bg-white dark:bg-gray-800 shadow">
          <button
            type="button"
            className="px-4 border-r border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <MenuIcon className="h-6 w-6" aria-hidden="true" />
          </button>
          
          <div className="flex-1 px-4 flex justify-between">
            <div className="flex-1 flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                {navigation.find(item => item.href === currentPath)?.name || 'Dashboard'}
              </h1>
            </div>
            
            <div className="ml-4 flex items-center md:ml-6">
              <ThemeToggle className="mr-4" />
              <div className="flex items-center">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 mr-2">
                  {user?.full_name || user?.email}
                </span>
                <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white">
                  {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        </div>

        <main className="flex-1 relative overflow-y-auto focus:outline-none p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

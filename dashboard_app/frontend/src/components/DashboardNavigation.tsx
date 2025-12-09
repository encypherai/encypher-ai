'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import {
  HomeIcon,
  ClipboardDocumentListIcon,
  ShieldCheckIcon,
  CommandLineIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon,
  DocumentCheckIcon,
  UsersIcon
} from '@heroicons/react/24/outline';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  children?: NavItem[];
}

export default function DashboardNavigation() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});
  
  const navigation: NavItem[] = [
    { name: 'Dashboard', href: '/dashboard/overview', icon: HomeIcon },
    { name: 'Coalition', href: '/dashboard/coalition', icon: UsersIcon },
    {
      name: 'Audit Logs',
      href: '/dashboard/audit-logs',
      icon: ClipboardDocumentListIcon,
    },
    { 
      name: 'Policy Validation', 
      href: '/dashboard/policy-validation', 
      icon: ShieldCheckIcon,
      children: [
        { name: 'Validation Results', href: '/dashboard/policy-validation', icon: ClipboardDocumentListIcon },
        { name: 'Policy Schemas', href: '/dashboard/policy-validation/schemas', icon: ShieldCheckIcon },
        { name: 'Create Schema', href: '/dashboard/policy-validation/schemas/new', icon: ShieldCheckIcon },
      ]
    },
    { name: 'Directory Signing', href: '/dashboard/signing', icon: DocumentCheckIcon },
    { name: 'CLI Integration', href: '/dashboard/cli-integration', icon: CommandLineIcon },
    { name: 'Profile', href: '/dashboard/profile', icon: UserIcon },
    { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
  ];
  
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  const toggleExpandItem = (name: string) => {
    setExpandedItems(prev => ({
      ...prev,
      [name]: !prev[name]
    }));
  };
  
  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === href;
    }
    return pathname.startsWith(href);
  };
  
  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    logout();
    window.location.href = '/login';
  };
  
  return (
    <>
      {/* Mobile menu button */}
      <div className="md:hidden flex items-center px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <button
          type="button"
          className="text-gray-500 hover:text-gray-600 dark:text-gray-400 dark:hover:text-gray-300"
          onClick={toggleMobileMenu}
        >
          <span className="sr-only">Open sidebar</span>
          {isMobileMenuOpen ? (
            <XMarkIcon className="h-6 w-6" aria-hidden="true" />
          ) : (
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          )}
        </button>
        <div className="ml-4 flex-1 flex justify-between items-center">
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Encypher Dashboard</h1>
          </div>
          {user && (
            <div className="flex items-center">
              <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">{user.name || user.email}</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Mobile menu, show/hide based on state */}
      <div className={`md:hidden ${isMobileMenuOpen ? 'block' : 'hidden'} bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700`}>
        <nav className="px-2 py-4 space-y-1">
          {navigation.map((item) => (
            <div key={item.name}>
              {item.children ? (
                <div>
                  <button
                    onClick={() => toggleExpandItem(item.name)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                      isActive(item.href)
                        ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                    }`}
                  >
                    <item.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                    <span className="flex-1">{item.name}</span>
                    <ChevronDownIcon
                      className={`ml-3 h-4 w-4 transition-transform ${
                        expandedItems[item.name] ? 'transform rotate-180' : ''
                      }`}
                    />
                  </button>
                  
                  {expandedItems[item.name] && (
                    <div className="ml-8 mt-1 space-y-1">
                      {item.children.map((child) => (
                        <Link
                          key={child.name}
                          href={child.href}
                          className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                            isActive(child.href)
                              ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                              : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                          }`}
                        >
                          <child.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                          {child.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <Link
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                  {item.name}
                </Link>
              )}
            </div>
          ))}
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
            Logout
          </button>
        </nav>
      </div>
      
      {/* Desktop sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">Encypher Dashboard</h1>
            </div>
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navigation.map((item) => (
                <div key={item.name}>
                  {item.children ? (
                    <div className="space-y-1">
                      <button
                        onClick={() => toggleExpandItem(item.name)}
                        className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                          isActive(item.href)
                            ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                            : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                        }`}
                      >
                        <item.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                        <span className="flex-1">{item.name}</span>
                        <ChevronDownIcon
                          className={`ml-3 h-4 w-4 transition-transform ${
                            expandedItems[item.name] ? 'transform rotate-180' : ''
                          }`}
                        />
                      </button>
                      
                      {expandedItems[item.name] && (
                        <div className="ml-8 space-y-1">
                          {item.children.map((child) => (
                            <Link
                              key={child.name}
                              href={child.href}
                              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                                isActive(child.href)
                                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                              }`}
                            >
                              <child.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                              {child.name}
                            </Link>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <Link
                      href={item.href}
                      className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                        isActive(item.href)
                          ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                      }`}
                    >
                      <item.icon className="mr-3 h-5 w-5 flex-shrink-0" aria-hidden="true" />
                      {item.name}
                    </Link>
                  )}
                </div>
              ))}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex-shrink-0 w-full group block">
              <div className="flex items-center">
                <div>
                  <UserIcon className="inline-block h-9 w-9 rounded-full text-gray-500 dark:text-gray-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {user?.name || user?.email || 'User'}
                  </p>
                  <button
                    onClick={handleLogout}
                    className="text-xs font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

'use client';

import { useSession, signOut } from 'next-auth/react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode, useState } from 'react';
import { OrganizationSwitcher } from '../OrganizationSwitcher';
import { MobileNav } from '../MobileNav';
import { NotificationCenter } from '../NotificationCenter';
import { ThemeToggleButton } from '../../contexts/ThemeContext';

interface DashboardLayoutProps {
  children: ReactNode;
}

const navItems = [
  { href: '/', label: 'Overview' },
  { href: '/api-keys', label: 'API Keys' },
  { href: '/playground', label: 'Playground' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/webhooks', label: 'Webhooks', businessOnly: true },
  { href: '/team', label: 'Team', businessOnly: true },
  { href: '/settings', label: 'Settings' },
  { href: '/billing', label: 'Billing' },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { data: session } = useSession();
  const pathname = usePathname();
  const isAdmin = ((session?.user as any)?.role ?? '').toLowerCase() === 'admin';
  const userTier = (session?.user as any)?.tier || 'starter';
  const hasTeamFeature = ['business', 'enterprise'].includes(userTier);
  const userName = session?.user?.name || session?.user?.email || 'User';
  const userInitial = userName.charAt(0).toUpperCase();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
    
  // Filter nav items based on tier
  const visibleNavItems = navItems.filter(item => !item.businessOnly || hasTeamFeature);

  const handleSignOut = () => {
    signOut({ callbackUrl: process.env.NEXT_PUBLIC_SITE_URL || 'https://s-www.encypherai.com' });
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header - Clean, minimal design matching marketing site */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
              aria-label="Open menu"
            >
              <svg className="w-6 h-6 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Logo + Dashboard Badge + Org Switcher */}
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center">
                {/* Light mode logo */}
                <Image
                  src="/assets/encypher_full_logo_color.svg"
                  alt="Encypher"
                  width={140}
                  height={36}
                  className="h-8 w-auto dark:hidden"
                  priority
                />
                {/* Dark mode logo */}
                <Image
                  src="/assets/encypher_full_logo_white.svg"
                  alt="Encypher"
                  width={140}
                  height={36}
                  className="h-8 w-auto hidden dark:block"
                  priority
                />
              </Link>
              <div className="hidden sm:block">
                <span className="px-2.5 py-1 text-xs font-semibold bg-delft-blue text-white rounded-md">
                  Dashboard
                </span>
              </div>
              {/* Organization Switcher - only shows if user has multiple orgs */}
              {hasTeamFeature && (
                <div className="hidden md:block">
                  <OrganizationSwitcher />
                </div>
              )}
            </div>

            {/* Center Navigation */}
            <nav className="hidden lg:flex items-center gap-1">
              {visibleNavItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link 
                    key={item.href} 
                    href={item.href}
                    className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 ${
                      isActive 
                        ? 'text-blue-ncs bg-blue-ncs/10' 
                        : 'text-slate-600 dark:text-slate-300 hover:text-delft-blue dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
              {isAdmin && (
                <Link 
                  href="/admin"
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 ${
                    pathname === '/admin' 
                      ? 'text-blue-ncs bg-blue-ncs/10' 
                      : 'text-slate-600 dark:text-slate-300 hover:text-delft-blue dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700'
                  }`}
                >
                  Admin
                </Link>
              )}
            </nav>

            {/* Right Side - Theme + Notifications + Docs + User */}
            <div className="flex items-center gap-2">
              {/* Theme Toggle */}
              <div className="hidden sm:block">
                <ThemeToggleButton />
              </div>

              {/* Notifications */}
              <NotificationCenter />

              {/* Docs Link */}
              <a
                href="https://docs.encypherai.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-delft-blue dark:hover:text-white transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Docs
              </a>
              
              {/* User Menu */}
              <div className="relative">
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-ncs to-delft-blue rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {userInitial}
                  </div>
                  <svg className={`w-4 h-4 text-slate-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {/* Dropdown */}
                {isDropdownOpen && (
                  <>
                    <div 
                      className="fixed inset-0 z-40" 
                      onClick={() => setIsDropdownOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 z-50 overflow-hidden">
                      <div className="p-4 bg-gradient-to-br from-slate-50 to-white dark:from-slate-700 dark:to-slate-800 border-b border-slate-100 dark:border-slate-700">
                        <p className="font-semibold text-sm text-delft-blue dark:text-white truncate">{userName}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">{session?.user?.email}</p>
                      </div>
                      <div className="p-2">
                        <Link 
                          href="/settings"
                          onClick={() => setIsDropdownOpen(false)}
                          className="flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                        >
                          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          Settings
                        </Link>
                        <Link 
                          href="/billing"
                          onClick={() => setIsDropdownOpen(false)}
                          className="flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
                        >
                          <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                          </svg>
                          Billing
                        </Link>
                        <div className="border-t border-slate-100 dark:border-slate-700 mt-2 pt-2">
                          <button
                            onClick={handleSignOut}
                            className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                            </svg>
                            Sign out
                          </button>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Mobile Navigation */}
      <MobileNav
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        navItems={visibleNavItems}
        isAdmin={isAdmin}
        userName={userName}
        userEmail={session?.user?.email || ''}
        userInitial={userInitial}
      />
    </div>
  );
}

export default DashboardLayout;

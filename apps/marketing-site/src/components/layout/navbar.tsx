"use client";

import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MenuIcon } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useState, useEffect } from 'react';
import { toolLinks } from '@/config/tools';

export function Navbar() {
  const { setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // After mounting, we can show the theme toggle
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center">
            <Image 
              src="/encypher_full_nobg.png" 
              alt="Encypher Logo" 
              width={160} 
              height={40}
              className="h-10 w-auto"
              priority
              quality={90}
            />
          </Link>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-4">
          {/* Solutions Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="text-sm font-medium hover:text-primary px-2">
                Solutions
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="bg-background !bg-opacity-100 !backdrop-blur-none !bg-neutral-900 !shadow-lg">
              <DropdownMenuItem asChild>
                <Link href="/solutions/ai-companies">For AI Companies</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/solutions/publishers">For Publishers</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/solutions/enterprises">For Enterprises</Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {/* Tools Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="text-sm font-medium hover:text-primary px-2">
                Tools
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="bg-background !bg-opacity-100 !backdrop-blur-none !bg-neutral-900 !shadow-lg">
              {toolLinks.filter(t => !t.hiddenInMenu).map(t => (
                <DropdownMenuItem key={t.href} asChild>
                  <Link href={t.href}>{t.name}</Link>
                </DropdownMenuItem>
              ))}
              <DropdownMenuItem asChild>
                <Link href="/tools">All Tools</Link>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Link href="/blog" className="text-sm font-medium hover:text-primary">
            Blog
          </Link>
          <Link href="/licensing" className="text-sm font-medium hover:text-primary">
            Pricing
          </Link>
          <Link href="/company" className="text-sm font-medium hover:text-primary">
            Company
          </Link>
          {/* Platform link disabled for publisher demo branch */}
          {/* <Link href="/platform" className="text-sm font-medium hover:text-primary">
            Platform
          </Link> */}
          {/* Auth Buttons - Disabled for publisher demo branch */}
          {/* {status === "loading" ? null : session ? (
            <>
              <Button
                asChild
                variant="secondary"
                size="sm"
                className="mr-2"
              >
                <Link href="/dashboard">Dashboard</Link>
              </Button>
              <Button variant="outline" size="sm" onClick={() => signOut({ callbackUrl: "/" })}>Sign out</Button>
            </>
          ) : (
            <div className="flex gap-2">
              <Button asChild variant="outline" size="sm">
                <Link href="/auth/register">Sign Up</Link>
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/auth/register?mode=signin">Sign In</Link>
              </Button>
            </div>
          )} */}
        </nav>
        
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              {/* <Button variant="outline" size="icon" className="h-9 w-9">
                {theme === 'dark' ? <SunIcon className="h-4 w-4" /> : <MoonIcon className="h-4 w-4" />}
                <span className="sr-only">Toggle theme</span>
              </Button> */}
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setTheme('light')}>
                Light
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('dark')}>
                Dark
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme('system')}>
                System
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          
          {/* Mobile Menu Button */}
          <Button 
            variant="outline" 
            size="icon" 
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <MenuIcon className="h-5 w-5" />
            <span className="sr-only">Toggle menu</span>
          </Button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden p-4 border-t border-border/40 bg-background">
          <nav className="flex flex-col space-y-4">
            {/* Platform link disabled for publisher demo branch */}
            {/* <Link 
              href="/platform" 
              className="text-sm font-medium hover:text-primary"
              onClick={() => setMobileMenuOpen(false)}
            >
              Platform
            </Link> */}
            {/* Mobile Solutions Links */}
            <span className="text-sm font-medium">Solutions</span>
            <Link 
              href="/solutions/ai-companies" 
              className="text-sm font-medium hover:text-primary pl-4"
              onClick={() => setMobileMenuOpen(false)}
            >
              For AI Companies
            </Link>
            <Link 
              href="/solutions/publishers" 
              className="text-sm font-medium hover:text-primary pl-4"
              onClick={() => setMobileMenuOpen(false)}
            >
              For Publishers
            </Link>
            <Link 
              href="/solutions/enterprises" 
              className="text-sm font-medium hover:text-primary pl-4"
              onClick={() => setMobileMenuOpen(false)}
            >
              For Enterprises
            </Link>
            {/* Mobile Tools Links */}
            <span className="text-sm font-medium">Tools</span>
            {toolLinks.filter(t => !t.hiddenInMenu).map(t => (
              <Link
                key={t.href}
                href={t.href}
                className="text-sm font-medium hover:text-primary pl-4"
                onClick={() => setMobileMenuOpen(false)}
              >
                {t.name}
              </Link>
            ))}
            <Link 
              href="/tools" 
              className="text-sm font-medium hover:text-primary pl-4"
              onClick={() => setMobileMenuOpen(false)}
            >
              All Tools
            </Link>
            <Link 
              href="/blog" 
              className="text-sm font-medium hover:text-primary"
              onClick={() => setMobileMenuOpen(false)}
            >
              Blog
            </Link>
            <Link 
              href="/licensing" 
              className="text-sm font-medium hover:text-primary"
              onClick={() => setMobileMenuOpen(false)}
            >
              Pricing
            </Link>
            <Link 
              href="/company" 
              className="text-sm font-medium hover:text-primary"
              onClick={() => setMobileMenuOpen(false)}
            >
              Company
            </Link>
            
            {/* Auth Buttons for Mobile - Disabled for publisher demo branch */}
            {/* {status === "loading" ? null : session ? (
              <>
                <Button
                  asChild
                  variant="secondary"
                  size="sm"
                  className="w-full"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link href="/dashboard">Dashboard</Link>
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => { setMobileMenuOpen(false); signOut({ callbackUrl: "/" }); }}
                >
                  Sign out
                </Button>
              </>
            ) : (
              <div className="flex flex-col space-y-2 pt-2">
                <Link 
                  href="/auth/register?mode=signin" 
                  className="block w-full text-left px-4 py-2 text-sm font-medium hover:text-primary"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Link 
                  href="/auth/register" 
                  className="block w-full text-left px-4 py-2 text-sm font-medium hover:text-primary"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </div>
            )} */}
          </nav>
        </div>
      )}
    </header>
  );
}
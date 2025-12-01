"use client";

import Link from 'next/link';
import Image from 'next/image';
import { showCookiePreferences } from '@/components/CookieConsent';

export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-2 md:grid-cols-7 gap-8">
          <div className="space-y-3">
            <Link href="/">
              <Image
                src="/encypher_full_nobg.png"
                alt="Encypher Logo"
                width={180}
                height={30}
                className="h-7 w-auto"
              />
            </Link>
            <p className="text-sm text-muted-foreground">
              Content Intelligence Infrastructure
            </p>
          </div>

          {/* SOLUTIONS */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Solutions</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/solutions/publishers" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  For Publishers
                </Link>
              </li>
              <li>
                <Link href="/solutions/ai-companies" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  For AI Labs
                </Link>
              </li>
              <li>
                <Link href="/solutions/enterprises" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  For Enterprises
                </Link>
              </li>
            </ul>
          </div>

          {/* RESOURCES */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/blog" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <a href="https://github.com/encypherai/encypher-ai" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  GitHub
                </a>
              </li>
              <li>
                <a href="https://docs.encypherai.com" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* COMPANY */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Company</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/company" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/company#contact" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* LEGAL */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/privacy" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Terms
                </Link>
              </li>
              <li>
                <a href="https://github.com/encypherai/encypher-ai/tree/main?tab=License-1-ov-file#readme" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Licence (AGPL-3.0)
                </a>
              </li>
              <li>
                <button 
                  onClick={showCookiePreferences}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors text-left"
                >
                  Cookie Settings
                </button>
              </li>
            </ul>
          </div>

          {/* STANDARDS */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Standards</h3>
            <ul className="space-y-2">
              <li>
                <a href="https://c2pa.org" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  C2PA
                </a>
              </li>
              <li>
                <a href="https://contentauthenticity.org" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  CAI
                </a>
              </li>
            </ul>
          </div>

          {/* CONNECT */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Connect</h3>
            <ul className="space-y-2">
              <li>
                <a href="https://www.linkedin.com/company/encypher/" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  LinkedIn
                </a>
              </li>
              <li>
                <a href="https://x.com/EncypherAI" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Twitter
                </a>
              </li>
              <li>
                <a href="https://github.com/encypherai/encypher-ai" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  GitHub
                </a>
              </li>
              <li>
                <a href="mailto:contact@encypherai.com?subject=Encypher%20Inquiry" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Email
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 pb-4">
            <p className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} Encypher Corporation. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <a href="https://github.com/encypherai/encypher-ai" target="_blank" className="flex items-center">
                <Image 
                  src="https://img.shields.io/github/stars/encypherai/encypher-ai?style=for-the-badge&logo=github" 
                  alt="GitHub Stars" 
                  width={120} 
                  height={28}
                  unoptimized
                />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
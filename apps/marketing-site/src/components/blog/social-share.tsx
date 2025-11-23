'use client';

import { useState } from 'react';
import { 
  Twitter, 
  Facebook, 
  Linkedin, 
  Mail, 
  Link as LinkIcon,
  Check
} from 'lucide-react';
import { getSiteUrl } from '@/lib/env';

interface SocialShareProps {
  url: string;
  title: string;
  description?: string;
  className?: string;
}

export function SocialShare({ url, title, description, className = '' }: SocialShareProps) {
  const [copied, setCopied] = useState(false);
  
  // Ensure we have the full URL
  const baseUrl = getSiteUrl();
  const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
  
  // Prepare share URLs
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(fullUrl)}`;
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`;
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`;
  const mailUrl = `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${description || title}\n\n${fullUrl}`)}`;
  
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <a 
        href={twitterUrl} 
        target="_blank" 
        rel="noopener noreferrer"
        className="p-2 rounded-full bg-muted hover:bg-muted/80 transition-colors"
        aria-label="Share on Twitter"
      >
        <Twitter className="w-4 h-4" />
      </a>
      <a 
        href={facebookUrl} 
        target="_blank" 
        rel="noopener noreferrer"
        className="p-2 rounded-full bg-muted hover:bg-muted/80 transition-colors"
        aria-label="Share on Facebook"
      >
        <Facebook className="w-4 h-4" />
      </a>
      <a 
        href={linkedinUrl} 
        target="_blank" 
        rel="noopener noreferrer"
        className="p-2 rounded-full bg-muted hover:bg-muted/80 transition-colors"
        aria-label="Share on LinkedIn"
      >
        <Linkedin className="w-4 h-4" />
      </a>
      <a 
        href={mailUrl}
        className="p-2 rounded-full bg-muted hover:bg-muted/80 transition-colors"
        aria-label="Share via Email"
      >
        <Mail className="w-4 h-4" />
      </a>
      <button
        onClick={copyToClipboard}
        className="p-2 rounded-full bg-muted hover:bg-muted/80 transition-colors relative"
        aria-label="Copy link to clipboard"
      >
        {copied ? <Check className="w-4 h-4 text-green-500" /> : <LinkIcon className="w-4 h-4" />}
        {copied && (
          <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-xs bg-background border border-border px-2 py-1 rounded shadow-sm whitespace-nowrap">
            Copied!
          </span>
        )}
      </button>
    </div>
  );
}

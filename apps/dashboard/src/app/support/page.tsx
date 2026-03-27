'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Input } from '@encypher/design-system';
import { useSession } from 'next-auth/react';
import { ReactNode, useState } from 'react';
import { toast } from 'sonner';

import apiClient from '@/lib/api';

import { DashboardLayout } from '../../components/layout/DashboardLayout';

function IconApi({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  );
}

function IconTerminal({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}

function IconPackage({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
    </svg>
  );
}

function IconStatus({ className = 'w-5 h-5' }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

const CATEGORY_OPTIONS = [
  { value: 'general', label: 'General' },
  { value: 'technical', label: 'Technical' },
  { value: 'billing', label: 'Billing' },
  { value: 'security', label: 'Security' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'feature_request', label: 'Feature Request' },
];

export default function SupportPage() {
  const { data: session } = useSession();
  const accessToken = (session?.user as Record<string, unknown>)?.accessToken as string | undefined;

  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [category, setCategory] = useState('general');
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    if (!accessToken) {
      toast.error('You must be signed in to submit a support request.');
      return;
    }

    setSending(true);
    try {
      await apiClient.submitSupportTicket(accessToken, {
        subject: subject.trim(),
        message: message.trim(),
        category,
      });
      toast.success('Message sent! We will get back to you within 24 hours.');
      setSubject('');
      setMessage('');
      setCategory('general');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to send message. Please try again.';
      toast.error(msg);
    } finally {
      setSending(false);
    }
  };

  const faqs = [
    {
      question: 'How do I get started with Encypher?',
      answer: 'Sign up for a free account, generate your first API key, and follow our quickstart guide in the documentation.',
    },
    {
      question: 'What is the difference between signing and verifying?',
      answer: 'Signing adds a cryptographic signature to your content, while verifying checks if a signature is valid and authentic.',
    },
    {
      question: 'How many API calls can I make?',
      answer: 'It depends on your plan. The free tier includes 1,000 signatures per month, while paid plans offer higher limits.',
    },
    {
      question: 'Can I upgrade or downgrade my plan?',
      answer: 'Yes, you can change your plan at any time from the Billing page. Changes take effect immediately.',
    },
    {
      question: 'Is my data secure?',
      answer: 'Yes, we use industry-standard encryption and security practices to protect your data and API keys.',
    },
  ];

  const resources: { title: string; description: string; icon: ReactNode; iconBg: string; link: string }[] = [
    { title: 'API Documentation', description: 'Interactive API reference with Swagger UI', icon: <IconApi className="w-5 h-5" />, iconBg: 'bg-gradient-to-br from-[#1B2F50] to-[#2A87C4]', link: 'https://api.encypher.com/docs' },
    { title: 'Python SDK', description: 'Official Python client library', icon: <IconTerminal className="w-5 h-5" />, iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#1B2F50]', link: 'https://pypi.org/project/encypher/' },
    { title: 'TypeScript SDK', description: 'Official TypeScript/Node.js client', icon: <IconPackage className="w-5 h-5" />, iconBg: 'bg-gradient-to-br from-[#00CED1] to-[#2A87C4]', link: 'https://www.npmjs.com/package/@encypher/sdk' },
    { title: 'Status Page', description: 'Check system uptime and health', icon: <IconStatus className="w-5 h-5" />, iconBg: 'bg-gradient-to-br from-[#2A87C4] to-[#00CED1]', link: 'https://verify.encypher.com/status' },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Support</h1>
          <p className="text-sm text-muted-foreground mt-1">Get help with Encypher and find answers to common questions.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Contact Support</CardTitle>
              <CardDescription>Send us a message and we will get back to you within 24 hours</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Category</label>
                  <select
                    className="w-full px-3 py-2 bg-background text-foreground border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-columbia-blue"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    {CATEGORY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Subject</label>
                  <Input
                    placeholder="Brief description of your issue"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Message</label>
                  <textarea
                    className="w-full min-h-[150px] px-3 py-2 bg-background text-foreground border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-columbia-blue"
                    placeholder="Describe your issue in detail..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                  />
                </div>
                <Button type="submit" variant="primary" fullWidth disabled={sending}>
                  {sending ? 'Sending...' : 'Send Message'}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Links</CardTitle>
              <CardDescription>Helpful resources and documentation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {resources.map((resource, idx) => (
                  <a
                    key={idx}
                    href={resource.link}
                    className="p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className={`w-9 h-9 ${resource.iconBg} rounded-lg flex items-center justify-center text-white mb-3`}>{resource.icon}</div>
                    <div className="font-medium text-sm mb-1">{resource.title}</div>
                    <div className="text-xs text-muted-foreground">{resource.description}</div>
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
            <CardDescription>Find answers to common questions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {faqs.map((faq, idx) => (
                <details key={idx} className="group">
                  <summary className="flex items-center justify-between p-4 border border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                    <span className="font-medium">{faq.question}</span>
                    <svg className="w-5 h-5 text-muted-foreground group-open:rotate-180 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </summary>
                  <div className="p-4 text-muted-foreground">
                    {faq.answer}
                  </div>
                </details>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

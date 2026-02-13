'use client';

import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent, Input } from '@encypher/design-system';
import { useState } from 'react';
import { toast } from 'sonner';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

export default function SupportPage() {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !message.trim()) {
      toast.error('Please fill in all fields');
      return;
    }
    
    setSending(true);
    // Simulate sending - in production this would call an API
    await new Promise(resolve => setTimeout(resolve, 1000));
    toast.success('Message sent! We\'ll get back to you within 24 hours.');
    setSubject('');
    setMessage('');
    setSending(false);
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

  const resources = [
    { title: 'API Documentation', description: 'Interactive API reference with Swagger UI', icon: '📚', link: 'https://api.encypherai.com/docs' },
    { title: 'Python SDK', description: 'Official Python client library', icon: '🐍', link: 'https://pypi.org/project/encypher/' },
    { title: 'TypeScript SDK', description: 'Official TypeScript/Node.js client', icon: '📦', link: 'https://www.npmjs.com/package/@encypher/sdk' },
    { title: 'Status Page', description: 'Check system status', icon: '🟢', link: 'https://verify.encypherai.com/status' },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-delft-blue dark:text-white mb-2">Support & Help</h2>
          <p className="text-muted-foreground">Get help with Encypher and find answers to common questions</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Contact Support</CardTitle>
              <CardDescription>Send us a message and we'll get back to you within 24 hours</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
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
                    className="w-full min-h-[150px] px-3 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-columbia-blue"
                    placeholder="Describe your issue in detail..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                  />
                </div>
                <Button variant="primary" fullWidth>Send Message</Button>
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
                    <div className="text-2xl mb-2">{resource.icon}</div>
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


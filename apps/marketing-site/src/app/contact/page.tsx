'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Mail, MessageSquare, Github, CheckCircle, Loader2, Building2, Clock } from 'lucide-react';

type ContactContext = 'general' | 'publisher' | 'ai' | 'enterprise';

const contextOptions: { value: ContactContext; label: string; description: string }[] = [
  { value: 'general', label: 'General Inquiry', description: 'Questions about Encypher' },
  { value: 'publisher', label: 'Publisher', description: 'Content protection & licensing' },
  { value: 'ai', label: 'AI Lab', description: 'Performance intelligence & compliance' },
  { value: 'enterprise', label: 'Enterprise', description: 'Custom implementation & SLA' },
];

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    role: '',
    context: 'general' as ContactContext,
    message: '',
    consent: false,
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMessage('');

    try {
      const response = await fetch('/api/demo-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          source: 'contact-page',
        }),
      });
      if (!response.ok) throw new Error('Failed to submit');
      setStatus('success');
    } catch {
      setStatus('error');
      setErrorMessage('Failed to submit. Please try again or email sales@encypherai.com');
    }
  };

  return (
    <div className="container py-12 md:py-20">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">Get in Touch</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Whether you&apos;re a publisher, AI lab, or enterprise — we&apos;d love to hear from you.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Contact Form — 2 columns */}
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="pt-6">
                {status === 'success' ? (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">Message Received!</h2>
                    <p className="text-muted-foreground mb-2">
                      Thank you for reaching out. We&apos;ll get back to you within 24 hours.
                    </p>
                    <p className="text-sm text-muted-foreground mb-8">
                      A confirmation has been sent to {formData.email}.
                    </p>
                    <Button onClick={() => setStatus('idle')}>Send Another Message</Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Context selector */}
                    <div className="space-y-2">
                      <Label>I&apos;m reaching out as a...</Label>
                      <div className="grid grid-cols-2 gap-2">
                        {contextOptions.map((opt) => (
                          <button
                            key={opt.value}
                            type="button"
                            onClick={() => setFormData(prev => ({ ...prev, context: opt.value }))}
                            className={`p-3 rounded-lg border text-left transition-all ${
                              formData.context === opt.value
                                ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                                : 'border-border hover:border-primary/40'
                            }`}
                          >
                            <p className="font-medium text-sm">{opt.label}</p>
                            <p className="text-xs text-muted-foreground">{opt.description}</p>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Full Name *</Label>
                        <Input
                          id="name"
                          name="name"
                          required
                          value={formData.name}
                          onChange={handleChange}
                          placeholder="Jane Smith"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email">Work Email *</Label>
                        <Input
                          type="email"
                          id="email"
                          name="email"
                          required
                          value={formData.email}
                          onChange={handleChange}
                          placeholder="jane@company.com"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="organization">Organization</Label>
                        <Input
                          id="organization"
                          name="organization"
                          value={formData.organization}
                          onChange={handleChange}
                          placeholder="Your company"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="role">Job Title</Label>
                        <Input
                          id="role"
                          name="role"
                          value={formData.role}
                          onChange={handleChange}
                          placeholder="VP of Engineering"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="message">How can we help? *</Label>
                      <Textarea
                        id="message"
                        name="message"
                        required
                        rows={5}
                        maxLength={1000}
                        value={formData.message}
                        onChange={handleChange}
                        placeholder="Tell us about your needs, questions, or how you'd like to work together..."
                      />
                      <p className="text-xs text-muted-foreground text-right">{formData.message.length}/1000</p>
                    </div>

                    <div className="flex items-start gap-2">
                      <input
                        type="checkbox"
                        id="consent"
                        className="h-4 w-4 mt-0.5 rounded border-gray-300 text-primary focus:ring-primary"
                        checked={formData.consent}
                        onChange={(e) => setFormData(prev => ({ ...prev, consent: e.target.checked }))}
                        required
                      />
                      <Label htmlFor="consent" className="text-sm font-normal text-muted-foreground">
                        I agree to receive communications from Encypher. I can unsubscribe at any time.
                      </Label>
                    </div>

                    {status === 'error' && (
                      <div className="p-4 bg-red-50 text-red-700 rounded-md text-sm">{errorMessage}</div>
                    )}

                    <Button type="submit" className="w-full py-3" disabled={status === 'submitting'}>
                      {status === 'submitting' ? (
                        <span className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Sending...</span>
                      ) : (
                        'Send Message'
                      )}
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar — quick contact info */}
          <div className="space-y-6">
            <Card>
              <CardContent className="pt-6 space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Mail className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Email Us</h3>
                    <a href="mailto:sales@encypherai.com" className="text-sm text-primary hover:underline">sales@encypherai.com</a>
                    <p className="text-xs text-muted-foreground mt-1">For sales & partnerships</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Enterprise</h3>
                    <a href="mailto:enterprise@encypherai.com" className="text-sm text-primary hover:underline">enterprise@encypherai.com</a>
                    <p className="text-xs text-muted-foreground mt-1">Custom implementations & SLAs</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Github className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Open Source</h3>
                    <a href="https://github.com/encypherai/encypher-ai" target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">github.com/encypherai</a>
                    <p className="text-xs text-muted-foreground mt-1">Issues, PRs, & discussions</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Clock className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Response Time</h3>
                    <p className="text-sm text-foreground">Within 24 hours</p>
                    <p className="text-xs text-muted-foreground mt-1">Mon–Fri, 9am–6pm PT</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="pt-6">
                <MessageSquare className="w-8 h-8 text-primary mb-3" />
                <h3 className="font-semibold mb-2">Looking for a demo?</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  See our interactive demos to understand how Encypher works for publishers and AI labs.
                </p>
                <div className="space-y-2">
                  <Button asChild variant="outline" className="w-full" size="sm">
                    <a href="/publisher-demo">Publisher Demo</a>
                  </Button>
                  <Button asChild variant="outline" className="w-full" size="sm">
                    <a href="/ai-demo">AI Lab Demo</a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

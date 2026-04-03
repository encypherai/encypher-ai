'use client';

import { useState } from 'react';
import { Button } from '@encypher/design-system';
import { Card, CardContent } from '@encypher/design-system';
import { Input } from '@encypher/design-system';
import { Textarea } from '@encypher/design-system';
import { Label } from '@encypher/design-system';
import { CheckCircle, Loader2, Shield, FileText, Zap, Clock } from 'lucide-react';
import TurnstileWidget from '@/components/security/TurnstileWidget';

export default function DemoPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    role: '',
    message: '',
    consent: false,
    source: 'demo-page',
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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
        body: JSON.stringify({ ...formData, context: 'general', turnstileToken }),
      });
      if (!response.ok) throw new Error('Failed to submit demo request');
      setStatus('success');
    } catch (error) {
      console.error('Demo request failed:', error);
      setStatus('error');
      setTurnstileToken(null);
      setErrorMessage(error instanceof Error ? error.message : 'Something went wrong. Please try again.');
    }
  };

  return (
    <section className="py-16 md:py-20 px-4 bg-background">
      <div className="container mx-auto max-w-5xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Schedule a Private Demo
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            See how sentence-level cryptographic proof transforms content protection and licensing. Tailored to your use case.
          </p>
        </div>

        <div className="grid lg:grid-cols-5 gap-8">
          {/* Form — 3 columns */}
          <div className="lg:col-span-3">
            <Card>
              <CardContent className="pt-6">
                {status === 'success' ? (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-foreground mb-2">Demo Request Received!</h2>
                    <p className="text-muted-foreground mb-2">
                      Thank you for your interest. We&apos;ve sent a confirmation to {formData.email}.
                    </p>
                    <p className="text-sm text-muted-foreground mb-8">
                      A member of our team will reach out within 24 hours to schedule your personalized demo.
                    </p>
                    <Button onClick={() => setStatus('idle')}>Submit Another Request</Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Full Name *</Label>
                        <Input id="name" name="name" required value={formData.name} onChange={handleChange} placeholder="Jane Smith" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email">Work Email *</Label>
                        <Input type="email" id="email" name="email" required value={formData.email} onChange={handleChange} placeholder="jane@company.com" />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="organization">Company / Organization *</Label>
                        <Input id="organization" name="organization" required value={formData.organization} onChange={handleChange} placeholder="Your company" />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="role">Job Title</Label>
                        <Input id="role" name="role" value={formData.role} onChange={handleChange} placeholder="VP of Engineering" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="message">What are you most interested in?</Label>
                      <Textarea id="message" name="message" rows={4} value={formData.message || ''} onChange={handleChange} placeholder="Tell us about your content protection challenges or what you'd like to see in the demo..." />
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

                    <TurnstileWidget
                      onVerify={setTurnstileToken}
                      onExpire={() => setTurnstileToken(null)}
                      onError={() => setTurnstileToken(null)}
                      action="demo-request"
                    />

                    {status === 'error' && (
                      <div className="p-4 bg-red-50 text-red-700 rounded-md text-sm">{errorMessage}</div>
                    )}

                    <Button type="submit" className="w-full py-3" disabled={status === 'submitting' || !turnstileToken}>
                      {status === 'submitting' ? (
                        <span className="flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Submitting...</span>
                      ) : (
                        'Request Private Demo'
                      )}
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar — what to expect */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="pt-6">
                <h3 className="font-bold text-lg mb-4">What You&apos;ll See</h3>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm">Live C2PA Signing</p>
                      <p className="text-xs text-muted-foreground">Watch content get cryptographically signed in real-time</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <FileText className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm">Tamper Detection</p>
                      <p className="text-xs text-muted-foreground">See how modifications are detected at the sentence level</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <Zap className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm">Enforcement Pipeline</p>
                      <p className="text-xs text-muted-foreground">From signing to formal notice to evidence package</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-medium text-sm">30-Minute Session</p>
                      <p className="text-xs text-muted-foreground">Tailored to your specific use case and questions</p>
                    </div>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-sm text-muted-foreground mb-3">Want to try it yourself first?</p>
                <div className="space-y-2">
                  <Button asChild variant="outline" className="w-full" size="sm">
                    <a href="/publisher-demo">Try Publisher Demo</a>
                  </Button>
                  <Button asChild variant="outline" className="w-full" size="sm">
                    <a href="/tools/sign-verify">Try Sign & Verify Tool</a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}

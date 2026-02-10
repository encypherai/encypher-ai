'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, consent: checked }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMessage('');

    try {
      const response = await fetch('/api/demo-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          context: 'general',
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to submit demo request');
      }
      setStatus('success');
    } catch (error) {
      console.error('Demo request failed:', error);
      setStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Something went wrong. Please try again.');
    }
  };

  return (
    <section className="py-20 px-4 bg-background">
      <div className="container mx-auto max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            Schedule a Demo
          </h1>
          <p className="text-xl text-muted-foreground">
            See how Encypher can protect your content and build trust with your audience.
          </p>
        </div>

        <Card className="bg-card">
            <CardContent className="pt-6">
              {status === 'success' ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-bold text-foreground mb-2">Request Received!</h2>
                  <p className="text-muted-foreground mb-8">
                    Thank you for your interest. We've sent a confirmation email to {formData.email}.
                    Our team will be in touch shortly.
                  </p>
                  <Button onClick={() => setStatus('idle')}>
                    Submit Another Request
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name *</Label>
                      <Input
                        type="text"
                        id="name"
                        name="name"
                        required
                        value={formData.name}
                        onChange={handleChange}
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
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="organization">Company / Organization</Label>
                      <Input
                        type="text"
                        id="organization"
                        name="organization"
                        value={formData.organization}
                        onChange={handleChange}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="role">Job Title</Label>
                      <Input
                        type="text"
                        id="role"
                        name="role"
                        value={formData.role}
                        onChange={handleChange}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message">How can we help?</Label>
                    <Textarea
                      id="message"
                      name="message"
                      rows={4}
                      value={formData.message || ''}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="flex items-start gap-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="consent"
                        className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                        checked={formData.consent}
                        onChange={(e) => handleCheckboxChange(e.target.checked)}
                      />
                      <Label htmlFor="consent" className="text-sm font-normal text-muted-foreground">
                        I agree to receive communications from Encypher. I can unsubscribe at any time.
                      </Label>
                    </div>
                  </div>

                  {status === 'error' && (
                    <div className="p-4 bg-red-50 text-red-700 rounded-md text-sm">
                      {errorMessage}
                    </div>
                  )}

                  <Button 
                    type="submit" 
                    className="w-full py-3"
                    disabled={status === 'submitting'}
                  >
                    {status === 'submitting' ? 'Submitting...' : 'Request Demo'}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
      </div>
    </section>
  );
}


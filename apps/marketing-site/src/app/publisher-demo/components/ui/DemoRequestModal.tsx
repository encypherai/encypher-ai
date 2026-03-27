'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
// AnimatePresence not used in this component
import { X, Loader2, CheckCircle } from 'lucide-react';
import { trackFormEvent } from '../../lib/analytics';
import TurnstileWidget from '@/components/security/TurnstileWidget';

interface DemoRequestModalProps {
  onClose: () => void;
}

interface FormData {
  name: string;
  email: string;
  organization: string;
  role: string;
  message: string;
  consent: boolean;
}

export default function DemoRequestModal({ onClose }: DemoRequestModalProps) {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    organization: '',
    role: '',
    message: '',
    consent: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/demo-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          source: 'publisher-demo',
          context: 'publisher',
          turnstileToken,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit demo request');
      }

      const data = await response.json();
      trackFormEvent('submitted', { requestId: data.id });
      setIsSuccess(true);

      // Close modal after 3 seconds
      setTimeout(() => {
        onClose();
      }, 3000);
    } catch (err) {
      setError('Failed to submit request. Please try again or contact demo@encypher.com');
      setTurnstileToken(null);
      trackFormEvent('error', { error: err instanceof Error ? err.message : 'Unknown error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Request a Private Demo</h2>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-900 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {isSuccess ? (
            <motion.div
              className="text-center py-12"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Demo Request Received</h3>
              <p className="text-slate-700 mb-4">
                Thank you for your interest in Encypher.
              </p>
              <p className="text-slate-600 text-sm">
                A member of our team will contact you within 24 hours to schedule your private demonstration.
              </p>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-semibold text-slate-900 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-blue-ncs"
                  placeholder="Jane Smith"
                />
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-slate-900 mb-2">
                  Work Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-blue-ncs"
                  placeholder="jane.smith@publisher.com"
                />
              </div>

              {/* Organization */}
              <div>
                <label htmlFor="organization" className="block text-sm font-semibold text-slate-900 mb-2">
                  Organization *
                </label>
                <input
                  type="text"
                  id="organization"
                  name="organization"
                  required
                  value={formData.organization}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-blue-ncs"
                  placeholder="The Encypher Times"
                />
              </div>

              {/* Role */}
              <div>
                <label htmlFor="role" className="block text-sm font-semibold text-slate-900 mb-2">
                  Your Role *
                </label>
                <select
                  id="role"
                  name="role"
                  required
                  value={formData.role}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-blue-ncs"
                >
                  <option value="">Select your role</option>
                  <option value="c-suite">C-Suite Executive</option>
                  <option value="vp-strategy">VP/Director of Strategy</option>
                  <option value="vp-legal">VP/Director of Legal</option>
                  <option value="vp-tech">VP/Director of Technology</option>
                  <option value="product">Product Manager</option>
                  <option value="bizdev">Business Development</option>
                  <option value="investor">Investor</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Message */}
              <div>
                <label htmlFor="message" className="block text-sm font-semibold text-slate-900 mb-2">
                  What are you most interested in learning about? (Optional)
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={4}
                  maxLength={500}
                  value={formData.message}
                  onChange={handleChange}
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-ncs focus:border-blue-ncs resize-none"
                  placeholder="Tell us about your content protection challenges..."
                />
                <p className="text-xs text-slate-500 mt-1">{formData.message.length}/500 characters</p>
              </div>

              {/* Consent */}
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="consent"
                  name="consent"
                  required
                  checked={formData.consent}
                  onChange={handleChange}
                  className="mt-1 w-4 h-4 bg-white border-slate-300 rounded focus:ring-2 focus:ring-blue-ncs"
                />
                <label htmlFor="consent" className="text-sm text-slate-600">
                  I agree to receive communications from Encypher about this demo and related products. You can unsubscribe at any time.
                </label>
              </div>

              <TurnstileWidget
                onVerify={setTurnstileToken}
                onExpire={() => setTurnstileToken(null)}
                onError={() => setTurnstileToken(null)}
                action="publisher-demo"
              />

              {/* Error */}
              {error && (
                <div className="bg-red-50 border border-red-300 rounded-lg p-4 text-red-700 text-sm">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isSubmitting || !turnstileToken}
                // TEAM_061: Remove blue/purple gradients; use design-system token colors.
                className="w-full px-6 py-3 bg-blue-ncs hover:bg-blue-ncs/90 active:bg-blue-ncs/80 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-semibold transition-all flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-ncs"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  'Submit Request'
                )}
              </button>
            </form>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

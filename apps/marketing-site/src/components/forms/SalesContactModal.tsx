'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Loader2, CheckCircle } from 'lucide-react';
import { submitDemoRequest } from '@/lib/api';

export type ContactContext = 'ai' | 'publisher' | 'enterprise' | 'general';

interface SalesContactModalProps {
  onClose: () => void;
  context?: ContactContext;
  title?: string;
  subtitle?: string;
}

interface FormData {
  name: string;
  email: string;
  organization: string;
  role: string;
  message: string;
  consent: boolean;
}

const contextConfig = {
  ai: {
    title: 'Schedule Technical Deep Dive',
    subtitle: 'Let\'s discuss how Encypher can help you track and analyze AI-generated content.',
    emailPlaceholder: 'john.smith@aicompany.com',
    orgPlaceholder: 'OpenAI',
    messagePlaceholder: 'Tell us about your AI performance analytics needs...',
    roles: [
      { value: 'c-suite', label: 'C-Suite Executive' },
      { value: 'vp-rd', label: 'VP/Director of R&D' },
      { value: 'vp-product', label: 'VP/Director of Product' },
      { value: 'vp-engineering', label: 'VP/Director of Engineering' },
      { value: 'ml-engineer', label: 'ML Engineer' },
      { value: 'data-scientist', label: 'Data Scientist' },
      { value: 'product-manager', label: 'Product Manager' },
      { value: 'investor', label: 'Investor' },
      { value: 'other', label: 'Other' },
    ],
    apiEndpoint: '/api/v1/ai-demo/demo-requests',
    source: 'ai-demo',
  },
  publisher: {
    title: 'Request a Private Demo',
    subtitle: 'Discover how Encypher can help you protect and monetize your content.',
    emailPlaceholder: 'jane.smith@publisher.com',
    orgPlaceholder: 'The New York Times',
    messagePlaceholder: 'Tell us about your content protection challenges...',
    roles: [
      { value: 'c-suite', label: 'C-Suite Executive' },
      { value: 'vp-strategy', label: 'VP/Director of Strategy' },
      { value: 'vp-legal', label: 'VP/Director of Legal' },
      { value: 'vp-tech', label: 'VP/Director of Technology' },
      { value: 'product', label: 'Product Manager' },
      { value: 'bizdev', label: 'Business Development' },
      { value: 'investor', label: 'Investor' },
      { value: 'other', label: 'Other' },
    ],
    apiEndpoint: '/api/v1/publisher-demo/demo-requests',
    source: 'publisher-demo',
  },
  enterprise: {
    title: 'Contact Enterprise Sales',
    subtitle: 'Let\'s discuss how Encypher can meet your organization\'s specific needs.',
    emailPlaceholder: 'contact@company.com',
    orgPlaceholder: 'Your Company',
    messagePlaceholder: 'Tell us about your requirements and use case...',
    roles: [
      { value: 'c-suite', label: 'C-Suite Executive' },
      { value: 'vp-it', label: 'VP/Director of IT' },
      { value: 'vp-operations', label: 'VP/Director of Operations' },
      { value: 'vp-security', label: 'VP/Director of Security' },
      { value: 'vp-compliance', label: 'VP/Director of Compliance' },
      { value: 'procurement', label: 'Procurement' },
      { value: 'it-manager', label: 'IT Manager' },
      { value: 'project-manager', label: 'Project Manager' },
      { value: 'other', label: 'Other' },
    ],
    apiEndpoint: '/api/v1/sales/enterprise-requests',
    source: 'enterprise-sales',
  },
  general: {
    title: 'Contact Sales',
    subtitle: 'We\'d love to hear from you. Let us know how we can help.',
    emailPlaceholder: 'your.email@company.com',
    orgPlaceholder: 'Your Organization',
    messagePlaceholder: 'Tell us about your needs...',
    roles: [
      { value: 'c-suite', label: 'C-Suite Executive' },
      { value: 'vp-director', label: 'VP/Director' },
      { value: 'manager', label: 'Manager' },
      { value: 'engineer', label: 'Engineer/Technical' },
      { value: 'product', label: 'Product' },
      { value: 'bizdev', label: 'Business Development' },
      { value: 'investor', label: 'Investor' },
      { value: 'other', label: 'Other' },
    ],
    apiEndpoint: '/api/v1/sales/general-requests',
    source: 'general-sales',
  },
};

export default function SalesContactModal({ 
  onClose, 
  context = 'general',
  title,
  subtitle 
}: SalesContactModalProps) {
  const config = contextConfig[context];
  const displayTitle = title || config.title;
  const displaySubtitle = subtitle || config.subtitle;

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const url = `${baseUrl}${config.apiEndpoint}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          source: config.source,
          context,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit request');
      }

      const data = await response.json();
      setIsSuccess(true);

      // Close modal after 3 seconds
      setTimeout(() => {
        onClose();
      }, 3000);
    } catch (err) {
      setError('Failed to submit request. Please try again or contact sales@encypher.com');
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
        <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">{displayTitle}</h2>
            {displaySubtitle && (
              <p className="text-sm text-slate-600 mt-1">{displaySubtitle}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-900 transition-colors flex-shrink-0 ml-4"
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
              <h3 className="text-2xl font-bold text-slate-900 mb-2">Request Received</h3>
              <p className="text-slate-700 mb-4">
                Thank you for your interest in Encypher.
              </p>
              <p className="text-slate-600 text-sm">
                A member of our team will contact you within 24 hours.
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
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="John Smith"
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
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder={config.emailPlaceholder}
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
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder={config.orgPlaceholder}
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
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select your role</option>
                  {config.roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
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
                  className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder={config.messagePlaceholder}
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
                  className="mt-1 w-4 h-4 bg-white border-slate-300 rounded focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="consent" className="text-sm text-slate-600">
                  I agree to receive communications from Encypher about this inquiry and related products. You can unsubscribe at any time.
                </label>
              </div>

              {/* Error */}
              {error && (
                <div className="bg-red-50 border border-red-300 rounded-lg p-4 text-red-700 text-sm">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-semibold transition-all flex items-center justify-center gap-2"
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

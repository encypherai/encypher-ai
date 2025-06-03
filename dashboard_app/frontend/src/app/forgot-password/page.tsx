'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { EnvelopeIcon } from '@heroicons/react/24/outline';
import { useNotifications } from '@/lib/notifications';
import { requestPasswordReset } from '@/lib/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';

type ForgotPasswordFormData = {
  email: string;
};

export default function ForgotPasswordPage() {
  const router = useRouter();
  const { addNotification } = useNotifications();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>();

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsSubmitting(true);
    try {
      await requestPasswordReset(data.email);
      setEmailSent(true);
      addNotification({
        type: 'success',
        title: 'Email Sent',
        message: 'If your email is registered, you will receive password reset instructions.',
        duration: 5000,
      });
    } catch (error) {
      // We don't want to reveal if the email exists or not for security reasons
      // So we show the same success message even if the API call fails
      setEmailSent(true);
      addNotification({
        type: 'success',
        title: 'Email Sent',
        message: 'If your email is registered, you will receive password reset instructions.',
        duration: 5000,
      });
      console.error('Error requesting password reset:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reset Your Password</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {emailSent
              ? 'Check your email for reset instructions'
              : 'Enter your email address and we will send you instructions to reset your password'}
          </p>
        </div>

        {!emailSent ? (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Input
                label="Email Address"
                type="email"
                error={errors.email?.message}
                icon={<div className="text-gray-400"><EnvelopeIcon className="h-5 w-5" /></div>}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
              />
            </div>
            
            <Button
              type="submit"
              fullWidth
              isLoading={isSubmitting}
              disabled={isSubmitting}
            >
              Send Reset Instructions
            </Button>
            
            <div className="text-center">
              <Link 
                href="/login" 
                className="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
              >
                Back to Login
              </Link>
            </div>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-md">
              <p className="text-green-800 dark:text-green-200 text-sm">
                If your email is registered in our system, you will receive instructions to reset your password shortly.
              </p>
            </div>
            <Button
              onClick={() => router.push('/login')}
              fullWidth
            >
              Return to Login
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

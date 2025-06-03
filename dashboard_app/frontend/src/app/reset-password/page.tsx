'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { LockClosedIcon } from '@heroicons/react/24/outline';
import { useNotifications } from '@/lib/notifications';
import { resetPassword } from '@/lib/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Card from '@/components/ui/Card';

type ResetPasswordFormData = {
  newPassword: string;
  confirmPassword: string;
};

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const { addNotification } = useNotifications();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resetComplete, setResetComplete] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ResetPasswordFormData>();
  
  const password = watch('newPassword');

  // If no token is provided, show an error
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <Card className="w-full max-w-md p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Invalid Reset Link</h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              This password reset link is invalid or has expired.
            </p>
          </div>
          <Button
            onClick={() => router.push('/forgot-password')}
            fullWidth
          >
            Request New Reset Link
          </Button>
        </Card>
      </div>
    );
  }

  const onSubmit = async (data: ResetPasswordFormData) => {
    setIsSubmitting(true);
    try {
      await resetPassword({
        token,
        newPassword: data.newPassword,
        confirmPassword: data.confirmPassword,
      });
      
      setResetComplete(true);
      addNotification({
        type: 'success',
        title: 'Password Reset',
        message: 'Your password has been reset successfully.',
        duration: 5000,
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Reset Failed',
        message: error.response?.data?.detail || 'Failed to reset password. The link may be invalid or expired.',
        duration: 5000,
      });
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
            {resetComplete
              ? 'Your password has been reset successfully'
              : 'Enter your new password below'}
          </p>
        </div>

        {!resetComplete ? (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <Input
                label="New Password"
                type="password"
                error={errors.newPassword?.message}
                icon={<div className="text-gray-400"><LockClosedIcon className="h-5 w-5" /></div>}
                {...register('newPassword', {
                  required: 'New password is required',
                  minLength: {
                    value: 8,
                    message: 'Password must be at least 8 characters',
                  },
                })}
              />
            </div>
            
            <div>
              <Input
                label="Confirm Password"
                type="password"
                error={errors.confirmPassword?.message}
                icon={<div className="text-gray-400"><LockClosedIcon className="h-5 w-5" /></div>}
                {...register('confirmPassword', {
                  required: 'Please confirm your password',
                  validate: value => value === password || 'Passwords do not match',
                })}
              />
            </div>
            
            <Button
              type="submit"
              fullWidth
              isLoading={isSubmitting}
              disabled={isSubmitting}
            >
              Reset Password
            </Button>
          </form>
        ) : (
          <div className="space-y-6">
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-md">
              <p className="text-green-800 dark:text-green-200 text-sm">
                Your password has been reset successfully. You can now log in with your new password.
              </p>
            </div>
            <Button
              onClick={() => router.push('/login')}
              fullWidth
            >
              Go to Login
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

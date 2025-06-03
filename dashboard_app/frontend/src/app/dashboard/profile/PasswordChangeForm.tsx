'use client';

import React, { useState } from 'react';
import { usePasswordUpdate } from '@/lib/hooks/usePasswordUpdate';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

interface PasswordChangeFormProps {
  onCancel: () => void;
  onSuccess?: () => void;
}

export default function PasswordChangeForm({ onCancel, onSuccess }: PasswordChangeFormProps) {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const { mutate: updatePassword, isLoading } = usePasswordUpdate({
    onSuccess: () => {
      // Clear form data
      setFormData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      // Call parent success handler if provided
      if (onSuccess) {
        onSuccess();
      }
    }
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.current_password) {
      newErrors.current_password = 'Current password is required';
    }
    
    if (!formData.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (formData.new_password.length < 8) {
      newErrors.new_password = 'Password must be at least 8 characters';
    }
    
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your new password';
    } else if (formData.new_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      updatePassword(formData);
    }
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    if (field === 'current') {
      setShowCurrentPassword(!showCurrentPassword);
    } else if (field === 'new') {
      setShowNewPassword(!showNewPassword);
    } else {
      setShowConfirmPassword(!showConfirmPassword);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <div className="relative">
          <Input
            type={showCurrentPassword ? 'text' : 'password'}
            name="current_password"
            label="Current Password"
            value={formData.current_password}
            onChange={handleInputChange}
            error={errors.current_password}
            required
            className="pr-10"
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('current')}
          >
            {showCurrentPassword ? (
              <EyeSlashIcon className="h-5 w-5 text-gray-400" />
            ) : (
              <EyeIcon className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>
      
      <div>
        <div className="relative">
          <Input
            type={showNewPassword ? 'text' : 'password'}
            name="new_password"
            label="New Password"
            value={formData.new_password}
            onChange={handleInputChange}
            error={errors.new_password}
            required
            className="pr-10"
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('new')}
          >
            {showNewPassword ? (
              <EyeSlashIcon className="h-5 w-5 text-gray-400" />
            ) : (
              <EyeIcon className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
          Password must be at least 8 characters
        </p>
      </div>
      
      <div>
        <div className="relative">
          <Input
            type={showConfirmPassword ? 'text' : 'password'}
            name="confirm_password"
            label="Confirm New Password"
            value={formData.confirm_password}
            onChange={handleInputChange}
            error={errors.confirm_password}
            required
            className="pr-10"
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 top-6 pr-3 flex items-center"
            onClick={() => togglePasswordVisibility('confirm')}
          >
            {showConfirmPassword ? (
              <EyeSlashIcon className="h-5 w-5 text-gray-400" />
            ) : (
              <EyeIcon className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
      </div>
      
      <div className="flex justify-end space-x-3 mt-4">
        <Button
          type="button"
          variant="ghost"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
        >
          Update Password
        </Button>
      </div>
    </form>
  );
}

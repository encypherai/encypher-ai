'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { useNotifications } from '@/lib/notifications';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { MoonIcon, SunIcon, UserIcon, KeyIcon } from '@heroicons/react/24/outline';

interface UserPreferences {
  darkMode: boolean;
  defaultPageSize: number;
  emailNotifications: boolean;
}

export default function SettingsPage() {
  const { user, updateUserProfile, changePassword } = useAuth();
  const { addNotification } = useNotifications();
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
    department: '',
  });
  
  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  // Preferences form state
  const [preferences, setPreferences] = useState<UserPreferences>({
    darkMode: false,
    defaultPageSize: 10,
    emailNotifications: true,
  });
  
  // Loading states
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  const [isPasswordLoading, setIsPasswordLoading] = useState(false);
  const [isPreferencesLoading, setIsPreferencesLoading] = useState(false);
  
  // Error states
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [preferencesError, setPreferencesError] = useState<string | null>(null);
  
  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setProfileForm({
        name: user.name || '',
        email: user.email || '',
        department: user.department || '',
      });
    }
    
    // Load preferences from localStorage
    const storedPreferences = localStorage.getItem('userPreferences');
    if (storedPreferences) {
      try {
        const parsedPreferences = JSON.parse(storedPreferences);
        setPreferences(parsedPreferences);
      } catch (error) {
        console.error('Failed to parse stored preferences:', error);
      }
    } else {
      // Set default preferences based on system
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setPreferences(prev => ({ ...prev, darkMode: prefersDark }));
    }
  }, [user]);
  
  // Apply dark mode preference
  useEffect(() => {
    if (preferences.darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [preferences.darkMode]);
  
  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handlePreferenceChange = (name: keyof UserPreferences, value: any) => {
    setPreferences(prev => ({ ...prev, [name]: value }));
  };
  
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProfileLoading(true);
    setProfileError(null);
    
    try {
      // This would call the API to update the user profile
      // For now, we'll just simulate success
      await updateUserProfile(profileForm);
      
      addNotification({
        type: 'success',
        title: 'Profile Updated',
        message: 'Your profile information has been updated successfully.',
      });
    } catch (error: any) {
      setProfileError(error.message || 'Failed to update profile. Please try again.');
      
      addNotification({
        type: 'error',
        title: 'Profile Update Failed',
        message: error.message || 'Failed to update profile. Please try again.',
      });
    } finally {
      setIsProfileLoading(false);
    }
  };
  
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPasswordLoading(true);
    setPasswordError(null);
    
    // Validate passwords
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordError('New passwords do not match.');
      setIsPasswordLoading(false);
      return;
    }
    
    try {
      // This would call the API to change the password
      // For now, we'll just simulate success
      await changePassword(passwordForm.currentPassword, passwordForm.newPassword);
      
      // Reset form
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      
      addNotification({
        type: 'success',
        title: 'Password Changed',
        message: 'Your password has been changed successfully.',
      });
    } catch (error: any) {
      setPasswordError(error.message || 'Failed to change password. Please try again.');
      
      addNotification({
        type: 'error',
        title: 'Password Change Failed',
        message: error.message || 'Failed to change password. Please try again.',
      });
    } finally {
      setIsPasswordLoading(false);
    }
  };
  
  const handlePreferencesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPreferencesLoading(true);
    setPreferencesError(null);
    
    try {
      // Save preferences to localStorage
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      
      addNotification({
        type: 'success',
        title: 'Preferences Saved',
        message: 'Your preferences have been saved successfully.',
      });
    } catch (error: any) {
      setPreferencesError(error.message || 'Failed to save preferences. Please try again.');
      
      addNotification({
        type: 'error',
        title: 'Preferences Save Failed',
        message: error.message || 'Failed to save preferences. Please try again.',
      });
    } finally {
      setIsPreferencesLoading(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Settings</h1>
      
      {/* Profile Settings */}
      <Card title="Profile Information">
        <form onSubmit={handleProfileSubmit} className="space-y-4">
          {profileError && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{profileError}</span>
            </div>
          )}
          
          <div className="flex items-center space-x-4 mb-4">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-full p-3">
              <UserIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {profileForm.name || 'User Profile'}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {profileForm.email || 'No email set'}
              </p>
            </div>
          </div>
          
          <Input
            label="Full Name"
            name="name"
            value={profileForm.name}
            onChange={handleProfileChange}
          />
          
          <Input
            label="Email Address"
            type="email"
            name="email"
            value={profileForm.email}
            onChange={handleProfileChange}
          />
          
          <Input
            label="Department"
            name="department"
            value={profileForm.department}
            onChange={handleProfileChange}
          />
          
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              isLoading={isProfileLoading}
            >
              Save Profile
            </Button>
          </div>
        </form>
      </Card>
      
      {/* Password Settings */}
      <Card title="Change Password">
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          {passwordError && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{passwordError}</span>
            </div>
          )}
          
          <div className="flex items-center space-x-4 mb-4">
            <div className="bg-gray-200 dark:bg-gray-700 rounded-full p-3">
              <KeyIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Password Security
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Ensure your account is using a strong password
              </p>
            </div>
          </div>
          
          <Input
            label="Current Password"
            type="password"
            name="currentPassword"
            value={passwordForm.currentPassword}
            onChange={handlePasswordChange}
          />
          
          <Input
            label="New Password"
            type="password"
            name="newPassword"
            value={passwordForm.newPassword}
            onChange={handlePasswordChange}
          />
          
          <Input
            label="Confirm New Password"
            type="password"
            name="confirmPassword"
            value={passwordForm.confirmPassword}
            onChange={handlePasswordChange}
          />
          
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              isLoading={isPasswordLoading}
            >
              Change Password
            </Button>
          </div>
        </form>
      </Card>
      
      {/* Preferences Settings */}
      <Card title="User Preferences">
        <form onSubmit={handlePreferencesSubmit} className="space-y-4">
          {preferencesError && (
            <div className="bg-red-50 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{preferencesError}</span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {preferences.darkMode ? (
                <MoonIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              ) : (
                <SunIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              )}
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Dark Mode
              </span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={preferences.darkMode}
                onChange={(e) => handlePreferenceChange('darkMode', e.target.checked)}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
          
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <Select
              label="Default Page Size"
              options={[
                { value: '5', label: '5 items per page' },
                { value: '10', label: '10 items per page' },
                { value: '25', label: '25 items per page' },
                { value: '50', label: '50 items per page' },
                { value: '100', label: '100 items per page' },
              ]}
              value={preferences.defaultPageSize.toString()}
              onChange={(value) => handlePreferenceChange('defaultPageSize', parseInt(value, 10))}
            />
          </div>
          
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Email Notifications
            </span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={preferences.emailNotifications}
                onChange={(e) => handlePreferenceChange('emailNotifications', e.target.checked)}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
          
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              isLoading={isPreferencesLoading}
            >
              Save Preferences
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

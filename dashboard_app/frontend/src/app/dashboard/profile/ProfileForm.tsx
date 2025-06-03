'use client';

import React, { useState, useEffect } from 'react';
import { User } from '@/lib/services/users';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { PencilIcon, UserIcon } from '@heroicons/react/24/outline';
import PasswordChangeForm from './PasswordChangeForm';

interface ProfileFormProps {
  user: User;
  isUpdating: boolean;
  onUpdate: (userData: Partial<User>) => void;
}

interface FormData {
  first_name: string;
  last_name: string;
  email: string;
  department: string;
}

const ProfileForm: React.FC<ProfileFormProps> = ({
  user,
  isUpdating,
  onUpdate
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    email: '',
    department: ''
  });

  // Update form data when user data changes
  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        department: user.department || ''
      });
    }
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    if (user) {
      setFormData({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        department: user.department || ''
      });
    }
    setIsEditing(false);
  };

  return (
    <div className="mb-6">
      {isEditing ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-medium text-gray-900 dark:text-white">Edit Profile</h2>
            <div className="flex space-x-2">
              <Button 
                variant="ghost"
                onClick={handleCancel}
                disabled={isUpdating}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isUpdating}
              >
                Save Changes
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              required
            />
            <Input
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              required
            />
            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
            <Input
              label="Department"
              name="department"
              value={formData.department}
              onChange={handleInputChange}
            />
          </div>
        </form>
      ) : (
        <>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <UserIcon className="h-8 w-8 text-gray-500 dark:text-gray-400" />
              </div>
              <div>
                <h2 className="text-xl font-medium text-gray-900 dark:text-white">
                  {user?.first_name} {user?.last_name}
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setIsEditing(true)}
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              Edit Profile
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Account Information</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-5 w-5 text-gray-400 dark:text-gray-500 mr-3 mt-0.5">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                      <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Email</p>
                    <p className="text-sm text-gray-900 dark:text-white">{user?.email}</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-5 w-5 text-gray-400 dark:text-gray-500 mr-3 mt-0.5">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h6v4H7V5zm8 8v2h1v1H4v-1h1v-2h-.5a.5.5 0 01-.5-.5v-2a.5.5 0 01.5-.5H7v4h6v-4h2.5a.5.5 0 01.5.5v2a.5.5 0 01-.5.5H15z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Department</p>
                    <p className="text-sm text-gray-900 dark:text-white">{user?.department || 'Not specified'}</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-5 w-5 text-gray-400 dark:text-gray-500 mr-3 mt-0.5">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Role</p>
                    <p className="text-sm text-gray-900 dark:text-white">{user?.role || 'User'}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Session Information</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-5 w-5 text-gray-400 dark:text-gray-500 mr-3 mt-0.5">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Login</p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {user?.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Password Change Section */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Password</h3>
            
            {isChangingPassword ? (
              <PasswordChangeForm 
                onCancel={() => setIsChangingPassword(false)}
                onSuccess={() => setIsChangingPassword(false)}
              />
            ) : (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Update your password to keep your account secure
                </p>
                <Button
                  variant="secondary"
                  onClick={() => setIsChangingPassword(true)}
                >
                  Change Password
                </Button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ProfileForm;

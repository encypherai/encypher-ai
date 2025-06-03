'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth';

export default function TestLoginPage() {
  const { login, user, isAuthenticated, isLoading, error, logout } = useAuth();
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('admin123');
  const [rememberMe, setRememberMe] = useState(true);
  const [loginStatus, setLoginStatus] = useState<string | null>(null);

  const handleLogin = async () => {
    try {
      setLoginStatus('Attempting login...');
      await login(email, password, rememberMe);
      setLoginStatus('Login successful!');
    } catch (err: any) {
      console.error('Login error details:', err);
      // Handle different types of errors
      if (err.response?.data?.detail) {
        // FastAPI validation error format
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // Handle validation errors array
          const errorMessages = detail.map(e => `${e.loc.join('.')} - ${e.msg}`).join(', ');
          setLoginStatus(`Login failed: ${errorMessages}`);
        } else {
          // Handle string error
          setLoginStatus(`Login failed: ${detail}`);
        }
      } else {
        // Generic error handling
        setLoginStatus(`Login failed: ${err.message || 'Unknown error'}`);
      }
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Authentication Test Page</h1>
      
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">Login Test</h2>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded"
            />
          </div>
          
          <div className="mb-4">
            <label className="block mb-2">Password:</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              className="border p-2 w-full"
            />
          </div>
          
          <div className="mb-4">
            <label className="flex items-center">
              <input 
                type="checkbox" 
                checked={rememberMe} 
                onChange={(e) => setRememberMe(e.target.checked)} 
                className="mr-2"
              />
              Remember me for 30 days
            </label>
          </div>
        </div>
        
        <div className="flex space-x-4">
          <button 
            onClick={handleLogin}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Loading...' : 'Login'}
          </button>
          
          <button 
            onClick={logout}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Logout
          </button>
        </div>
        
        {loginStatus && (
          <div className={`mt-4 p-3 rounded ${loginStatus.includes('failed') ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
            {loginStatus}
          </div>
        )}
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-800 rounded">
            Error: {error}
          </div>
        )}
      </div>
      
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
        
        <div className="space-y-2">
          <p><strong>Is Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
          <p><strong>Is Loading:</strong> {isLoading ? 'Yes' : 'No'}</p>
          
          {user && (
            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">User Information</h3>
              <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded overflow-auto">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Test Credentials</h2>
        <ul className="list-disc pl-5 space-y-2">
          <li><strong>Admin User:</strong> admin / admin123</li>
          <li><strong>Regular User:</strong> user / user123</li>
        </ul>
      </div>
    </div>
  );
}

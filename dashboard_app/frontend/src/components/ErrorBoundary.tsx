'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import ErrorDisplay from './ui/ErrorDisplay';
import Button from './ui/Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // You can also log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
    
    // Here you could send the error to your analytics or error tracking service
    // Example: sendToErrorTracking(error, errorInfo);
  }

  resetErrorBoundary = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <ErrorDisplay
              title="Something went wrong"
              message={this.state.error?.message || 'An unexpected error occurred.'}
              className="mb-4"
            />
            
            <div className="mt-4 space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Please try refreshing the page or contact support if the problem persists.
              </p>
              
              <div className="flex space-x-4">
                <Button
                  variant="primary"
                  onClick={this.resetErrorBoundary}
                >
                  Try Again
                </Button>
                
                <Button
                  variant="secondary"
                  onClick={() => window.location.href = '/dashboard'}
                >
                  Go to Dashboard
                </Button>
              </div>
              
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <div className="mt-6">
                  <details className="whitespace-pre-wrap text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 p-4 rounded-md">
                    <summary className="font-medium mb-2 cursor-pointer">Error Details (Development Only)</summary>
                    <p className="mb-2">{this.state.error?.toString()}</p>
                    <p className="font-mono">{this.state.errorInfo.componentStack}</p>
                  </details>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

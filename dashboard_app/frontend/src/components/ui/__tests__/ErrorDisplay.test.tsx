// __tests__/ErrorDisplay.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import ErrorDisplay from '../ErrorDisplay';

describe('ErrorDisplay Component', () => {
  it('should render the error message correctly when message prop is provided', () => {
    const errorMessage = 'Something went terribly wrong!';
    render(<ErrorDisplay message={errorMessage} />);
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    // Default title should also be present
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });

  it('should render the error message from error object if provided', () => {
    const errorObj = new Error('Error from error object');
    render(<ErrorDisplay error={errorObj} />);
    expect(screen.getByText(errorObj.message)).toBeInTheDocument();
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });

  it('should prioritize error object message over message prop', () => {
    const errorObj = new Error('Priority error message');
    const messageProp = 'This should be overridden';
    render(<ErrorDisplay error={errorObj} message={messageProp} />);
    expect(screen.getByText(errorObj.message)).toBeInTheDocument();
    expect(screen.queryByText(messageProp)).not.toBeInTheDocument();
  });

  it('should render a default message if no message or error prop is provided', () => {
    render(<ErrorDisplay />);
    expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
    expect(screen.getByText('An error occurred')).toBeInTheDocument(); 
  });

  it('should render with a custom title if provided', () => {
    const title = 'Network Error';
    const errorMessage = 'Could not connect to the server.';
    render(<ErrorDisplay title={title} message={errorMessage} />);
    expect(screen.getByText(title)).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('should render a retry button with specific text if onRetry is provided', () => {
    const handleRetry = jest.fn();
    render(<ErrorDisplay message="Failed to load data" onRetry={handleRetry} />);
    const retryButton = screen.getByRole('button', { name: 'Try again' });
    expect(retryButton).toBeInTheDocument();
    retryButton.click();
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it('should not render a retry button if onRetry is not provided', () => {
    render(<ErrorDisplay message="Failed to load data" />);
    const retryButton = screen.queryByRole('button', { name: 'Try again' });
    expect(retryButton).not.toBeInTheDocument();
  });

  it('should apply custom className if provided', () => {
    const customClass = 'my-custom-error-class';
    const { container } = render(<ErrorDisplay message="Test" className={customClass} />);
    // The component's root div has other classes, so we check for the presence of the custom one.
    expect(container.firstChild).toHaveClass(customClass);
  });
});

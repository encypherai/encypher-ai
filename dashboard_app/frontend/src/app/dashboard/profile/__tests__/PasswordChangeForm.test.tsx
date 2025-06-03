import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PasswordChangeForm from '../PasswordChangeForm';

// Mock the usePasswordUpdate hook
jest.mock('@/lib/hooks/usePasswordUpdate', () => ({
  usePasswordUpdate: jest.fn(() => ({
    mutate: jest.fn((data, options) => {
      if (options?.onSuccess) {
        options.onSuccess();
      }
    }),
    isLoading: false
  }))
}));

// Mock the UI components
jest.mock('@/components/ui/Button', () => {
  return function MockButton({ 
    children, 
    onClick, 
    type, 
    disabled, 
    isLoading,
    variant 
  }: { 
    children: React.ReactNode, 
    onClick?: () => void, 
    type?: 'button' | 'submit', 
    disabled?: boolean,
    isLoading?: boolean,
    variant?: string
  }) {
    return (
      <button 
        onClick={onClick} 
        type={type || 'button'} 
        disabled={disabled || isLoading}
        data-variant={variant}
      >
        {isLoading ? 'Loading...' : children}
      </button>
    );
  };
});

jest.mock('@/components/ui/Input', () => {
  return function MockInput({ 
    label, 
    name, 
    type, 
    value, 
    onChange, 
    error,
    required,
    className
  }: { 
    label: string, 
    name: string, 
    type: string, 
    value: string, 
    onChange: (e: any) => void, 
    error?: string,
    required?: boolean,
    className?: string
  }) {
    return (
      <div>
        <label htmlFor={name}>{label}</label>
        <input 
          id={name}
          name={name} 
          type={type} 
          value={value} 
          onChange={onChange}
          required={required}
          className={className}
          data-testid={`input-${name}`}
        />
        {error && <span data-testid={`error-${name}`}>{error}</span>}
      </div>
    );
  };
});

describe('PasswordChangeForm', () => {
  const mockOnCancel = jest.fn();
  const mockOnSuccess = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the password change form correctly', () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Check if all inputs are rendered
    expect(screen.getByLabelText('Current Password')).toBeInTheDocument();
    expect(screen.getByLabelText('New Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm New Password')).toBeInTheDocument();
    
    // Check if buttons are rendered
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Update Password')).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    fireEvent.click(screen.getByText('Cancel'));
    
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it('shows validation errors when form is submitted with empty fields', async () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Submit the form without filling any fields
    fireEvent.click(screen.getByText('Update Password'));
    
    // Check if validation errors are displayed
    await waitFor(() => {
      expect(screen.getByTestId('error-current_password')).toBeInTheDocument();
      expect(screen.getByTestId('error-new_password')).toBeInTheDocument();
      expect(screen.getByTestId('error-confirm_password')).toBeInTheDocument();
    });
  });

  it('shows validation error when passwords do not match', async () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Fill in the form with non-matching passwords
    await userEvent.type(screen.getByTestId('input-current_password'), 'currentpass123');
    await userEvent.type(screen.getByTestId('input-new_password'), 'newpassword123');
    await userEvent.type(screen.getByTestId('input-confirm_password'), 'differentpassword123');
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Password'));
    
    // Check if validation error for password mismatch is displayed
    await waitFor(() => {
      expect(screen.getByTestId('error-confirm_password')).toHaveTextContent('Passwords do not match');
    });
  });

  it('shows validation error when new password is too short', async () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Fill in the form with a short password
    await userEvent.type(screen.getByTestId('input-current_password'), 'currentpass123');
    await userEvent.type(screen.getByTestId('input-new_password'), 'short');
    await userEvent.type(screen.getByTestId('input-confirm_password'), 'short');
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Password'));
    
    // Check if validation error for short password is displayed
    await waitFor(() => {
      expect(screen.getByTestId('error-new_password')).toHaveTextContent('Password must be at least 8 characters');
    });
  });

  it('submits the form successfully when all validations pass', async () => {
    const { usePasswordUpdate } = require('@/lib/hooks/usePasswordUpdate');
    const mockUpdatePassword = jest.fn();
    
    (usePasswordUpdate as jest.Mock).mockReturnValue({
      mutate: mockUpdatePassword,
      isLoading: false
    });
    
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Fill in the form with valid data
    await userEvent.type(screen.getByTestId('input-current_password'), 'currentpass123');
    await userEvent.type(screen.getByTestId('input-new_password'), 'newpassword123');
    await userEvent.type(screen.getByTestId('input-confirm_password'), 'newpassword123');
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Password'));
    
    // Check if updatePassword was called with correct data
    await waitFor(() => {
      expect(mockUpdatePassword).toHaveBeenCalledWith(
        {
          current_password: 'currentpass123',
          new_password: 'newpassword123',
          confirm_password: 'newpassword123'
        },
        expect.any(Object)
      );
    });
  });

  it('toggles password visibility when eye icon is clicked', async () => {
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Initially all password fields should be of type 'password'
    expect(screen.getByTestId('input-current_password')).toHaveAttribute('type', 'password');
    expect(screen.getByTestId('input-new_password')).toHaveAttribute('type', 'password');
    expect(screen.getByTestId('input-confirm_password')).toHaveAttribute('type', 'password');
    
    // Click on eye icons to toggle visibility
    const eyeIcons = screen.getAllByRole('button');
    
    // Toggle current password visibility
    fireEvent.click(eyeIcons[0]);
    await waitFor(() => {
      expect(screen.getByTestId('input-current_password')).toHaveAttribute('type', 'text');
    });
    
    // Toggle new password visibility
    fireEvent.click(eyeIcons[1]);
    await waitFor(() => {
      expect(screen.getByTestId('input-new_password')).toHaveAttribute('type', 'text');
    });
    
    // Toggle confirm password visibility
    fireEvent.click(eyeIcons[2]);
    await waitFor(() => {
      expect(screen.getByTestId('input-confirm_password')).toHaveAttribute('type', 'text');
    });
  });

  it('calls onSuccess callback when password update is successful', async () => {
    const { usePasswordUpdate } = require('@/lib/hooks/usePasswordUpdate');
    const mockUpdatePassword = jest.fn((data, options) => {
      if (options?.onSuccess) {
        options.onSuccess();
      }
    });
    
    (usePasswordUpdate as jest.Mock).mockReturnValue({
      mutate: mockUpdatePassword,
      isLoading: false
    });
    
    render(<PasswordChangeForm onCancel={mockOnCancel} onSuccess={mockOnSuccess} />);
    
    // Fill in the form with valid data
    await userEvent.type(screen.getByTestId('input-current_password'), 'currentpass123');
    await userEvent.type(screen.getByTestId('input-new_password'), 'newpassword123');
    await userEvent.type(screen.getByTestId('input-confirm_password'), 'newpassword123');
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Password'));
    
    // Check if onSuccess callback was called
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledTimes(1);
    });
  });
});

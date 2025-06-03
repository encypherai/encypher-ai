import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProfileForm from '../ProfileForm';
import { User } from '@/lib/services/users';

// Mock the PasswordChangeForm component
jest.mock('../PasswordChangeForm', () => {
  return function MockPasswordChangeForm({ onCancel, onSuccess }: { onCancel: () => void, onSuccess: () => void }) {
    return (
      <div data-testid="password-change-form">
        <button onClick={onCancel}>Cancel Password Change</button>
        <button onClick={onSuccess}>Complete Password Change</button>
      </div>
    );
  };
});

describe('ProfileForm', () => {
  const mockUser: User = {
    id: 1,
    email: 'test@example.com',
    first_name: 'John',
    last_name: 'Doe',
    role: 'Admin',
    department: 'Engineering',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
    last_login: '2023-05-15T10:30:00Z'
  };

  const mockOnUpdate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders user information correctly', () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Check if user information is displayed
    expect(screen.getByText(`${mockUser.first_name} ${mockUser.last_name}`)).toBeInTheDocument();
    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
    expect(screen.getByText(mockUser.department)).toBeInTheDocument();
    expect(screen.getByText(mockUser.role)).toBeInTheDocument();
    
    // Check if edit button is present
    expect(screen.getByText('Edit Profile')).toBeInTheDocument();
  });

  it('switches to edit mode when edit button is clicked', async () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Click the edit button
    fireEvent.click(screen.getByText('Edit Profile'));

    // Check if form inputs are present
    await waitFor(() => {
      expect(screen.getByLabelText('First Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Department')).toBeInTheDocument();
    });

    // Check if form inputs have correct values
    expect(screen.getByLabelText('First Name')).toHaveValue(mockUser.first_name);
    expect(screen.getByLabelText('Last Name')).toHaveValue(mockUser.last_name);
    expect(screen.getByLabelText('Email')).toHaveValue(mockUser.email);
    expect(screen.getByLabelText('Department')).toHaveValue(mockUser.department);
  });

  it('calls onUpdate with form data when form is submitted', async () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Click the edit button
    fireEvent.click(screen.getByText('Edit Profile'));

    // Update form fields
    const firstNameInput = screen.getByLabelText('First Name');
    const lastNameInput = screen.getByLabelText('Last Name');
    
    await userEvent.clear(firstNameInput);
    await userEvent.type(firstNameInput, 'Jane');
    
    await userEvent.clear(lastNameInput);
    await userEvent.type(lastNameInput, 'Smith');

    // Submit the form
    fireEvent.click(screen.getByText('Save Changes'));

    // Check if onUpdate was called with correct data
    expect(mockOnUpdate).toHaveBeenCalledWith(expect.objectContaining({
      first_name: 'Jane',
      last_name: 'Smith',
      email: mockUser.email,
      department: mockUser.department
    }));
  });

  it('cancels editing when cancel button is clicked', async () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Click the edit button
    fireEvent.click(screen.getByText('Edit Profile'));

    // Update form fields
    const firstNameInput = screen.getByLabelText('First Name');
    await userEvent.clear(firstNameInput);
    await userEvent.type(firstNameInput, 'Jane');

    // Click cancel button
    fireEvent.click(screen.getByText('Cancel'));

    // Check if we're back to view mode
    await waitFor(() => {
      expect(screen.getByText(`${mockUser.first_name} ${mockUser.last_name}`)).toBeInTheDocument();
    });

    // Check that onUpdate was not called
    expect(mockOnUpdate).not.toHaveBeenCalled();
  });

  it('shows password change form when change password button is clicked', async () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Click change password button
    fireEvent.click(screen.getByText('Change Password'));

    // Check if password change form is shown
    await waitFor(() => {
      expect(screen.getByTestId('password-change-form')).toBeInTheDocument();
    });
  });

  it('hides password change form when cancel is clicked', async () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={false}
        onUpdate={mockOnUpdate}
      />
    );

    // Click change password button
    fireEvent.click(screen.getByText('Change Password'));

    // Click cancel button in password change form
    fireEvent.click(screen.getByText('Cancel Password Change'));

    // Check if password change form is hidden
    await waitFor(() => {
      expect(screen.queryByTestId('password-change-form')).not.toBeInTheDocument();
    });
  });

  it('disables buttons when isUpdating is true', () => {
    render(
      <ProfileForm 
        user={mockUser}
        isUpdating={true}
        onUpdate={mockOnUpdate}
      />
    );

    // Click the edit button
    fireEvent.click(screen.getByText('Edit Profile'));

    // Check if buttons are disabled
    expect(screen.getByText('Cancel')).toBeDisabled();
    expect(screen.getByText('Save Changes')).toBeDisabled();
  });
});

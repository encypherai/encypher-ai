import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserOnboardingWizard } from './UserOnboardingWizard';
import { SessionProvider } from 'next-auth/react';
import type { Session } from 'next-auth';

// Mock fetchApi
jest.mock('@/lib/api', () => ({
  fetchApi: jest.fn(() => Promise.resolve({}))
}));

const mockSession: Session = {
  user: {
    id: '1',
    email: 'test@example.com',
    role: 'User',
    isActive: true,
    org_id: undefined,
    organization_uuid: undefined,
    // For test: add custom fields as needed for onboarding, but only known props for type
  },
  accessToken: 'mock-token',
  expires: new Date('2099-01-01T00:00:00.000Z'),
};

function renderWizard() {
  return render(
    <SessionProvider session={mockSession}>
      <UserOnboardingWizard />
    </SessionProvider>
  );
}

describe('UserOnboardingWizard', () => {
  it('renders user info step and validates input', async () => {
    renderWizard();
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/required/);
  });

  it('renders org step and validates revenue tier', async () => {
    // Simulate user info already completed
    renderWizard();
    fireEvent.change(screen.getByLabelText(/First Name/i), { target: { value: 'Test' } });
    fireEvent.change(screen.getByLabelText(/Last Name/i), { target: { value: 'User' } });
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    await waitFor(() => expect(screen.getByLabelText(/Organization Name/i)).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText(/Organization Name/i), { target: { value: 'Test Org' } });
    fireEvent.click(screen.getByRole('button', { name: /Finish/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/Revenue tier is required/);
    fireEvent.change(screen.getByLabelText(/Revenue Tier/i), { target: { value: 'growth' } });
    fireEvent.click(screen.getByRole('button', { name: /Finish/i }));
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
  });
});

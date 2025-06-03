import React from 'react';
import { render, screen } from '@testing-library/react';
import ProfileFormSkeleton from '../ProfileFormSkeleton';

// Mock the Card component
jest.mock('@/components/ui/Card', () => {
  return function MockCard({ children, title }: { children: React.ReactNode, title?: string }) {
    return (
      <div data-testid="card">
        {title && <h2>{title}</h2>}
        {children}
      </div>
    );
  };
});

describe('ProfileFormSkeleton', () => {
  it('renders the skeleton component with default props', () => {
    render(<ProfileFormSkeleton />);
    
    // Check if card is rendered
    expect(screen.getByTestId('card')).toBeInTheDocument();
    
    // Check if title is rendered
    expect(screen.getByText('Profile Information')).toBeInTheDocument();
    
    // Check if skeleton elements are rendered
    // We can't check for specific skeleton elements directly since they're just divs with classes
    // But we can check for the wrapper div that contains them
    const skeletonContainer = screen.getByTestId('card').querySelector('.space-y-6');
    expect(skeletonContainer).toBeInTheDocument();
  });

  it('renders with custom title when provided', () => {
    const customTitle = 'Custom Profile Title';
    render(<ProfileFormSkeleton title={customTitle} />);
    
    expect(screen.getByText(customTitle)).toBeInTheDocument();
  });

  it('renders the correct number of skeleton fields', () => {
    render(<ProfileFormSkeleton />);
    
    // The component should render profile info section and form fields
    const profileInfoSection = screen.getByTestId('card');
    
    // Check for avatar skeleton
    const avatarSkeleton = profileInfoSection.querySelector('.rounded-full');
    expect(avatarSkeleton).toBeInTheDocument();
    
    // Check for form field skeletons (name, email, department, role)
    const formFieldSkeletons = profileInfoSection.querySelectorAll('.h-4');
    // We should have multiple skeleton lines for the form fields
    expect(formFieldSkeletons.length).toBeGreaterThan(3);
  });

  it('renders skeleton buttons at the bottom', () => {
    render(<ProfileFormSkeleton />);
    
    const buttonContainer = screen.getByTestId('card').querySelector('.flex.justify-between.mt-6');
    expect(buttonContainer).toBeInTheDocument();
    
    // Check for button skeletons
    const buttonSkeletons = buttonContainer?.querySelectorAll('.h-10');
    expect(buttonSkeletons?.length).toBeGreaterThan(0);
  });
});

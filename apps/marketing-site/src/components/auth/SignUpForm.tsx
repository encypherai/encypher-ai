import React, { useMemo } from 'react';
import { Input } from '@encypher/design-system';
import { Label } from '@encypher/design-system';
import zxcvbn from 'zxcvbn';

/**
 * SignUpForm Component
 *
 * Accessible, modular sign-up form for new user registration.
 *
 * Props:
 * - onSignUp: (email, password, confirm, orgName?) => Promise<void> - called on form submit
 * - loading: boolean - disables form and shows loading state
 * - error: string | null - error message to display
 * - email: string - current email input value
 * - setEmail: (email) => void - update email input
 * - password: string - current password input value
 * - setPassword: (password) => void - update password input
 * - confirm: string - current confirm password input value
 * - setConfirm: (confirm) => void - update confirm input
 * - orgName?: string - current organization name input value
 * - setOrgName?: (orgName) => void - update organization name input
 * - requireOrgName?: boolean - whether to show organization name field
 *
 * Accessibility:
 * - Uses ARIA roles and aria-live for error feedback
 * - Password strength meter is screen-reader friendly
 * - Keyboard/focus accessible
 */
interface SignUpFormProps {
  /**
   * Called when the form is submitted with email, password, confirm password, and organization name (if required).
   */
  onSignUp: (email: string, password: string, confirm: string, orgName?: string) => Promise<void>;
  /**
   * Disables the form and shows a loading state.
   */
  loading: boolean;
  /**
   * Error message to display to the user.
   */
  error: string | null;
  /**
   * Current email input value.
   */
  email: string;
  /**
   * Updates the email input value.
   */
  setEmail: (email: string) => void;
  /**
   * Current password input value.
   */
  password: string;
  /**
   * Updates the password input value.
   */
  setPassword: (password: string) => void;
  /**
   * Current confirm password input value.
   */
  confirm: string;
  /**
   * Updates the confirm password input value.
   */
  setConfirm: (confirm: string) => void;
  /**
   * Current organization name input value.
   */
  orgName?: string;
  /**
   * Updates the organization name input value.
   */
  setOrgName?: (orgName: string) => void;
  /**
   * Whether to show the organization name field.
   */
  requireOrgName?: boolean;
}

export const SignUpForm: React.FC<SignUpFormProps> = ({
  onSignUp,
  loading,
  error,
  email,
  setEmail,
  password,
  setPassword,
  confirm,
  setConfirm,
  orgName = '',
  setOrgName,
  requireOrgName = false,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSignUp(email, password, confirm, requireOrgName ? orgName : undefined);
  };

  // Password strength calculation
  const strength = useMemo(() => zxcvbn(password), [password]);
  const strengthLabels = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-600'];

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit} autoComplete="on" aria-label="Sign up form">
      <div>
        <Label htmlFor="signup-email">Email</Label>
        <Input
          id="signup-email"
          type="email"
          autoComplete="email"
          placeholder="Your email address"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          className="mt-1"
          aria-required="true"
        />
      </div>
      {requireOrgName && setOrgName && (
        <div>
          <Label htmlFor="signup-org">Organization Name</Label>
          <Input
            id="signup-org"
            type="text"
            autoComplete="organization"
            placeholder="Your organization name"
            value={orgName}
            onChange={e => setOrgName(e.target.value)}
            required
            className="mt-1"
            aria-required="true"
          />
        </div>
      )}
      <div>
        <Label htmlFor="signup-password">Password</Label>
        <Input
          id="signup-password"
          type="password"
          autoComplete="new-password"
          placeholder="Create a password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          className="mt-1"
          aria-required="true"
        />
        {password && (
          <div className="mt-2 flex items-center gap-2" aria-live="polite" aria-atomic="true">
            <div className={`h-2 w-24 rounded ${strengthColors[strength.score]}`}></div>
            <span className="text-xs text-muted-foreground">{strengthLabels[strength.score]}</span>
          </div>
        )}
      </div>
      <div>
        <Label htmlFor="signup-confirm">Confirm Password</Label>
        <Input
          id="signup-confirm"
          type="password"
          autoComplete="new-password"
          placeholder="Confirm your password"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          required
          className="mt-1"
          aria-required="true"
        />
      </div>
      {error && <div className="text-destructive text-sm" role="alert" aria-live="assertive">{error}</div>}
      <button
        type="submit"
        className="w-full py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-ring
          bg-primary text-primary-foreground hover:bg-primary/90 border border-primary shadow-sm mt-2 disabled:opacity-70"
        disabled={loading}
        aria-busy={loading}
      >
        {loading ? 'Signing up...' : 'Sign up'}
      </button>
    </form>
  );
};

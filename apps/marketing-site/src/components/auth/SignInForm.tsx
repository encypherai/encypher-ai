import React from 'react';
import { Input } from '@encypher/design-system';
import { Label } from '@encypher/design-system';

/**
 * SignInForm Component
 *
 * Accessible, modular sign-in form for user authentication.
 *
 * Props:
 * - onSignIn: (email, password) => Promise<void> - called on form submit
 * - loading: boolean - disables form and shows loading state
 * - error: string | null - error message to display
 * - email: string - current email input value
 * - setEmail: (email) => void - update email input
 * - password: string - current password input value
 * - setPassword: (password) => void - update password input
 *
 * Accessibility:
 * - Uses ARIA roles and aria-live for error feedback
 * - Keyboard/focus accessible
 */
interface SignInFormProps {
  /**
   * Called when the form is submitted with email and password.
   */
  onSignIn: (email: string, password: string) => Promise<void>;
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
}

/**
 * Accessible, modular sign-in form for user authentication.
 */
export const SignInForm: React.FC<SignInFormProps> = ({
  onSignIn,
  loading,
  error,
  email,
  setEmail,
  password,
  setPassword,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSignIn(email, password);
  };

  return (
    <form className="flex flex-col gap-4" onSubmit={handleSubmit} autoComplete="on" aria-label="Sign in form">
      <div>
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
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
      <div>
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          placeholder="Your password"
          value={password}
          onChange={e => setPassword(e.target.value)}
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
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  );
};

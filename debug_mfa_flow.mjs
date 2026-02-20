import fetch from "node-fetch";

// The error shows:
// encyclpher-dashboard | [NextAuth] Attempting login to: http://traefik:8000/api/v1/auth/login
// encyclpher-dashboard | [NextAuth] Stale MFA challenge detected; retrying primary login flow
// ...
// encyclpher-dashboard | [NextAuth] Login failed - invalid credentials

// Wait, the logs in the screenshot text say:
// encypher-dashboard | [NextAuth] Stale MFA challenge detected; retrying primary login flow

// That means `mfaErrorMessage === 'Invalid or expired MFA challenge'` happened.
// Why did that happen? Because the backend returned that error for `/auth/login/mfa/complete`.
// WHY did the backend return that? Because the `mfaToken` was expired, OR it was invalid.
// Since the frontend just got it, it shouldn't be expired.
// Let's check what the backend actually returns.

import fs from 'fs';
const file = 'apps/dashboard/src/app/login/page.tsx';
let content = fs.readFileSync(file, 'utf8');

// The error happens when:
// 1. `mfaToken` and `mfaCode` are provided to `signIn`.
// 2. The `/auth/login/mfa/complete` endpoint returns an error, e.g. 401 "Invalid multi-factor authentication code".
// 3. BUT NextAuth code says:
//      const mfaErrorMessage = mfaData.detail || mfaData.error?.message || 'Invalid multi-factor authentication code';
//      if (mfaErrorMessage === 'Invalid or expired MFA challenge') { ... } 
//      else { throw new Error(mfaErrorMessage); }
// 4. So `signIn` throws an error "Invalid multi-factor authentication code".
// 5. In `page.tsx`, we have:
//      setError(result.error === 'CredentialsSignin' ? 'Invalid email or password' : result.error);
// 6. Wait! So why does it show "Invalid email or password"?
// Oh wait. If NextAuth throws an error, NextAuth's `authorize` catch block catches it:
//      } catch (error) {
//        console.error('[NextAuth] Auth error:', error);
//        if (error instanceof Error) {
//          throw error;
//        }
//        throw new Error('An error occurred during login. Please try again.');
//      }
// AND THEN NextAuth's internal `CredentialsProvider` catches the error thrown from `authorize` and DOES NOT expose the custom error string properly if it's not handled correctly?
// Wait, we ALREADY established earlier that NextAuth URL-encodes custom errors in `result.error`.
// So `result.error` will be `Invalid%20multi-factor%20authentication%20code`.
// Wait. Is that what's happening? Let's check `page.tsx` again.

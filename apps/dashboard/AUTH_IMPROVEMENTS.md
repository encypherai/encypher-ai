# Dashboard Authentication Improvements

## Changes Made

### 1. Extended Session Token Duration
**Files**: `services/auth-service/app/core/config.py`, `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`

- **Access Token**: Increased from 60 minutes to 480 minutes (8 hours)
- **Refresh Token**: Increased from 14 days to 30 days

**Rationale**: Reduces session expiry interruptions while maintaining security. Users can work for a full day without re-authentication.

### 2. Created Reusable Auth Guard Hook
**File**: `apps/dashboard/src/hooks/useRequireAuth.ts`

A centralized hook that:
- Checks authentication status on component mount
- Redirects to login if unauthenticated
- Preserves the intended destination URL for post-login redirect
- Returns session data, loading state, and access token

**Usage**:
```typescript
const { session, status, accessToken, isLoading, isAuthenticated } = useRequireAuth();
```

### 3. Applied Auth Guard to Protected Pages
**Updated Pages**:
- ✅ `/` - Dashboard home
- ✅ `/playground` - API playground
- 🔄 `/settings` - User settings (needs update)
- 🔄 `/api-keys` - API key management (needs update)
- 🔄 `/billing` - Billing & subscriptions (needs update)
- 🔄 `/analytics` - Analytics dashboard (needs update)
- 🔄 `/team` - Team management (needs update)
- 🔄 `/admin` - Admin panel (needs update)
- 🔄 `/webhooks` - Webhook management (needs update)
- 🔄 `/audit-logs` - Audit logs (needs update)

### 4. Global Session Expiry Handling
**Files**: `apps/dashboard/src/components/providers.tsx`, `apps/dashboard/src/middleware.ts`

Already implemented:
- React Query error handler detects session expiry (401 errors)
- Distinguishes between session expiry and permission errors
- Automatically logs out and redirects to login on true session expiry
- Middleware immediately redirects sessions already marked with `RefreshAccessTokenError`
- Middleware rejects non-refreshable expired legacy sessions

### 5. Unified Backend Session Lifecycle
**Files**: `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`, `services/auth-service/app/api/v1/endpoints.py`

The dashboard now treats auth-service as the session authority:

- NextAuth stores backend-issued `accessToken`, `refreshToken`, `accessTokenExpires`, `role`, `tier`, and `name`
- Silent refresh rotates refresh tokens via `POST /auth/refresh`
- Refresh responses update canonical user metadata from backend truth
- OAuth logins now persist backend refresh tokens instead of access-token-only sessions
- Email verification auto-login and passkey login also bootstrap refresh-capable sessions
- NextAuth `signOut` revokes backend refresh state via `POST /auth/logout`

### 6. Periodic Backend Session Verification
**File**: `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`

- Still-valid backend access tokens are re-verified on the normal session polling/window-focus cycle
- If backend verification fails, the dashboard attempts a refresh fallback once
- If refresh fails, the session is marked expired and the user is redirected to login

This balances security and UX by avoiding a backend call on every navigation while still detecting revoked sessions promptly.

### 7. Local Dashboard Dev Stability
**Files**: `apps/dashboard/Dockerfile.dev`, `docker-compose.full-stack.yml`

- The dashboard dev container now clears `/app/.next` on boot before starting `next dev`
- The persistent dashboard `.next` compose volume was removed to avoid stale `routes-manifest.json` corruption
- Recreated dashboard containers now rebuild the Next.js dev artifacts cleanly

## Benefits

1. **Consistent Auth Checks**: All protected pages use the same authentication logic
2. **Better UX**: Silent refresh and periodic verification reduce interruptions without hiding invalid sessions
3. **Automatic Redirects**: Users are automatically sent to login when refresh or verification fails
4. **Preserved Navigation**: Post-login redirect returns users to their intended page
5. **Backend-Backed Session Truth**: Refresh token rotation and logout revocation are controlled by auth-service

## Testing

1. **Session Duration**: Verify 8-hour sessions work correctly
2. **Auto-Redirect**: Visit protected page while logged out → should redirect to login
3. **Post-Login Return**: After login, should return to original destination
4. **Session Expiry**: After 8 hours, should refresh automatically when refresh token is valid
5. **Session Revocation**: Revoked sessions should fail verification and redirect to login on the next session poll/focus cycle
6. **OAuth Persistence**: OAuth login should receive refresh-capable backend sessions
7. **Verify Email / Passkey**: Token-bootstrap logins should persist and refresh like credential logins

## Security Considerations

- 8-hour access tokens are acceptable for B2B SaaS with proper refresh token rotation
- Refresh tokens are stored securely and can be revoked
- Session verification plus refresh fallback detects revoked sessions without a backend round-trip on every navigation
- All API calls still validate tokens server-side

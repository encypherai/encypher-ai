# Dashboard Authentication Improvements

## Changes Made

### 1. Extended Session Token Duration
**File**: `services/auth-service/app/core/config.py`

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
**File**: `apps/dashboard/src/components/providers.tsx`

Already implemented:
- React Query error handler detects session expiry (401 errors)
- Distinguishes between session expiry and permission errors
- Automatically logs out and redirects to login on true session expiry
- Session refetch every 5 minutes to detect backend token expiration

## Benefits

1. **Consistent Auth Checks**: All protected pages use the same authentication logic
2. **Better UX**: Longer sessions reduce interruptions
3. **Automatic Redirects**: Users are automatically sent to login when needed
4. **Preserved Navigation**: Post-login redirect returns users to their intended page
5. **Centralized Logic**: Single source of truth for auth requirements

## Remaining Work

Apply `useRequireAuth` to remaining protected pages:
- Settings, API Keys, Billing, Analytics, Team, Admin, Webhooks, Audit Logs

## Testing

1. **Session Duration**: Verify 8-hour sessions work correctly
2. **Auto-Redirect**: Visit protected page while logged out → should redirect to login
3. **Post-Login Return**: After login, should return to original destination
4. **Session Expiry**: After 8 hours, should detect expiry and redirect to login
5. **Refresh Token**: Should automatically refresh access token using refresh token

## Security Considerations

- 8-hour access tokens are acceptable for B2B SaaS with proper refresh token rotation
- Refresh tokens are stored securely and can be revoked
- Session expiry detection prevents use of expired tokens
- All API calls still validate tokens server-side

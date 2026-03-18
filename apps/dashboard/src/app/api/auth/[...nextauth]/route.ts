import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';

if (process.env.NODE_ENV === 'production' && !process.env.NEXTAUTH_SECRET) {
  throw new Error(
    'NEXTAUTH_SECRET must be set in production. Without a stable secret, ' +
    'all user sessions are invalidated on every deploy.'
  );
}

// Server-side API base: prefer Docker-internal URL over public URL for server-side fetches
const API_BASE =
  (process.env.API_BASE_INTERNAL || process.env.API_BASE || process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

// Backend access token lifetime (8 hours), refresh 5 min before expiry
const ACCESS_TOKEN_TTL_MS = 8 * 60 * 60 * 1000;
const REFRESH_BUFFER_MS = 5 * 60 * 1000;
const SESSION_VERIFICATION_INTERVAL_MS = 60 * 60 * 1000;

type BackendUser = {
  id?: string;
  email?: string;
  name?: string;
  role?: string;
  account_type?: string;
  permission?: string;
  tier?: string;
  subscription_tier?: string;
  plan?: string;
};

type RefreshedBackendSession = {
  accessToken: string;
  refreshToken: string;
  accessTokenExpires: number;
  user?: BackendUser;
};

function mapBackendUser(user: BackendUser | undefined) {
  return {
    id: user?.id ? String(user.id) : undefined,
    email: user?.email,
    name: user?.name,
    role: user?.role ?? user?.account_type ?? user?.permission ?? 'member',
    tier: user?.tier ?? user?.subscription_tier ?? user?.plan ?? 'free',
  };
}

type RefreshResult =
  | { ok: true; data: RefreshedBackendSession }
  | { ok: false; reason: string };

async function refreshBackendToken(refreshToken: string): Promise<RefreshResult> {
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) {
      const reason = `HTTP ${res.status}`;
      console.warn('[NextAuth] Token refresh failed:', reason);
      return { ok: false, reason };
    }
    const data = await res.json();
    if (data.success && data.data?.access_token) {
      return {
        ok: true,
        data: {
          accessToken: data.data.access_token,
          refreshToken: data.data.refresh_token,
          accessTokenExpires: Date.now() + ACCESS_TOKEN_TTL_MS - REFRESH_BUFFER_MS,
          user: data.data.user,
        },
      };
    }
    const reason = data.error?.message || data.detail || 'Unexpected response shape';
    console.warn('[NextAuth] Token refresh: unexpected response -', reason);
    return { ok: false, reason };
  } catch (err) {
    const reason = err instanceof Error ? err.message : String(err);
    console.error('[NextAuth] Token refresh error:', reason);
    return { ok: false, reason };
  }
}

async function verifyBackendAccessToken(accessToken: string): Promise<BackendUser | null> {
  try {
    const res = await fetch(`${API_BASE}/auth/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!res.ok) {
      return null;
    }

    const data = await res.json();
    if (data.success && data.data) {
      return data.data as BackendUser;
    }

    return null;
  } catch (error) {
    console.warn('[NextAuth] Backend session verify failed:', error);
    return null;
  }
}

// Shape returned from each authorize sub-handler (matches NextAuth User fields + extensions).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AuthorizeResult = any;

// Shared helper: build the user object returned from a successful login.
function buildAuthorizedUser(
  user: BackendUser & { id?: string | number },
  accessToken: string,
  refreshToken: string | undefined,
): AuthorizeResult {
  return {
    id: String(user.id),
    email: user.email,
    name: user.name,
    accessToken,
    refreshToken,
    accessTokenExpires: Date.now() + ACCESS_TOKEN_TTL_MS - REFRESH_BUFFER_MS,
    role: user.role ?? user.account_type ?? user.permission ?? 'member',
    tier: user.tier ?? user.subscription_tier ?? user.plan ?? 'free',
  };
}

// Sub-handler: token-based login (email verification flow).
// The password field carries the access token prefixed with '__TOKEN__'.
async function authorizeWithToken(
  email: string,
  accessToken: string,
  refreshToken: string | undefined,
): Promise<AuthorizeResult> {
  console.log('[NextAuth] Token-based login for:', email);
  const verifyRes = await fetch(`${API_BASE}/auth/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!verifyRes.ok) {
    console.log('[NextAuth] Token verification failed (HTTP', verifyRes.status, '), redirecting to manual login');
    throw new Error('Session expired. Please log in with your credentials.');
  }

  const verifyData = await verifyRes.json();
  if (verifyData.success && verifyData.data) {
    console.log('[NextAuth] Token verification successful for:', verifyData.data.email);
    return buildAuthorizedUser(verifyData.data, accessToken, refreshToken);
  }

  console.log('[NextAuth] Token verification failed: unexpected response');
  throw new Error('Session expired. Please log in with your credentials.');
}

// Sub-handler: MFA completion flow.
// Returns the authorized user on success, or { staleMfaChallenge: true } if the challenge expired.
type MfaResult =
  | { user: AuthorizeResult }
  | { staleMfaChallenge: true };

async function authorizeWithMfa(mfaToken: string, mfaCode: string): Promise<MfaResult> {
  const mfaRes = await fetch(`${API_BASE}/auth/login/mfa/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mfa_token: mfaToken, mfa_code: mfaCode }),
  });
  const mfaData = await mfaRes.json();

  if (mfaRes.ok && mfaData.success) {
    return { user: buildAuthorizedUser(mfaData.data.user, mfaData.data.access_token, mfaData.data.refresh_token) };
  }

  const mfaErrorMessage = mfaData.detail || mfaData.error?.message || 'Invalid multi-factor authentication code';
  if (mfaErrorMessage === 'Invalid or expired MFA challenge') {
    console.warn('[NextAuth] Stale MFA challenge detected; retrying primary login flow');
    return { staleMfaChallenge: true };
  }

  throw new Error(mfaErrorMessage);
}

// Sub-handler: standard credential login (email + password).
// Also handles MFA-required redirect and HTTP error shaping.
async function authorizeWithCredentials(
  email: string,
  password: string,
  mfaCode: string | undefined,
  turnstileToken: string | undefined,
): Promise<AuthorizeResult> {
  console.log('[NextAuth] Attempting login to:', `${API_BASE}/auth/login`);
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      mfa_code: mfaCode || undefined,
      turnstile_token: turnstileToken || undefined,
    }),
  });

  const data = await res.json();
  console.log('[NextAuth] API response status:', res.status, 'success:', data.success);

  if (res.status === 401) {
    const errorDetail = data?.detail || data?.error?.message;
    console.log('[NextAuth] Login failed - unauthorized:', errorDetail || 'Invalid credentials');
    throw new Error(errorDetail || 'Invalid email or password');
  }

  if (res.status === 403) {
    console.log('[NextAuth] Login failed - account not verified');
    throw new Error('Please verify your email before signing in');
  }

  if (!res.ok) {
    console.log('[NextAuth] Login failed - server error:', res.status);
    throw new Error(data.error?.message || data.detail || 'Login failed. Please try again.');
  }

  if (data.success && data.data?.mfa_required && data.data?.mfa_token) {
    throw new Error(`MFA_REQUIRED:${data.data.mfa_token}`);
  }

  if (data.success && data.data?.user && data.data?.access_token) {
    console.log('[NextAuth] Login successful for user:', data.data.user.email);
    return buildAuthorizedUser(data.data.user, data.data.access_token, data.data.refresh_token);
  }

  console.log('[NextAuth] Login failed - invalid response structure');
  throw new Error('Login failed. Please try again.');
}

const handler = NextAuth({
  providers: [
    // Email/Password Authentication
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email", placeholder: "you@example.com" },
        password: { label: "Password", type: "password" },
        refreshToken: { label: "Refresh Token", type: "text" },
        mfaCode: { label: "MFA Code", type: "text" },
        mfaToken: { label: "MFA Token", type: "text" },
        turnstileToken: { label: "Turnstile Token", type: "text" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          console.log('[NextAuth] Missing credentials');
          throw new Error('Please enter both email and password. Navigate to /login if you need to reset your password.');
        }

        try {
          // Token-based login: password field carries a pre-issued access token.
          if (credentials.password.startsWith('__TOKEN__')) {
            const accessToken = credentials.password.replace('__TOKEN__', '');
            return await authorizeWithToken(credentials.email, accessToken, credentials.refreshToken);
          }

          // MFA completion flow: client supplies both token and code.
          if (credentials.mfaToken && credentials.mfaCode) {
            const mfaResult = await authorizeWithMfa(credentials.mfaToken, credentials.mfaCode);
            if ('user' in mfaResult) {
              return mfaResult.user;
            }
            // Stale challenge: fall through to fresh credential login without the stale MFA code.
          }

          // Standard credential login (also handles fresh MFA challenge after stale one).
          const mfaCode = (credentials.mfaToken && credentials.mfaCode) ? undefined : credentials.mfaCode;
          return await authorizeWithCredentials(
            credentials.email,
            credentials.password,
            mfaCode,
            credentials.turnstileToken,
          );
        } catch (error) {
          console.error('[NextAuth] Auth error:', error);
          if (error instanceof Error) {
            throw error;
          }
          throw new Error('An error occurred during login. Please try again.');
        }
      }
    }),

    // Google OAuth
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code"
        }
      }
    }),

    // GitHub OAuth
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID || '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
    }),
  ],
  pages: {
    signIn: '/login',
    signOut: '/login',
    error: '/login',
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id as string | undefined;
        token.email = (user.email ?? undefined) as string | undefined;
        // propagate access token and role metadata if present from credentials
        // @ts-expect-error - extending user type
        if (user.accessToken) token.accessToken = user.accessToken as string;
        // @ts-expect-error - extending user type
        if (user.refreshToken) token.refreshToken = user.refreshToken as string;
        // @ts-expect-error - extending user type
        if (user.accessTokenExpires) token.accessTokenExpires = user.accessTokenExpires as number;
        token.backendVerifiedAt = Date.now();
        if (user.name) token.name = user.name as string;
        // @ts-expect-error - extending user type
        if (user.role) token.role = user.role as string;
        // @ts-expect-error - extending user type
        if (user.tier) token.tier = user.tier as string;

        // For OAuth logins, exchange provider tokens for internal access token
        if (account && (account.provider === 'google' || account.provider === 'github')) {
          try {
            console.log('[NextAuth] Exchanging OAuth token for internal access token');
            const exchangeRes = await fetch(`${API_BASE}/auth/oauth/exchange`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                provider: account.provider,
                id_token: account.id_token,
                access_token: account.access_token,
              }),
            });

            if (exchangeRes.ok) {
              const exchangeData = await exchangeRes.json();
              if (exchangeData.success && exchangeData.data?.access_token) {
                const mappedUser = mapBackendUser(exchangeData.data.user);
                token.accessToken = exchangeData.data.access_token;
                token.refreshToken = exchangeData.data.refresh_token;
                token.accessTokenExpires = Date.now() + ACCESS_TOKEN_TTL_MS - REFRESH_BUFFER_MS;
                token.id = mappedUser.id ?? token.id;
                token.email = mappedUser.email ?? token.email;
                token.name = mappedUser.name ?? token.name;
                token.role = mappedUser.role;
                token.tier = mappedUser.tier;
                console.log('[NextAuth] OAuth token exchange successful');
              }
            } else {
              console.warn('[NextAuth] OAuth token exchange failed:', await exchangeRes.text());
            }
          } catch (error) {
            console.error('[NextAuth] OAuth token exchange error:', error);
          }
        }
        return token;
      }

      // Access token still valid - return as-is
      if (token.accessTokenExpires && Date.now() < (token.accessTokenExpires as number)) {
        const shouldReverify =
          token.accessToken &&
          (!token.backendVerifiedAt || Date.now() - (token.backendVerifiedAt as number) >= SESSION_VERIFICATION_INTERVAL_MS);

        if (!shouldReverify) {
          return token;
        }

        const verifiedUser = await verifyBackendAccessToken(token.accessToken as string);
        if (verifiedUser) {
          const mappedUser = mapBackendUser(verifiedUser);
          return {
            ...token,
            id: mappedUser.id ?? token.id,
            email: mappedUser.email ?? token.email,
            name: mappedUser.name ?? token.name,
            role: mappedUser.role ?? token.role,
            tier: mappedUser.tier ?? token.tier,
            backendVerifiedAt: Date.now(),
            error: undefined,
          };
        }

        if (token.refreshToken) {
          console.warn('[NextAuth] Backend session verify failed, attempting refresh fallback');
          const refreshResult = await refreshBackendToken(token.refreshToken as string);
          if (refreshResult.ok) {
            const refreshed = refreshResult.data;
            const mappedUser = mapBackendUser(refreshed.user);
            return {
              ...token,
              accessToken: refreshed.accessToken,
              refreshToken: refreshed.refreshToken,
              accessTokenExpires: refreshed.accessTokenExpires,
              id: mappedUser.id ?? token.id,
              email: mappedUser.email ?? token.email,
              name: mappedUser.name ?? token.name,
              role: mappedUser.role ?? token.role,
              tier: mappedUser.tier ?? token.tier,
              backendVerifiedAt: Date.now(),
              error: undefined,
            };
          }

          console.warn('[NextAuth] Backend session verify refresh fallback failed:', refreshResult.reason, '- keeping current valid access token until expiry');
          return {
            ...token,
            backendVerifiedAt: Date.now(),
            error: undefined,
          };
        }

        console.warn('[NextAuth] Backend session verify failed without refresh token; keeping current valid access token until expiry');
        return {
          ...token,
          backendVerifiedAt: Date.now(),
          error: undefined,
        };
      }

      // Access token expired (or no expiry recorded for legacy sessions) - attempt silent refresh
      if (token.refreshToken) {
        console.log('[NextAuth] Access token expired, attempting silent refresh');
        const refreshResult = await refreshBackendToken(token.refreshToken as string);
        if (refreshResult.ok) {
          console.log('[NextAuth] Silent token refresh successful');
          const refreshed = refreshResult.data;
          const mappedUser = mapBackendUser(refreshed.user);
          return {
            ...token,
            accessToken: refreshed.accessToken,
            refreshToken: refreshed.refreshToken,
            accessTokenExpires: refreshed.accessTokenExpires,
            backendVerifiedAt: Date.now(),
            id: mappedUser.id ?? token.id,
            email: mappedUser.email ?? token.email,
            name: mappedUser.name ?? token.name,
            role: mappedUser.role ?? token.role,
            tier: mappedUser.tier ?? token.tier,
            error: undefined,
          };
        }
        console.warn('[NextAuth] Silent token refresh failed:', refreshResult.reason, '- marking session for logout');
        return { ...token, error: `RefreshAccessTokenError: ${refreshResult.reason}` };
      }

      // Legacy sessions without refresh tokens are allowed to continue until they naturally expire.
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        session.user.name = token.name as string | undefined;
        // expose accessToken in session for API calls if needed
        (session.user as Record<string, unknown>).accessToken = token.accessToken as string | undefined;
        (session.user as Record<string, unknown>).refreshToken = token.refreshToken as string | undefined;
        (session.user as Record<string, unknown>).role = token.role as string | undefined;
        (session.user as Record<string, unknown>).tier = token.tier as string | undefined;
        // propagate any token error (e.g. 'RefreshAccessTokenError') so the client can react
        (session.user as Record<string, unknown>).error = token.error as string | undefined;
      }
      return session;
    },
  },
  events: {
    async signOut(message) {
      const refreshToken = 'token' in message ? message.token?.refreshToken : undefined;
      if (!refreshToken) {
        return;
      }

      try {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (error) {
        console.warn('[NextAuth] Failed to revoke backend refresh token during sign-out:', error);
      }
    },
  },
  session: {
    strategy: 'jwt',
    // 30-day session lifetime matches refresh token lifetime.
    // The backend access token (8h) is silently refreshed by the JWT callback,
    // so users stay logged in as long as they're active within the refresh token window.
    maxAge: 30 * 24 * 60 * 60, // 30 days
    updateAge: 24 * 60 * 60,   // Roll the session cookie once per day of activity
  },
  cookies: {
    sessionToken: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.session-token' : 'next-auth.session-token',
      options: {
        // Only set domain if NEXTAUTH_COOKIE_DOMAIN is explicitly set (for cross-subdomain auth)
        ...(process.env.NEXTAUTH_COOKIE_DOMAIN && { domain: process.env.NEXTAUTH_COOKIE_DOMAIN }),
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
    callbackUrl: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.callback-url' : 'next-auth.callback-url',
      options: {
        ...(process.env.NEXTAUTH_COOKIE_DOMAIN && { domain: process.env.NEXTAUTH_COOKIE_DOMAIN }),
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
    csrfToken: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.csrf-token' : 'next-auth.csrf-token',
      options: {
        ...(process.env.NEXTAUTH_COOKIE_DOMAIN && { domain: process.env.NEXTAUTH_COOKIE_DOMAIN }),
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };

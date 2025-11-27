import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';

const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL || 'https://api.encypherai.com/api/v1').replace(/\/$/, '');

// Validate required environment variables
if (!process.env.NEXTAUTH_SECRET) {
  console.error('[NextAuth] NEXTAUTH_SECRET is not set!');
}

const handler = NextAuth({
  providers: [
    // Email/Password Authentication
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email", placeholder: "you@example.com" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Call API Gateway auth login (SRF)
          const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });

          const data = await res.json();

          if (res.ok && data.success && data.data?.user && data.data?.access_token) {
            const user = data.data.user;
            return {
              id: String(user.id),
              email: user.email,
              name: user.name,
              accessToken: data.data.access_token,
              role: user.role ?? user.account_type ?? user.permission ?? 'member',
              tier: user.tier ?? user.subscription_tier ?? user.plan ?? 'free',
            } as any;
          }
          
          return null;
        } catch (error) {
          console.error('Auth error:', error);
          return null;
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
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id as string | undefined;
        token.email = (user.email ?? undefined) as string | undefined;
        // propagate access token and role metadata if present from credentials
        // @ts-expect-error - extending user type
        if (user.accessToken) token.accessToken = user.accessToken as string;
        // @ts-expect-error - extending user type
        if (user.role) token.role = user.role as string;
        // @ts-expect-error - extending user type
        if (user.tier) token.tier = user.tier as string;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        // expose accessToken in session for API calls if needed
        (session.user as Record<string, unknown>).accessToken = token.accessToken as string | undefined;
        (session.user as Record<string, unknown>).role = token.role as string | undefined;
        (session.user as Record<string, unknown>).tier = token.tier as string | undefined;
      }
      return session;
    },
  },
  session: {
    strategy: 'jwt',
  },
  // Cookie configuration for cross-subdomain auth
  // Set NEXTAUTH_COOKIE_DOMAIN to enable SSO across subdomains:
  // - Railway staging: .up.railway.app
  // - Production: .encypherai.com
  // - Local dev: leave unset (cookies scoped to localhost)
  cookies: (() => {
    const cookieDomain = process.env.NEXTAUTH_COOKIE_DOMAIN;
    if (!cookieDomain) return undefined;
    
    // Use secure cookies when domain is set (assumes HTTPS in staging/production)
    const isSecure = !!cookieDomain;
    const cookiePrefix = isSecure ? '__Secure-' : '';
    
    return {
      sessionToken: {
        name: `${cookiePrefix}next-auth.session-token`,
        options: {
          domain: cookieDomain,
          httpOnly: true,
          sameSite: 'lax' as const,
          path: '/',
          secure: isSecure,
        },
      },
      callbackUrl: {
        name: `${cookiePrefix}next-auth.callback-url`,
        options: {
          domain: cookieDomain,
          httpOnly: true,
          sameSite: 'lax' as const,
          path: '/',
          secure: isSecure,
        },
      },
      csrfToken: {
        name: `${cookiePrefix}next-auth.csrf-token`,
        options: {
          domain: cookieDomain,
          httpOnly: true,
          sameSite: 'lax' as const,
          path: '/',
          secure: isSecure,
        },
      },
    };
  })(),
  secret: process.env.NEXTAUTH_SECRET,
});

export { handler as GET, handler as POST };

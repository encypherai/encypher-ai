import NextAuth, { NextAuthOptions, User as NextAuthUser, Account, Profile } from "next-auth";
import { JWT as NextAuthJWT } from "next-auth/jwt";
import GoogleProvider from "next-auth/providers/google";

// Allow self-signed certs in dev
if (process.env.NODE_ENV === 'development') {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
}

import GitHubProvider from "next-auth/providers/github";
import CredentialsProvider from "next-auth/providers/credentials";
import { jwtDecode } from "jwt-decode";
import { UserSessionData } from "../../../../types/auth-responses"; // Adjusted path for route.ts

// Define custom types for our application
interface CustomUser {
  id?: string;
  uuid?: string;
  user_uuid?: string;
  email?: string;
  name?: string;
  first_name?: string; // Added for lint fix
  last_name?: string; // Added for lint fix
  roles?: string[];
  isActive?: boolean;
  is_active?: boolean;
  org_id?: number | string;
  organization_uuid?: string;
  org_name?: string; // Added for consistency with UserSessionData
  initialAccessToken?: string;
  accessToken?: string; // For legacy flow if kept
  backendError?: string;
  image?: string;
}

// Combine NextAuth User with our custom properties
type User = NextAuthUser & CustomUser;

type JWT = NextAuthJWT & {
  sub?: string;
  id?: string;
  name?: string;
  email?: string;
  picture?: string;
  user_uuid?: string;
  roles?: string[];
  isActive?: boolean;
  org_id?: number | string; // Allow both number and string for compatibility with NextAuth
  organization_uuid?: string;
  accessToken?: string;
  error?: string;
};

type Session = {
  user?: User;
  accessToken?: string;
  error?: string;
  expires?: Date | undefined; // Align with NextAuth's DefaultSession type
};

// Define this interface near your other type definitions
interface BackendTokenPayload { // This represents the expected payload of our backend-issued JWT
  sub: string; // user_uuid from backend token
  id: string | number; // Database primary key from backend token (user.id)
  user_uuid: string;
  email?: string;
  name?: string; // Full name
  first_name?: string;
  last_name?: string;
  roles?: string[];
  is_active?: boolean;
  org_id?: number | string | null; // From backend JWT
  org_uuid?: string | null; // From backend JWT
  org_name?: string | null; // From backend JWT
  provider?: string; // e.g., 'google', 'github', 'credentials'
  // Add other claims like exp, iat, iss, aud if needed for typing, though jwtDecode handles them
}

/**
 * Backend user data interface to ensure type safety
 */
interface BackendUser { // Represents the user object structure from backend's /oauth/exchange and /login responses
  id: string | number;
  email?: string;
  name?: string; // Full name
  first_name?: string;
  last_name?: string;
  uuid?: string; // This is the user_uuid
  roles?: string[]; // Changed from role: string
  is_active?: boolean;
  isActive?: boolean; // Keep for potential legacy backend responses, prefer is_active
  organization_id?: number | string | null;
  organization_uuid?: string | null;
  org_name?: string | null;
}

/**
 * Helper function to merge backend user data into the NextAuth user object
 */
function mergeBackendUser(user: User, backendUserData: Record<string, unknown>, accessToken: string): void {
  // Cast the backend user data to our interface for type safety
  const backendUser = backendUserData as unknown as BackendUser;
  
  user.id = String(backendUser.id ?? user.id);
  user.email = backendUser.email ?? user.email;
  user.name = backendUser.name ?? user.name; // Full name
  user.first_name = backendUser.first_name ?? user.first_name;
  user.last_name = backendUser.last_name ?? user.last_name;
  user.uuid = backendUser.uuid; // user_uuid
  user.user_uuid = backendUser.uuid; // Ensure user_uuid is set
  // Handle roles: CustomUser expects roles: string[]
  // BackendUser now also expects roles: string[] aligning with UserSessionData
  user.roles = backendUser.roles ?? user.roles ?? []; 
  user.isActive = backendUser.is_active ?? backendUser.isActive ?? false;
  user.is_active = backendUser.is_active ?? backendUser.isActive ?? false;
  user.org_id = backendUser.organization_id ?? user.org_id;
  user.organization_uuid = backendUser.organization_uuid ?? user.organization_uuid;
  user.org_name = backendUser.org_name ?? user.org_name;
  user.initialAccessToken = accessToken;
}

// --- Auth Options ---
export const authOptions: NextAuthOptions = {
  providers: [
    // === Google Provider ===
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    }), // Provider compatibility handled by NextAuth types
    
    // === GitHub Provider ===
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID as string,
      clientSecret: process.env.GITHUB_CLIENT_SECRET as string,
    }), // Provider compatibility handled by NextAuth types
    
    // === Credentials Provider ===
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        // Standard email/password
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
        // For one-time token (magic links)
        token: { label: "One-Time Token", type: "text" },
        // For legacy direct access token (if kept)
        accessToken: { label: "Access Token", type: "text" },
        // Fields for the new verified email token flow (some overlap, like email, name)
        isVerifiedTokenFlow: { label: "Is Verified Flow", type: "text" }, // boolean as string
        backendToken: { label: "Backend Token", type: "text" },
        name: { label: "Name", type: "text" }, // Shared with standard, ensure no conflict if used differently
        user_uuid: { label: "User UUID", type: "text" },
        org_uuid: { label: "Org UUID", type: "text" },
        org_name: { label: "Org Name", type: "text" },
        roles: { label: "Roles", type: "text" }, // JSON string
        first_name: { label: "First Name", type: "text" },
        last_name: { label: "Last Name", type: "text" },
        is_verified: { label: "Is Verified", type: "text" } // boolean as string
      },
      
      async authorize(credentials) {
        // Priority 1: Handling for the new verified email token flow
        if (credentials && credentials.isVerifiedTokenFlow === "true" && credentials.backendToken && credentials.email) {
          console.log("[AUTH] Authorizing with verified email token flow...");
          try {
            // Directly use the session data passed from the verify-email page
            const rolesArray = credentials.roles ? JSON.parse(credentials.roles) : [];
            const userFromVerifiedFlow: User = {
              id: credentials.user_uuid, // Use user_uuid as the primary ID for NextAuth user object internal consistency for this flow
              user_uuid: credentials.user_uuid,
              email: credentials.email,
              name: credentials.name,
              first_name: credentials.first_name, // Store these if available
              last_name: credentials.last_name,
              roles: rolesArray,
              isActive: credentials.is_verified === "true",
              is_active: credentials.is_verified === "true",
              org_uuid: credentials.org_uuid === 'null' || credentials.org_uuid === 'undefined' ? undefined : credentials.org_uuid,
              org_name: credentials.org_name === 'null' || credentials.org_name === 'undefined' ? undefined : credentials.org_name,
              // org_id can be derived later if needed, or passed if available. For now, ensure it's part of CustomUser type if used.
              initialAccessToken: credentials.backendToken, // Store the backend token
            } as User; // Added 'as User' for type assertion
            console.log("[AUTH] User from verified flow:", userFromVerifiedFlow);
            return userFromVerifiedFlow;
          } catch (error) {
            console.error("[AUTH] Error processing verified email token flow:", error);
            return null;
          }
        }

        // 2. Handling for one-time token login (e.g., magic links)
        // Ensure this doesn't conflict with the new flow's credential fields
        if (credentials && credentials.token && !credentials.backendToken && !credentials.isVerifiedTokenFlow) {
          try {
            console.log("[AUTH] Authorizing with one-time token...");
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/auth/one-time-login`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ token: credentials.token }),
            });

            if (!res.ok) {
              console.error("[AUTH] Backend one-time-login failed:", res.status, await res.text());
              return null;
            }

            const data = await res.json();
            if (data.success && data.data?.user && data.data?.access_token) {
              console.log("[AUTH] One-time token login successful.");
              const backendUser = data.data.user;
              // Construct object matching the augmented User type
              return {
                id: String(backendUser.id), // Ensure base fields are present
                uuid: backendUser.uuid,
                user_uuid: backendUser.uuid, // Map uuid to user_uuid if needed
                email: backendUser.email === null ? undefined : backendUser.email, // Explicit null check
                name: backendUser.name === null ? undefined : backendUser.name, // Explicit null check
                roles: backendUser.role ? [backendUser.role] : [], // Return roles as array
                isActive: backendUser.is_active ?? backendUser.isActive,
                is_active: backendUser.is_active ?? backendUser.isActive,
                org_id: backendUser.organization_id,
                organization_uuid: backendUser.organization_uuid,
                initialAccessToken: data.data.access_token,
              } as User;
            } else {
              console.error("[AUTH] One-time token login failed: Invalid response data", data);
              return null;
            }
          } catch (error) {
            console.error("[AUTH] One-time token login error:", error);
            return null;
          }
        }

        // 3. Handling for legacy direct access token login (if still needed, or to be deprecated)
        // This condition should be more specific if kept, to avoid overlap with isVerifiedTokenFlow
        if (credentials && credentials.accessToken && !credentials.backendToken && !credentials.isVerifiedTokenFlow && !credentials.token) {
          try {
            console.log("[AUTH] Authorizing with direct access token...");
            // Decode the JWT to get user info without making a backend call
            // This is safe because the token was generated by our backend
            const decoded = jwtDecode<BackendTokenPayload>(credentials.accessToken);
            console.log("[AUTH] Decoded token for direct access:", decoded);
            
            // Validate essential fields from token
            if (decoded && decoded.sub && decoded.id) { // decoded.sub is user_uuid, decoded.id is DB PK
              return {
                id: String(decoded.id), // Use the DB primary key as 'id'
                user_uuid: decoded.user_uuid || decoded.sub, // Ensure user_uuid is populated
                email: decoded.email,
                name: decoded.name, // Will be undefined if not in token yet
                roles: decoded.roles, // Assign the full roles array
                isActive: decoded.is_active,
                is_active: decoded.is_active, // for consistency
                org_id: decoded.org_id, // Extract from token
                organization_uuid: decoded.org_uuid, // Corrected: Extract from token
                initialAccessToken: credentials.accessToken,
              } as User;
            } else {
              console.error("[AUTH] Direct token login failed: Invalid token structure or missing sub/id", decoded);
              return null;
            }
          } catch (error) {
            console.error("[AUTH] Direct token login error:", error);
            return null;
          }
        }

        // 3. Handling for email/password login
        if (credentials && credentials.email && credentials.password) {
          try {
            console.log("[AUTH] Authorizing with email/password...");
            // Force IPv4 by replacing 'localhost' to avoid potential IPv6 resolution hangs
            const rawBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
            const baseUrl = rawBaseUrl.replace('localhost', '127.0.0.1');
            console.log(`[AUTH] Using backend URL: ${baseUrl}/api/v1/auth/login`);

            // Add a timeout to prevent hanging requests
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

            let res: Response;
            try {
              res = await fetch(`${baseUrl}/api/v1/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  email: credentials.email,
                  password: credentials.password,
                }),
                signal: controller.signal,
              });
            } finally {
              clearTimeout(timeoutId);
            }

            if (!res.ok) {
              const errText = await res.text();
              console.error("[AUTH] Backend login failed:", res.status, errText);
              return null;
            }

            const data = await res.json();
            if (data.success && data.data?.user && data.data?.access_token) {
              console.log("[AUTH] Email/password login successful.");
              const backendUser = data.data.user;
              return {
                id: String(backendUser.id),
                uuid: backendUser.uuid,
                user_uuid: backendUser.uuid,
                email: backendUser.email,
                name: backendUser.name,
                roles: backendUser.role ? [backendUser.role] : [], // Return roles as array
                isActive: backendUser.is_active ?? backendUser.isActive,
                is_active: backendUser.is_active ?? backendUser.isActive,
                org_id: backendUser.organization_id,
                organization_uuid: backendUser.organization_uuid,
                initialAccessToken: data.data.access_token,
              } as User;
            } else {
              console.error("[AUTH] Email/password login failed: Invalid response data", data);
              return null;
            }
          } catch (error) {
            console.error("[AUTH] Email/password login error:", error);
            return null;
          }
        }

        // If we reach here, no valid credentials were provided
        console.error("[AUTH] No valid credentials provided");
        return null;
      },
    }),
  ],

  // JWT Secret
  secret: process.env.NEXTAUTH_SECRET,

  // Session strategy
  session: {
    strategy: "jwt" as const,
  },

  cookies: {
    sessionToken: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.session-token' : 'next-auth.session-token',
      options: {
        domain: process.env.NEXTAUTH_COOKIE_DOMAIN || '.encypherai.com',
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
    callbackUrl: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.callback-url' : 'next-auth.callback-url',
      options: {
        domain: process.env.NEXTAUTH_COOKIE_DOMAIN || '.encypherai.com',
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
    csrfToken: {
      name: process.env.NODE_ENV === 'production' ? '__Secure-next-auth.csrf-token' : 'next-auth.csrf-token',
      options: {
        domain: process.env.NEXTAUTH_COOKIE_DOMAIN || '.encypherai.com',
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: process.env.NODE_ENV === 'production',
      },
    },
  },

  callbacks: {
    /**
     * signIn callback to handle OAuth sign-in and backend sync.
     */
    async signIn(params: { user: User | any; account: Account | null; profile?: Profile }): Promise<boolean> {
      const { user, account, profile } = params;
      console.log('[NextAuth][signIn] START - user:', user);
      console.log('[NextAuth][signIn] START - account:', account);
      console.log('[NextAuth][signIn] START - profile:', profile);

      if (account && profile && (account.provider === 'google' || account.provider === 'github')) {
        console.log(`[NextAuth][signIn] OAuth attempt via ${account.provider}.`);
        try {
          console.log('[NextAuth][signIn] Calling backend /api/v1/auth/oauth/exchange...');
          const backendPayload = {
            provider: account.provider,
            id_token: account.id_token,
            access_token: account.access_token,
          };
          
          // Force IPv4 by replacing 'localhost' with '127.0.0.1' if present
          const rawBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
          const baseUrl = rawBaseUrl.replace('localhost', '127.0.0.1');
          console.log(`[NextAuth][signIn] Using backend URL: ${baseUrl}/api/v1/auth/oauth/exchange`);
          
          // Set a timeout for the fetch request to prevent hanging
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
          
          try {
            const backendRes = await fetch(`${baseUrl}/api/v1/auth/oauth/exchange`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(backendPayload),
              signal: controller.signal
            });

            clearTimeout(timeoutId); // Clear the timeout if request completes

            if (!backendRes.ok) {
              const errorText = await backendRes.text();
              console.error(`[NextAuth][signIn] Backend /api/v1/auth/oauth/exchange failed (${backendRes.status}):`, errorText);
              (user as User).backendError = `Backend OAuth sync failed: ${errorText}`;
              return false; // Block sign-in if backend sync fails
            }

            const backendData = await backendRes.json();
            console.log('[NextAuth][signIn] Backend /api/v1/auth/oauth/exchange response:', backendData);

            if (backendData.success && backendData.data?.user && backendData.data?.access_token) {
              console.log('[NextAuth][signIn] Backend sync successful. Attaching data to user object.');
              mergeBackendUser(user as User, backendData.data.user, backendData.data.access_token);
              return true;
            } else {
              console.error('[NextAuth][signIn] Backend /api/v1/auth/oauth/exchange returned success=false or missing data:', backendData.error);
              (user as User).backendError = `Backend OAuth sync failed: ${backendData.error?.message || 'Unknown error'}`;
              return false; // Block sign-in
            }
          } catch (error) {
            console.error('[NextAuth][signIn] Error calling backend /api/v1/auth/oauth/exchange:', error);
            (user as User).backendError = `Backend OAuth sync failed: ${error instanceof Error ? error.message : 'Unknown error'}`;
            return false; // Block sign-in on error
          }
        } catch (error) {
          console.error('[NextAuth][signIn] Error during OAuth sign-in:', error);
          return false; // Block sign-in on error
        }
      }
      
      return true; // Success for non-OAuth providers
    },

    /**
     * session callback to attach backend user info and tokens to the session
     */
    async session(params: { session: any; token: any }): Promise<Session> {
      const { session, token } = params;
      console.log('[NextAuth][session] START - session:', session);
      console.log('[NextAuth][session] START - token:', token);
      
      // Reconstruct session.user directly from token properties
      session.user = {
        id: token.id as string, // This should now be the DB Primary Key (stringified)
        name: token.name as string | undefined,
        email: token.email as string | undefined,
        image: token.picture as string | undefined,
        user_uuid: token.user_uuid as string | undefined, // This is the actual UUID
        first_name: token.first_name as string | undefined,
        last_name: token.last_name as string | undefined,
        roles: token.roles as string[] | undefined,
        isActive: !!token.isActive, // Ensures boolean
        org_id: token.org_id as number | string | undefined,
        organization_uuid: token.organization_uuid as string | undefined,
        org_name: token.org_name as string | undefined,
        is_active: !!token.isActive, // for consistency
      } as User;
      
      session.accessToken = token.accessToken as string | undefined;
      session.error = token.error as string | undefined;
      
      console.log('[NextAuth][session] END - returning session:', session);
      return session;
    },

    /**
     * jwt callback to handle token creation and updates
     */
    async jwt(params: { token: any; user?: any; account?: any }): Promise<JWT> {
      const { token, user } = params;
      // Initial sign in
      if (user) {
        console.log('[NextAuth][jwt] User present, updating token with user data:', user);
        
        token.id = user.id; // DB Primary Key from authorize
        token.sub = user.id; // Explicitly set NextAuth sub to DB Primary Key for its internal use
        token.user_uuid = user.user_uuid; // UUID from authorize
        token.name = user.name;
        token.email = user.email;
        token.name = user.name; // Ensure name is set
        token.first_name = user.first_name;
        token.last_name = user.last_name;
        token.picture = user.image; // This might be null/undefined for credentials login
        token.roles = user.roles; // user.roles should be an array from authorize
        token.isActive = user.isActive ?? user.is_active; // Ensure boolean
        token.org_id = user.org_id;
        token.organization_uuid = user.organization_uuid;
        token.org_name = user.org_name;
        
        // If we have an access token from the backend (via OAuth or credentials), store it
        // and re-decode to ensure all claims are fresh on the NextAuth token.
        if (user.initialAccessToken) {
          token.accessToken = user.initialAccessToken; // This is the backend JWT
          try {
            const backendTokenDecoded = jwtDecode<BackendTokenPayload>(user.initialAccessToken);
            // Update token fields from the fresh backend token, preferring backend token's info
            token.email = backendTokenDecoded.email ?? token.email;
            token.name = backendTokenDecoded.name ?? token.name; // Full name
            // Assuming first_name, last_name, org_name might also be in backendTokenDecoded if it's our standard JWT
            // Need to ensure BackendTokenPayload includes these if we want to refresh them here.
            // For now, they are set from the 'user' object initially.
            // If UserSessionData (source of 'user' object in verified flow) is comprehensive, this might be sufficient.
            token.first_name = backendTokenDecoded.first_name ?? token.first_name; 
            token.last_name = backendTokenDecoded.last_name ?? token.last_name;
            token.roles = backendTokenDecoded.roles ?? token.roles; // Assign the full roles array
            token.isActive = backendTokenDecoded.is_active ?? token.isActive;
            token.org_id = backendTokenDecoded.org_id ?? token.org_id;
            token.organization_uuid = backendTokenDecoded.org_uuid ?? token.organization_uuid; // Corrected
            token.org_name = backendTokenDecoded.org_name ?? token.org_name;
            // token.id and token.user_uuid should already be correctly set from the `user` object,
            // which itself was populated from a decoded token in `authorize` or by `mergeBackendUser`.
            // However, ensure they are consistent if backendTokenDecoded has them:
            if (backendTokenDecoded.id) token.id = String(backendTokenDecoded.id);
            if (backendTokenDecoded.user_uuid) token.user_uuid = backendTokenDecoded.user_uuid;
            if (token.id) token.sub = token.id; // Re-affirm sub is primary key

          } catch (e) {
            console.error("[NextAuth][jwt] Error decoding initialAccessToken in jwt callback:", e);
          }
        }
        
        // If there was an error during sign-in, propagate it
        if (user.backendError) {
          token.error = user.backendError;
        }
      }
      
      return token;
    },
  },
};

// Export NextAuth API route handlers
const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };

import type { DefaultUser, DefaultSession } from "next-auth";
import type { JWT as DefaultJWT } from "next-auth/jwt";

// Extend the built-in types

declare module "next-auth" {
  /**
   * Represents the user object. Extends DefaultUser and adds custom fields.
   */
  interface User extends DefaultUser {
    // Explicitly define base fields matching DefaultUser for clarity
    id: string; // DefaultUser has string
    name?: string | null | undefined; // Allow null
    email?: string | null | undefined; // Allow null
    image?: string | null | undefined; // Allow null

    // Custom fields from backend/authorize
    role?: string;
    isActive?: boolean;
    is_active?: boolean; // Allow for backend variations
    org_id?: string | number;
    organization_uuid?: string;
    user_uuid?: string;
    uuid?: string; // Allow for backend variations
    accessToken?: string; // Our backend JWT (from OAuth sync or authorize)
    initialAccessToken?: string; // Specific field from authorize return
    backendError?: string; // For passing errors
  }

  /**
   * Represents the session object returned by the session callback.
   */
  interface Session extends DefaultSession {
    user?: User; // Use our fully augmented User type
    expires?: Date;
    accessToken?: string; // Add our custom backend token
    error?: string; // For propagating errors
  }
}

declare module "next-auth/jwt" {
  /**
   * Represents the JWT payload after the jwt callback.
   */
  interface JWT extends DefaultJWT {
    sub?: string;
    name?: string;
    email?: string;
    picture?: string;
    iat?: number;
    exp?: number;
    jti?: string;
    accessToken?: string;
    refreshToken?: string;
    accessTokenExpires?: number;
    user_uuid?: string; // Essential for backend
    role?: string;
    isActive?: boolean;
    org_id?: string | number;
    organization_uuid?: string;
    error?: string; // For propagating errors
  }
}

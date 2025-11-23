import { DefaultSession, DefaultUser } from "next-auth";
import { DefaultJWT } from "next-auth/jwt";

// Extend the JWT type
declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    id?: string;
    role?: string;
    accessToken?: string;
  }
}

// Extend the User type
declare module "next-auth" {
  interface User extends DefaultUser {
    id?: string; // Ensure id is always treated as string if coming from backend
    role?: string;
    accessToken?: string;
    email?: string | null;
    isActive?: boolean;
    is_active?: boolean;
    org_id?: string | number;
    organization_uuid?: string;
  }

  // Extend the Session type
  interface Session extends DefaultSession {
    accessToken?: string; // Add the access token to the session
    user?: {
      id?: string;
      role?: string;
      email?: string | null;
      isActive?: boolean;
      is_active?: boolean;
      org_id?: string | number;
      organization_uuid?: string;
    } & DefaultSession["user"]; // Add id and role to the session's user object
  }
}

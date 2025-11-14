import type { DefaultSession } from "next-auth";
import type { JWT as DefaultJWT } from "next-auth/jwt";

// Module augmentation for NextAuth.js
// Ensures session.user.id and token.id/email/accessToken are typed

declare module "next-auth" {
  interface Session {
    user: {
      id?: string;
      accessToken?: string;
      role?: string;
      tier?: string;
    } & DefaultSession["user"];
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    id?: string;
    email?: string;
    accessToken?: string;
    role?: string;
    tier?: string;
  }
}

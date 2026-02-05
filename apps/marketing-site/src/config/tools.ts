// src/config/tools.ts
// Central registry for tools used by both the navbar dropdown and /tools page

export type ToolLink = {
  name: string;
  description?: string;
  href: string;
  hiddenInMenu?: boolean; // set true to hide from dropdown but keep on /tools
};

export const toolLinks: ToolLink[] = [
  {
    name: "Sign/Verify",
    description: "Sign content with secure metadata or verify authenticity using the Encypher tool.",
    href: "/tools/sign-verify",
  },
  {
    name: "Sign Only",
    description: "Sign text with cryptographic provenance metadata.",
    href: "/tools/sign",
  },
  {
    name: "Verify Only",
    description: "Verify signed text and inspect embedded metadata.",
    href: "/tools/verify",
  },
  {
    name: "WordPress Plugin",
    description: "C2PA content authentication for WordPress. Protect your posts with cryptographic proof of authorship.",
    href: "/tools/wordpress",
  },
];

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
    name: "Encode/Decode",
    description: "Embed or extract secure metadata in your text using Unicode-powered tools.",
    href: "/tools/encode-decode",
  },
  {
    name: "Encode Only",
    description: "Encode metadata into text (Unicode variation selectors).",
    href: "/tools/encode",
  },
  {
    name: "Decode Only",
    description: "Extract metadata from text (Unicode variation selectors).",
    href: "/tools/decode",
  },
  // Only include tools that exist in frontend/src/app/tools/
  // Removed non-existent tools: encode-file, decode-file, encode-ads-coremetadata-file, scan-ads-coremetadata-file
];

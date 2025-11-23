"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";
import { siteConfig } from "@/lib/seo";
import { useEffect, useMemo, useState } from "react";

export default function WebPageSchema() {
  const pathname = usePathname();
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");

  useEffect(() => {
    if (typeof document !== "undefined") {
      setTitle(document.title || "Encypher");
      const meta = document.querySelector('meta[name="description"]') as HTMLMetaElement | null;
      setDescription(meta?.content || "");
    }
  }, [pathname]);

  const jsonLd = useMemo(() => {
    const url = `${siteConfig.url}${pathname || ""}`;
    return {
      "@context": "https://schema.org",
      "@type": "WebPage",
      name: title || "Encypher",
      description: description || undefined,
      url,
    };
  }, [pathname, title, description]);

  return (
    <Script
      id="schema-webpage"
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}

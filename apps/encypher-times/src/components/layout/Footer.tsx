import Link from "next/link";
import { SECTIONS } from "@/lib/sections";
import { EncypherMark } from "@/components/ui/EncypherMark";

export function Footer() {
  return (
    <footer className="mt-12 pt-8 pb-12 border-t-2 border-rule">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        {/* Sections */}
        <div>
          <h4 className="section-label text-ink mb-3">Sections</h4>
          <ul className="space-y-1.5">
            {SECTIONS.map((section) => (
              <li key={section.slug}>
                <Link
                  href={`/section/${section.slug}`}
                  className="font-[family-name:var(--font-ui)] text-sm text-ink-muted hover:text-ink transition-colors"
                >
                  {section.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Tools */}
        <div>
          <h4 className="section-label text-ink mb-3">Tools</h4>
          <ul className="space-y-1.5">
            <li>
              <Link
                href="/verify"
                className="font-[family-name:var(--font-ui)] text-sm text-ink-muted hover:text-ink transition-colors"
              >
                Verify Content
              </Link>
            </li>
          </ul>
        </div>

        {/* About */}
        <div>
          <h4 className="section-label text-ink mb-3">About</h4>
          <ul className="space-y-1.5">
            <li>
              <Link
                href="/about"
                className="font-[family-name:var(--font-ui)] text-sm text-ink-muted hover:text-ink transition-colors"
              >
                About This Site
              </Link>
            </li>
            <li>
              <a
                href="https://encypher.com"
                target="_blank"
                rel="noopener noreferrer"
                className="font-[family-name:var(--font-ui)] text-sm text-ink-muted hover:text-ink transition-colors"
              >
                About Encypher
              </a>
            </li>
          </ul>
        </div>

        {/* Provenance info */}
        <div>
          <h4 className="section-label text-ink mb-3">Content Provenance</h4>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint leading-relaxed">
            Every article, image, audio clip, and video on this site carries
            tamper-proof proof of origin signed by Encypher, built on the C2PA
            open standard. Install{" "}
            <a
              href="https://encypher.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-0.5 text-blue-ncs hover:underline"
            >
              <EncypherMark className="w-3 h-3" color="azure" />
              Encypher Verify
            </a>{" "}
            for Chrome to see proof-of-origin badges on every article, or copy
            any text to the{" "}
            <Link href="/verify" className="text-blue-ncs hover:underline">
              verify page
            </Link>
            .
          </p>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="mt-8 pt-4 border-t border-rule-light flex flex-col sm:flex-row items-center justify-between gap-2">
        <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint">
          The Encypher Times is a demonstration site. All articles are
          fictional. All signatures are real.
        </p>
        <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint inline-flex items-center gap-1">
          Content provenance by{" "}
          <a
            href="https://encypher.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-blue-ncs hover:underline"
          >
            <EncypherMark className="w-3 h-3" color="azure" />
            Encypher
          </a>
        </p>
      </div>
    </footer>
  );
}

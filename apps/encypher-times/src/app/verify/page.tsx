import type { Metadata } from "next";
import { VerifyWidget } from "@/components/ui/VerifyWidget";
import { EncypherMark } from "@/components/ui/EncypherMark";

export const metadata: Metadata = {
  title: "Verify Content Authenticity -- The Encypher Times",
  description:
    "Paste any text from The Encypher Times to verify its cryptographic provenance signature.",
};

export default function VerifyPage() {
  return (
    <div className="py-8 pb-24 max-w-[680px] mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <EncypherMark className="w-6 h-6" color="navy" />
          <h1 className="font-[family-name:var(--font-headline)] text-3xl font-black text-ink">
            Verify Content Authenticity
          </h1>
        </div>
        <p className="text-ink-light leading-relaxed">
          Every article on The Encypher Times is signed by Encypher at the
          sentence level. Each sentence carries an invisible, tamper-proof
          signature that proves who published it and whether it&apos;s been
          altered -- even after the text has been copied, shared, or
          redistributed.
        </p>
      </div>

      {/* Instructions */}
      <div className="mb-8 p-5 bg-newsprint-warm border border-rule-light rounded">
        <h2 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink mb-3">
          How to Verify
        </h2>
        <ol className="font-[family-name:var(--font-ui)] text-sm text-ink-muted space-y-2 list-decimal list-inside">
          <li>Copy any sentence or paragraph from an article on this site</li>
          <li>Paste it into the box below</li>
          <li>
            Click <strong>Verify</strong> -- Encypher confirms the publisher,
            signing date, and integrity status
          </li>
        </ol>
      </div>

      {/* Verify widget */}
      <VerifyWidget />

      {/* How It Works -- outcome-focused */}
      <div className="mt-10 pt-6 border-t border-rule-light">
        <h2 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink mb-3">
          How It Works
        </h2>
        <div className="font-[family-name:var(--font-ui)] text-sm text-ink-muted space-y-3 leading-relaxed">
          <p>
            When articles are signed, each sentence receives an invisible,
            tamper-proof marker that travels with the text wherever it goes. If
            even a single character is changed, the signature breaks -- revealing
            exactly which sentences were altered.
          </p>
          <p>
            These markers survive copy-paste, text editors, and raw extraction,
            making them practical for real-world content tracking. When content
            enters a new system, the signatures are detectable at the point of
            ingestion.
          </p>
        </div>

        {/* Collapsible technical details */}
        <details className="mt-4">
          <summary className="font-[family-name:var(--font-ui)] text-xs font-medium text-ink-faint cursor-pointer hover:text-ink-muted transition-colors">
            Technical Details
          </summary>
          <div className="mt-3 p-4 bg-newsprint-warm/50 border border-rule-light/50 rounded font-[family-name:var(--font-ui)] text-xs text-ink-faint space-y-2 leading-relaxed">
            <p>
              Encypher embeds invisible Unicode variation selectors into each
              sentence. Each marker carries a unique document identifier and an
              HMAC signature cryptographically bound to the sentence content.
            </p>
            <p>
              On verification, the API extracts the embedded marker, recomputes
              the HMAC against the current text, and compares. A match confirms
              integrity; a mismatch identifies tampering at the sentence level.
            </p>
            <p>
              The markers are zero-width characters -- invisible to readers and
              preserved through standard text operations including clipboard,
              most editors, and raw text pipelines.
            </p>
          </div>
        </details>
      </div>

      {/* Chrome extension CTA */}
      <div className="mt-8 p-5 bg-delft-blue/5 border border-delft-blue/15 rounded">
        <h3 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink mb-2">
          Automatic Verification with Encypher Verify
        </h3>
        <p className="font-[family-name:var(--font-ui)] text-sm text-ink-muted leading-relaxed">
          Install{" "}
          <a
            href="https://encypherai.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-blue-ncs hover:underline font-medium"
          >
            <EncypherMark className="w-3.5 h-3.5" color="azure" />
            Encypher Verify
          </a>{" "}
          for Chrome to see proof-of-origin badges appear automatically on
          every signed article, without needing to copy and paste.
        </p>
      </div>
    </div>
  );
}

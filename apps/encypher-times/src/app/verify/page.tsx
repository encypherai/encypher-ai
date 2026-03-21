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
    <div className="py-8 max-w-[680px] mx-auto">
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

      {/* Technical details */}
      <div className="mt-10 pt-6 border-t border-rule-light">
        <h2 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink mb-3">
          How It Works
        </h2>
        <div className="font-[family-name:var(--font-ui)] text-sm text-ink-muted space-y-3 leading-relaxed">
          <p>
            When articles are signed, invisible Unicode characters (variation
            selectors) are embedded into each sentence. These characters are
            zero-width -- they are invisible to readers and do not affect the
            text&apos;s appearance.
          </p>
          <p>
            Each marker contains a unique identifier and an HMAC signature bound
            to the sentence content. If even a single character of the sentence
            is changed, the signature will not match, revealing the tampering.
          </p>
          <p>
            The markers survive copy-paste, most text editors, and raw text
            extraction. This is what makes the technology practical for
            real-world content provenance: the proof of origin travels with the
            text and is detectable whenever content enters a new system.
          </p>
        </div>
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

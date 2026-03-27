import { FileText, Hash } from "lucide-react";
import Link from "next/link";
import { EncypherMark } from "@encypher/icons";

interface ContentIntegrityBoxProps {
  documentId: string;
  signedAt: string;
  merkleRoot?: string;
  hasHeroImage?: boolean;
}

export function ContentIntegrityBox({
  documentId,
  signedAt,
  merkleRoot,
  hasHeroImage = true,
}: ContentIntegrityBoxProps) {
  const signedDate = new Date(signedAt).toLocaleString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  });

  return (
    <div className="my-8 p-5 bg-newsprint-warm border border-rule-light rounded">
      <div className="flex items-center gap-2 mb-3">
        <EncypherMark className="w-4 h-4" color="navy" />
        <h4 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink">
          Signed &amp; Protected by Encypher
        </h4>
      </div>

      <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted leading-relaxed mb-3">
        Every sentence in this article carries an invisible, tamper-proof
        signature proving who published it and when. If this text is copied,
        redistributed, or scraped into a dataset, the proof of origin travels
        with it -- detectable at the point of ingestion.
      </p>

      {hasHeroImage && (
        <p className="font-[family-name:var(--font-ui)] text-xs text-ink-muted leading-relaxed mb-4">
          This article&apos;s hero image is independently signed with a C2PA
          provenance manifest, verifiable by any C2PA-compatible tool.
        </p>
      )}

      {/* Cryptographic Record */}
      <div className="mb-4">
        <p className="font-[family-name:var(--font-ui)] text-[0.65rem] font-bold text-ink-faint uppercase tracking-wider mb-2">
          Cryptographic Record
        </p>
        <div className="space-y-2 font-[family-name:var(--font-mono)] text-xs text-ink-muted">
          <div className="flex items-start gap-2">
            <FileText className="w-3.5 h-3.5 mt-0.5 shrink-0" />
            <div>
              <span className="text-ink-faint">Document ID: </span>
              <span className="text-ink">{documentId}</span>
            </div>
          </div>
          {merkleRoot && (
            <div className="flex items-start gap-2">
              <Hash className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              <div>
                <span className="text-ink-faint">Integrity Hash: </span>
                <span className="text-ink">
                  {merkleRoot.slice(0, 16)}...{merkleRoot.slice(-8)}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* CTA */}
      <div className="pt-3 border-t border-rule-light">
        <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint leading-relaxed">
          Copy any paragraph from this article and paste it below to verify the
          signature is authentic. Or install{" "}
          <a
            href="https://encypher.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-blue-ncs hover:underline font-medium"
          >
            <EncypherMark className="w-3 h-3" color="azure" />
            Encypher Verify
          </a>{" "}
          for Chrome to see proof-of-origin badges across every article
          automatically.
        </p>
      </div>

      {/* C2PA Standards Reference */}
      <div className="mt-3 pt-2 border-t border-rule-light/50">
        <p className="font-[family-name:var(--font-ui)] text-[0.6rem] text-ink-faint/70 leading-relaxed">
          Built on the C2PA open standard (Section A.7) -- Encypher co-chairs
          the C2PA Text Provenance Task Force alongside Google, BBC, OpenAI,
          Adobe, and Microsoft.
        </p>
      </div>
    </div>
  );
}

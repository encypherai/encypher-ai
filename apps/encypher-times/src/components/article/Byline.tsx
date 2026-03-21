import { formatDate, estimateReadingTime } from "@/lib/utils";

interface BylineProps {
  byline: string;
  dateline: string;
  publishedAt: string;
  updatedAt?: string;
  wordCount: number;
}

export function Byline({
  byline,
  dateline,
  publishedAt,
  updatedAt,
  wordCount,
}: BylineProps) {
  return (
    <div className="font-[family-name:var(--font-ui)] text-sm text-ink-muted py-3 border-t border-b border-rule-light">
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span className="font-bold text-ink">{byline}</span>
        {dateline && (
          <>
            <span aria-hidden="true">|</span>
            <span>{dateline}</span>
          </>
        )}
      </div>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 mt-1 text-xs text-ink-faint">
        <time dateTime={publishedAt}>{formatDate(publishedAt)}</time>
        {updatedAt && (
          <>
            <span aria-hidden="true">|</span>
            <span>Updated {formatDate(updatedAt)}</span>
          </>
        )}
        <span aria-hidden="true">|</span>
        <span>{estimateReadingTime(wordCount)}</span>
      </div>
    </div>
  );
}

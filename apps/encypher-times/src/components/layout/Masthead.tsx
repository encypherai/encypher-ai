import { formatDate } from "@/lib/utils";

export function Masthead() {
  const today = formatDate(new Date().toISOString());

  return (
    <header className="pt-4 pb-3">
      {/* Top rule */}
      <div className="rule-heavy" />

      {/* Masthead content */}
      <div className="text-center py-3">
        <h1
          className="text-[2.5rem] sm:text-[3.5rem] lg:text-[4.5rem] font-bold leading-tight tracking-wide"
          style={{ fontFamily: "'UnifrakturCook', 'Georgia', serif" }}
        >
          The Encypher Times
        </h1>
        <p className="font-[family-name:var(--font-headline)] italic text-ink-muted text-[0.8rem] sm:text-[0.85rem] tracking-[0.05em] mt-1">
          Every Word Authenticated
        </p>
      </div>

      {/* Date line and edition info */}
      <div className="rule-heavy" />
      <div className="flex items-center justify-between py-1.5 font-[family-name:var(--font-ui)] text-[0.7rem] text-ink-faint">
        <span>{today}</span>
        <span className="tracking-[0.1em] uppercase">Digital Edition</span>
        <span>Vol. I, No. 1</span>
      </div>
      <div className="rule-light" />
    </header>
  );
}

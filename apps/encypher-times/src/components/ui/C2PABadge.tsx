import { EncypherMark } from "@/components/ui/EncypherMark";

export function C2PABadge() {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-delft-blue/5 border border-delft-blue/15 rounded text-[0.625rem] font-[family-name:var(--font-ui)] font-bold text-delft-blue uppercase tracking-wider whitespace-nowrap">
      <EncypherMark className="w-3 h-3" color="navy" />
      C2PA Signed
    </span>
  );
}

import { EncypherMark } from "@/components/ui/EncypherMark";

export function DemoBanner() {
  return (
    <div className="sticky top-0 z-50 bg-gradient-to-r from-delft-blue to-[#152640] text-white text-center py-2.5 px-4 font-[family-name:var(--font-ui)] text-[0.7rem] font-bold tracking-[0.15em] uppercase shadow-md border-b-2 border-white/20">
      Every Article, Image, Audio, and Video Cryptographically Signed by{" "}
      <a
        href="https://encypherai.com"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 underline underline-offset-2 hover:text-columbia-blue transition-colors"
      >
        <EncypherMark className="w-3.5 h-3.5 inline-block" color="white" />
        Encypher
      </a>
    </div>
  );
}

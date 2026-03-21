import type { SignedAudioRef } from "@/lib/types";
import { C2PABadge } from "@/components/ui/C2PABadge";

interface AudioPlayerProps {
  audio: SignedAudioRef;
}

export function AudioPlayer({ audio }: AudioPlayerProps) {
  const minutes = Math.floor(audio.duration / 60);
  const seconds = audio.duration % 60;
  const durationStr = `${minutes}:${seconds.toString().padStart(2, "0")}`;

  return (
    <div className="my-6 p-4 bg-newsprint-warm border border-rule-light rounded">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h4 className="font-[family-name:var(--font-ui)] text-sm font-bold text-ink">
            {audio.title}
          </h4>
          <p className="font-[family-name:var(--font-ui)] text-xs text-ink-faint mt-0.5">
            {durationStr} | {audio.credit}
          </p>
        </div>
        {audio.c2paSigned && <C2PABadge />}
      </div>
      {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
      <audio controls className="w-full" preload="metadata">
        <source src={`/signed-media/${audio.filename}`} />
        Your browser does not support the audio element.
      </audio>
    </div>
  );
}

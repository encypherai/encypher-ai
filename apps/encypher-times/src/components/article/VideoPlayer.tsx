import type { SignedVideoRef } from "@/lib/types";
import { C2PABadge } from "@/components/ui/C2PABadge";

interface VideoPlayerProps {
  video: SignedVideoRef;
}

export function VideoPlayer({ video }: VideoPlayerProps) {
  const minutes = Math.floor(video.duration / 60);
  const seconds = video.duration % 60;
  const durationStr = `${minutes}:${seconds.toString().padStart(2, "0")}`;

  return (
    <div className="my-6">
      <div className="aspect-video bg-black rounded overflow-hidden">
        <video
          controls
          className="w-full h-full"
          preload="metadata"
          poster={
            video.poster ? `/signed-media/${video.poster}` : undefined
          }
        >
          <source src={`/signed-media/${video.filename}`} />
          Your browser does not support the video element.
        </video>
      </div>
      <div className="flex items-start justify-between gap-2 mt-2">
        <div className="font-[family-name:var(--font-ui)] text-xs text-ink-faint">
          <span className="font-medium text-ink">{video.title}</span>
          <span className="ml-2">{durationStr}</span>
          {video.credit && <span className="ml-2 italic">{video.credit}</span>}
        </div>
        {video.c2paSigned && <C2PABadge />}
      </div>
    </div>
  );
}

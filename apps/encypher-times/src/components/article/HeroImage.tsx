import type { SignedImageRef } from "@/lib/types";
import { C2PABadge } from "@/components/ui/C2PABadge";

interface HeroImageProps {
  image: SignedImageRef;
}

export function HeroImage({ image }: HeroImageProps) {
  return (
    <figure className="my-6">
      <div className="overflow-hidden bg-newsprint-warm">
        <img
          src={`/signed-media/${image.filename}`}
          alt={image.alt}
          width={image.width || 1200}
          height={image.height || 675}
          className="w-full h-auto"
        />
      </div>
      <figcaption className="flex items-start justify-between gap-2 mt-2">
        <div className="font-[family-name:var(--font-ui)] text-xs text-ink-faint leading-relaxed">
          {image.caption && <span>{image.caption} </span>}
          {image.credit && <span className="italic">{image.credit}</span>}
        </div>
        {image.c2paSigned && <C2PABadge />}
      </figcaption>
    </figure>
  );
}

import React from "react";
import { BRAND_COLORS } from "../colors";
import { MARK_GROUP_TRANSFORM, MARK_PATHS } from "../paths";
import type { EncypherMarkProps } from "../types";

const colorMap = {
  navy: BRAND_COLORS.navy,
  azure: BRAND_COLORS.azure,
  teal: BRAND_COLORS.teal,
  white: BRAND_COLORS.white,
  current: "currentColor",
} as const;

const bgColorMap = {
  navy: BRAND_COLORS.white,
  azure: BRAND_COLORS.white,
  teal: BRAND_COLORS.navy,
  white: BRAND_COLORS.navy,
  current: "currentColor",
} as const;

/**
 * Encypher brand mark - parametric React component.
 * 24x24 viewBox with uniform scale and perfect centering.
 */
export const EncypherMark: React.FC<EncypherMarkProps> = ({
  className,
  color = "current",
  withBackground = false,
  size,
}: EncypherMarkProps) => {
  const fill = colorMap[color as keyof typeof colorMap];
  const bgFill = bgColorMap[color as keyof typeof bgColorMap];

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={className}
      fill="none"
      role="img"
      aria-label="Encypher mark"
    >
      {withBackground && (
        <rect
          x="0.5"
          y="0.5"
          width="23"
          height="23"
          rx="3"
          fill={bgFill}
        />
      )}
      <g
        transform={
          withBackground
            ? "translate(13.56,9.593) scale(0.85)"
            : MARK_GROUP_TRANSFORM
        }
      >
        {MARK_PATHS.map((path) => (
          <path
            key={path.id}
            fill={fill}
            fillRule="nonzero"
            transform={path.transform}
            d={path.d}
          />
        ))}
      </g>
    </svg>
  );
};

import React from "react";
import { BRAND_COLORS } from "../colors";
import { MARK_PATHS } from "../paths";
import type { EncypherLoaderProps } from "../types";

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
  xl: "h-12 w-12",
} as const;

const loaderColorMap = {
  navy: BRAND_COLORS.navy,
  white: BRAND_COLORS.white,
  current: "currentColor",
} as const;

/**
 * Encypher branded loading spinner.
 * The outer jagged ring rotates while the inner icon stays static.
 * 24x24 viewBox with corrected centering (transform-origin at true center).
 */
export const EncypherLoader: React.FC<EncypherLoaderProps> = ({
  className = "",
  size = "md",
  color = "current",
}: EncypherLoaderProps) => {
  const fill = loaderColorMap[color as keyof typeof loaderColorMap];
  const outerRing = MARK_PATHS[0];
  const innerPaths = MARK_PATHS.slice(1);

  return (
    <svg
      className={`mx-auto ${sizeMap[size as keyof typeof sizeMap]} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      aria-label="Loading"
      role="status"
    >
      <style>
        {`
          @keyframes encypher-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .encypher-ring {
            animation: encypher-spin 2.5s linear infinite;
            transform-origin: -0.7657px 3.3383px;
          }
        `}
      </style>

      <g transform="translate(12.7657,8.6617)">
        {/* Outer ring - rotates */}
        <g className="encypher-ring">
          <path
            fill={fill}
            fillOpacity="0.35"
            fillRule="nonzero"
            transform={outerRing.transform}
            d={outerRing.d}
          />
        </g>

        {/* Inner paths - static */}
        {innerPaths.map((path) => (
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

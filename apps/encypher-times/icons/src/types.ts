export interface EncypherMarkProps {
  className?: string;
  /** Brand color or "current" to inherit CSS color */
  color?: "navy" | "azure" | "teal" | "white" | "current";
  /** Add a rounded-rect background behind the mark */
  withBackground?: boolean;
  /** Explicit size in px (overrides className sizing) */
  size?: number;
}

export interface EncypherLoaderProps {
  className?: string;
  /** Tailwind size preset */
  size?: "sm" | "md" | "lg" | "xl";
  /** Brand color or "current" to inherit CSS color */
  color?: "navy" | "white" | "current";
}

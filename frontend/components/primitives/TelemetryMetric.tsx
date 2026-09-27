"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * TelemetryMetric Primitive
 * Formats numbers with font-variant-numeric: tabular-nums to prevent Cumulative Layout Shift (CLS = 0).
 * Maximum 3-4 metrics per card (Data density cap).
 */

interface TelemetryMetricProps {
  label: string;
  value: string | number;
  unit?: string;
  delta?: number;
  deltaLabel?: string;
  trend?: "up" | "down" | "neutral";
  statusColor?: "emerald" | "indigo" | "rose" | "amber" | "slate";
  className?: string;
}

export const TelemetryMetric: React.FC<TelemetryMetricProps> = ({
  label,
  value,
  unit,
  delta,
  deltaLabel,
  trend,
  statusColor = "indigo",
  className,
}) => {
  const colorStyles = {
    indigo: "text-indigo-600 bg-indigo-50 border-indigo-200/70",
    emerald: "text-emerald-600 bg-emerald-50 border-emerald-200/70",
    rose: "text-rose-600 bg-rose-50 border-rose-200/70",
    amber: "text-amber-600 bg-amber-50 border-amber-200/70",
    slate: "text-slate-700 bg-slate-100 border-slate-200",
  };

  return (
    <div
      className={cn(
        "flex flex-col p-3 rounded-xl bg-surface border border-border-subtle",
        className
      )}
    >
      <span className="text-[11px] font-medium uppercase tracking-wider text-content-muted">
        {label}
      </span>

      <div className="flex items-baseline gap-1.5 mt-1">
        <span className="text-xl sm:text-2xl font-bold tracking-tight text-content-primary tabular-nums">
          {value}
        </span>
        {unit && (
          <span className="text-xs font-mono font-medium text-content-muted">
            {unit}
          </span>
        )}
      </div>

      {(delta !== undefined || deltaLabel) && (
        <div className="flex items-center gap-1 mt-1.5">
          <span
            className={cn(
              "inline-flex items-center gap-0.5 text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded border tabular-nums",
              colorStyles[statusColor]
            )}
          >
            {trend === "up" && <TrendingUp className="h-3 w-3" />}
            {trend === "down" && <TrendingDown className="h-3 w-3" />}
            {trend === "neutral" && <Minus className="h-3 w-3" />}
            {delta !== undefined && (delta > 0 ? `+${delta}%` : `${delta}%`)}
            {deltaLabel && ` ${deltaLabel}`}
          </span>
        </div>
      )}
    </div>
  );
};

export default TelemetryMetric;

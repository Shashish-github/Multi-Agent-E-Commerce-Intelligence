"use client";

import { ReactNode } from "react";
import clsx from "clsx";

interface MetricCardProps {
  icon: ReactNode;
  label: string;
  value: string | number;
  color?: "blue" | "green" | "yellow" | "red" | "purple";
  subtitle?: string;
}

const colorClasses = {
  blue: "text-accent-blue",
  green: "text-accent-green",
  yellow: "text-accent-yellow",
  red: "text-accent-red",
  purple: "text-accent-purple",
};

export function MetricCard({
  icon,
  label,
  value,
  color = "blue",
  subtitle,
}: MetricCardProps) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-2">
        <div className={clsx("opacity-70", colorClasses[color])}>{icon}</div>
        <span className="card-header mb-0">{label}</span>
      </div>
      <div className={clsx("metric-value", colorClasses[color])}>{value}</div>
      {subtitle && (
        <div className="text-xs text-text-muted mt-1">{subtitle}</div>
      )}
    </div>
  );
}

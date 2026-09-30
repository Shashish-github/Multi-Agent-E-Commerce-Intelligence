"use client";

import { AlertTriangle, CheckCircle, XCircle, Clock } from "lucide-react";
import clsx from "clsx";

interface Event {
  id: string;
  event_type: string;
  severity: string;
  confidence: number;
  occurred_at: string;
  status: string;
  explanation?: string;
}

const severityConfig: Record<string, { color: string; icon: ReactNode }> = {
  CRITICAL: { color: "badge-red", icon: <AlertTriangle className="h-3 w-3" /> },
  WARNING: { color: "badge-yellow", icon: <AlertTriangle className="h-3 w-3" /> },
  INFO: { color: "badge-blue", icon: <Clock className="h-3 w-3" /> },
};

export function EventTimeline({ events }: { events: Event[] }) {
  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted">
        <CheckCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No events detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-[400px] overflow-y-auto">
      {events.map((event) => {
        const sev = severityConfig[event.severity] || severityConfig.INFO;
        return (
          <div
            key={event.id}
            className={clsx(
              "bg-bg-tertiary rounded-lg p-3 border border-border",
              "hover:border-accent-blue/30 transition-colors cursor-pointer",
              event.status === "ACKNOWLEDGED" && "opacity-60"
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={clsx("badge", sev.color)}>
                  {sev.icon}
                  {event.severity}
                </span>
                <span className="text-sm font-medium">{event.event_type}</span>
              </div>
              <span className="text-xs text-text-muted font-mono">
                {(event.confidence * 100).toFixed(0)}%
              </span>
            </div>
            {event.explanation && (
              <p className="text-xs text-text-secondary mt-1 line-clamp-2">
                {event.explanation}
              </p>
            )}
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-text-muted font-mono">
                {new Date(event.occurred_at).toLocaleTimeString()}
              </span>
              <span
                className={clsx(
                  "text-xs",
                  event.status === "NEW" && "text-accent-yellow",
                  event.status === "ACKNOWLEDGED" && "text-accent-green",
                  event.status === "DISMISSED" && "text-text-muted"
                )}
              >
                {event.status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

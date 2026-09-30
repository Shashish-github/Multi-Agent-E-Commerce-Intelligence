"use client";

import { Camera, Wifi, WifiOff, AlertTriangle } from "lucide-react";
import clsx from "clsx";

interface CameraHealthItem {
  id: string;
  name: string;
  status: string;
  enabled: boolean;
}

const statusConfig: Record<string, { color: string; icon: ReactNode; label: string }> = {
  ONLINE: {
    color: "badge-green",
    icon: <Wifi className="h-3 w-3" />,
    label: "Online",
  },
  OFFLINE: {
    color: "badge-red",
    icon: <WifiOff className="h-3 w-3" />,
    label: "Offline",
  },
  DEGRADED: {
    color: "badge-yellow",
    icon: <AlertTriangle className="h-3 w-3" />,
    label: "Degraded",
  },
};

export function CameraHealthGrid({ cameras }: { cameras: CameraHealthItem[] }) {
  if (cameras.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted">
        <Camera className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No cameras configured</p>
        <p className="text-sm mt-1">Add a camera to start monitoring</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {cameras.map((camera) => {
        const status = statusConfig[camera.status] || statusConfig.OFFLINE;
        return (
          <div
            key={camera.id}
            className={clsx(
              "bg-bg-tertiary rounded-lg p-3 border border-border",
              "hover:border-accent-blue/50 transition-colors cursor-pointer",
              !camera.enabled && "opacity-50"
            )}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Camera className="h-4 w-4 text-text-secondary" />
                <span className="text-sm font-medium truncate">
                  {camera.name}
                </span>
              </div>
              <span className={clsx("badge flex items-center gap-1", status.color)}>
                {status.icon}
                {status.label}
              </span>
            </div>
            <div className="text-xs text-text-muted font-mono">{camera.id.slice(0, 8)}</div>
          </div>
        );
      })}
    </div>
  );
}

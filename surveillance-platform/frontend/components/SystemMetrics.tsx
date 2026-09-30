"use client";

import { Cpu, Gauge, Timer, Activity, BarChart3 } from "lucide-react";

export function SystemMetrics() {
  return (
    <div className="card">
      <div className="card-header flex items-center gap-2">
        <BarChart3 className="h-4 w-4" />
        System Performance
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-text-muted text-xs mb-1">
            <Gauge className="h-3 w-3" />
            FPS
          </div>
          <div className="metric-value text-accent-green text-lg">--</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-text-muted text-xs mb-1">
            <Timer className="h-3 w-3" />
            Detection Latency
          </div>
          <div className="metric-value text-accent-blue text-lg">-- ms</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-text-muted text-xs mb-1">
            <Activity className="h-3 w-3" />
            Tracking Latency
          </div>
          <div className="metric-value text-accent-yellow text-lg">-- ms</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-text-muted text-xs mb-1">
            <Cpu className="h-3 w-3" />
            CPU Usage
          </div>
          <div className="metric-value text-accent-purple text-lg">--%</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-text-muted text-xs mb-1">
            <Activity className="h-3 w-3" />
            Memory
          </div>
          <div className="metric-value text-accent-red text-lg">-- MB</div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { BarChart3, TrendingUp, Clock, Camera } from "lucide-react";
import { getAnalyticsSummary, getEventsOverTime, getCameraHealth } from "@/lib/api";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<any>(null);
  const [eventsOverTime, setEventsOverTime] = useState<any[]>([]);
  const [cameras, setCameras] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      getAnalyticsSummary(),
      getEventsOverTime(24),
      getCameraHealth(),
    ])
      .then(([s, e, c]) => {
        setSummary(s);
        setEventsOverTime(e);
        setCameras(c);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <h1 className="text-2xl font-bold flex items-center gap-2 mb-6">
        <BarChart3 className="h-6 w-6 text-accent-purple" />
        Analytics
      </h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card">
          <div className="card-header">Total Events</div>
          <div className="metric-value text-accent-blue">{summary?.total_events || 0}</div>
        </div>
        <div className="card">
          <div className="card-header">Active Cameras</div>
          <div className="metric-value text-accent-green">{summary?.active_cameras || 0}</div>
        </div>
        <div className="card">
          <div className="card-header">Total Tracks</div>
          <div className="metric-value text-accent-yellow">{summary?.total_tracks || 0}</div>
        </div>
        <div className="card">
          <div className="card-header">Avg Confidence</div>
          <div className="metric-value text-accent-purple">
            {((summary?.avg_confidence || 0) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Events by Type */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Events by Type
          </div>
          <div className="space-y-3">
            {Object.entries(summary?.events_by_type || {}).map(([type, count]) => (
              <div key={type} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="text-sm">{type}</div>
                  <div className="w-full bg-bg-tertiary rounded-full h-2 mt-1">
                    <div
                      className="bg-accent-blue rounded-full h-2"
                      style={{
                        width: `${Math.min(100, ((count as number) / Math.max(summary?.total_events || 1, 1)) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
                <span className="font-mono font-bold text-sm">{count as number}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Events Over Time */}
        <div className="card">
          <div className="card-header flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Events Over Time (24h)
          </div>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {eventsOverTime.map((item: any) => (
              <div key={item.hour} className="flex items-center gap-3">
                <span className="text-xs text-text-muted font-mono w-20">
                  {new Date(item.hour).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
                <div className="flex-1 bg-bg-tertiary rounded-full h-3">
                  <div
                    className="bg-accent-yellow rounded-full h-3 transition-all"
                    style={{
                      width: `${Math.min(100, (item.count / Math.max(...eventsOverTime.map((e: any) => e.count), 1)) * 100)}%`,
                    }}
                  />
                </div>
                <span className="font-mono text-xs w-8 text-right">{item.count}</span>
              </div>
            ))}
            {eventsOverTime.length === 0 && (
              <div className="text-center py-8 text-text-muted text-sm">
                No event data for the last 24 hours
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

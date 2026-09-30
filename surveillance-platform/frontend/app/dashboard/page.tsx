"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Camera,
  Clock,
  Eye,
  Shield,
  TrendingUp,
  Zap,
} from "lucide-react";
import { getAnalyticsSummary, getCameraHealth } from "@/lib/api";
import { MetricCard } from "@/components/MetricCard";
import { CameraHealthGrid } from "@/components/CameraHealthGrid";
import { EventTimeline } from "@/components/EventTimeline";
import { SystemMetrics } from "@/components/SystemMetrics";

interface AnalyticsSummary {
  total_events: number;
  events_by_type: Record<string, number>;
  events_by_severity: Record<string, number>;
  active_cameras: number;
  total_tracks: number;
  avg_confidence: number;
  uptime_hours: number;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [cameras, setCameras] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [summaryData, cameraData] = await Promise.all([
          getAnalyticsSummary(),
          getCameraHealth(),
        ]);
        setSummary(summaryData);
        setCameras(cameraData);
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-text-muted">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <header className="border-b border-border bg-bg-secondary px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="h-6 w-6 text-accent-blue" />
            <h1 className="text-xl font-bold">Surveillance Platform</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <Activity className="h-4 w-4 text-green-400" />
              <span>System Active</span>
            </div>
            <div className="text-sm text-text-muted font-mono">
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </header>

      <main className="p-6">
        {/* Top Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <MetricCard
            icon={<Camera className="h-5 w-5" />}
            label="Active Cameras"
            value={summary?.active_cameras || 0}
            color="blue"
          />
          <MetricCard
            icon={<AlertTriangle className="h-5 w-5" />}
            label="Total Events"
            value={summary?.total_events || 0}
            color="yellow"
          />
          <MetricCard
            icon={<Eye className="h-5 w-5" />}
            label="Active Tracks"
            value={summary?.total_tracks || 0}
            color="green"
          />
          <MetricCard
            icon={<TrendingUp className="h-5 w-5" />}
            label="Avg Confidence"
            value={`${((summary?.avg_confidence || 0) * 100).toFixed(1)}%`}
            color="purple"
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Camera Health - takes 2 columns */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <Camera className="h-4 w-4" />
                Camera Health
              </div>
              <CameraHealthGrid cameras={cameras} />
            </div>
          </div>

          {/* Event Summary */}
          <div>
            <div className="card">
              <div className="card-header flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Events by Severity
              </div>
              <div className="space-y-3">
                {Object.entries(summary?.events_by_severity || {}).map(
                  ([severity, count]) => (
                    <div
                      key={severity}
                      className="flex items-center justify-between"
                    >
                      <span className="badge badge-yellow">{severity}</span>
                      <span className="font-mono font-bold">{count}</span>
                    </div>
                  )
                )}
                {Object.keys(summary?.events_by_severity || {}).length === 0 && (
                  <div className="text-text-muted text-sm text-center py-4">
                    No events recorded
                  </div>
                )}
              </div>
            </div>

            <div className="card mt-4">
              <div className="card-header flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Uptime
              </div>
              <div className="metric-value text-accent-green">
                {summary?.uptime_hours
                  ? `${Math.floor(summary.uptime_hours / 24)}d ${Math.floor(summary.uptime_hours % 24)}h`
                  : "0h"}
              </div>
            </div>
          </div>
        </div>

        {/* System Performance */}
        <div className="mt-6">
          <SystemMetrics />
        </div>
      </main>
    </div>
  );
}

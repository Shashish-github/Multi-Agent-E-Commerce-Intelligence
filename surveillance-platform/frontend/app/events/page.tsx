"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Search, Filter, ChevronDown } from "lucide-react";
import { getEvents, updateEventStatus } from "@/lib/api";
import { EventTimeline } from "@/components/EventTimeline";

interface EventListResponse {
  items: any[];
  total: number;
  page: number;
  page_size: number;
}

export default function EventsPage() {
  const [events, setEvents] = useState<EventListResponse | null>(null);
  const [filters, setFilters] = useState({
    event_type: "",
    severity: "",
    status: "",
    page: 1,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchEvents() {
      try {
        setLoading(true);
        const params: Record<string, unknown> = { page: filters.page };
        if (filters.event_type) params.event_type = filters.event_type;
        if (filters.severity) params.severity = filters.severity;
        if (filters.status) params.status = filters.status;
        const data = await getEvents(params);
        setEvents(data);
      } catch (error) {
        console.error("Failed to fetch events:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchEvents();
  }, [filters]);

  const handleAcknowledge = async (eventId: string) => {
    try {
      await updateEventStatus(eventId, "ACKNOWLEDGED");
      setEvents((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((e: any) =>
            e.id === eventId ? { ...e, status: "ACKNOWLEDGED" } : e
          ),
        };
      });
    } catch (error) {
      console.error("Failed to acknowledge event:", error);
    }
  };

  return (
    <div className="min-h-screen bg-bg-primary p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertTriangle className="h-6 w-6 text-accent-yellow" />
          Events
        </h1>
        <div className="text-sm text-text-muted">
          {events?.total || 0} total events
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="h-4 w-4 text-text-muted" />
          <span className="card-header mb-0">Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <select
            className="input-field"
            value={filters.event_type}
            onChange={(e) => setFilters({ ...filters, event_type: e.target.value, page: 1 })}
          >
            <option value="">All Types</option>
            <option value="RESTRICTED_ENTRY">Restricted Entry</option>
            <option value="LOITERING">Loitering</option>
            <option value="LINE_CROSSING">Line Crossing</option>
            <option value="CROWD">Crowd</option>
            <option value="ANOMALY">Anomaly</option>
          </select>
          <select
            className="input-field"
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value, page: 1 })}
          >
            <option value="">All Severities</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="CRITICAL">Critical</option>
          </select>
          <select
            className="input-field"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
          <div className="text-sm text-text-muted flex items-center">
            Page {events?.page || 1} of {Math.ceil((events?.total || 0) / 20)}
          </div>
        </div>
      </div>

      {/* Event List */}
      <div className="card">
        {loading ? (
          <div className="text-center py-8 text-text-muted">Loading events...</div>
        ) : events?.items.length === 0 ? (
          <div className="text-center py-8 text-text-muted">No events match your filters</div>
        ) : (
          <div className="space-y-3">
            {events?.items.map((event: any) => (
              <div
                key={event.id}
                className="bg-bg-tertiary rounded-lg p-4 border border-border hover:border-accent-blue/30 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`badge ${
                      event.severity === "CRITICAL" ? "badge-red" :
                      event.severity === "WARNING" ? "badge-yellow" : "badge-blue"
                    }`}>
                      {event.severity}
                    </span>
                    <span className="font-medium">{event.event_type}</span>
                  </div>
                  <span className="text-sm font-mono text-text-muted">
                    {(event.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                {event.metadata?.explanation && (
                  <p className="text-sm text-text-secondary mb-2">
                    {event.metadata.explanation}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <div className="text-xs text-text-muted font-mono">
                    {new Date(event.occurred_at).toLocaleString()}
                  </div>
                  <div className="flex gap-2">
                    {event.status === "NEW" && (
                      <button
                        onClick={() => handleAcknowledge(event.id)}
                        className="text-xs text-accent-green hover:underline"
                      >
                        Acknowledge
                      </button>
                    )}
                    <a
                      href={`/events/${event.id}`}
                      className="text-xs text-accent-blue hover:underline"
                    >
                      View Details
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

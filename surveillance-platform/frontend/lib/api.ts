/**
 * API client for the surveillance platform backend.
 */
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach auth token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Auth ──
export async function login(email: string, password: string) {
  const { data } = await api.post("/api/v1/auth/login", { email, password });
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return data;
}

export async function register(email: string, password: string, role = "OPERATOR") {
  const { data } = await api.post("/api/v1/auth/register", { email, password, role });
  return data;
}

export async function getMe() {
  const { data } = await api.get("/api/v1/auth/me");
  return data;
}

// ── Cameras ──
export async function getCameras() {
  const { data } = await api.get("/api/v1/cameras");
  return data;
}

export async function getCamera(id: string) {
  const { data } = await api.get(`/api/v1/cameras/${id}`);
  return data;
}

export async function createCamera(payload: {
  name: string;
  source_type: string;
  source_reference: string;
  location_label?: string;
}) {
  const { data } = await api.post("/api/v1/cameras", payload);
  return data;
}

export async function updateCamera(id: string, payload: Record<string, unknown>) {
  const { data } = await api.patch(`/api/v1/cameras/${id}`, payload);
  return data;
}

export async function testCamera(id: string) {
  const { data } = await api.post(`/api/v1/cameras/${id}/test`);
  return data;
}

export async function getCameraStatus(id: string) {
  const { data } = await api.get(`/api/v1/cameras/${id}/status`);
  return data;
}

// ── Zones ──
export async function getZones(cameraId: string) {
  const { data } = await api.get(`/api/v1/cameras/${cameraId}/zones`);
  return data;
}

export async function createZone(cameraId: string, payload: {
  name: string;
  type: string;
  polygon: Array<{ x: number; y: number }>;
}) {
  const { data } = await api.post(`/api/v1/cameras/${cameraId}/zones`, payload);
  return data;
}

// ── Rules ──
export async function getRules(cameraId: string) {
  const { data } = await api.get(`/api/v1/cameras/${cameraId}/rules`);
  return data;
}

export async function createRule(cameraId: string, payload: {
  rule_type: string;
  configuration: Record<string, unknown>;
}) {
  const { data } = await api.post(`/api/v1/cameras/${cameraId}/rules`, payload);
  return data;
}

// ── Events ──
export async function getEvents(params: Record<string, unknown> = {}) {
  const { data } = await api.get("/api/v1/events", { params });
  return data;
}

export async function getEvent(id: string) {
  const { data } = await api.get(`/api/v1/events/${id}`);
  return data;
}

export async function updateEventStatus(id: string, status: string) {
  const { data } = await api.patch(`/api/v1/events/${id}`, { status });
  return data;
}

// ── Analytics ──
export async function getAnalyticsSummary() {
  const { data } = await api.get("/api/v1/analytics/summary");
  return data;
}

export async function getEventsOverTime(hours = 24) {
  const { data } = await api.get("/api/v1/analytics/events-over-time", { params: { hours } });
  return data;
}

export async function getCameraHealth() {
  const { data } = await api.get("/api/v1/analytics/camera-health");
  return data;
}

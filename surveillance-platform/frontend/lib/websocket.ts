/**
 * WebSocket client for real-time detection updates and alerts.
 */

type WSEventType = "detection_update" | "alert" | "system_status";

interface WSEvent {
  type: WSEventType;
  timestamp: string;
  [key: string]: unknown;
}

type WSCallback = (event: WSEvent) => void;

export class SurveillanceWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private cameraId: string;
  private callbacks: WSCallback[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private _isConnected = false;

  constructor(cameraId: string) {
    const wsBase = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    this.url = `${wsBase}/ws/cameras/${cameraId}`;
    this.cameraId = cameraId;
  }

  connect(token: string) {
    try {
      this.ws = new WebSocket(`${this.url}?token=${token}`);

      this.ws.onopen = () => {
        this._isConnected = true;
        this.reconnectAttempts = 0;
        console.log(`[WS] Connected to camera ${this.cameraId}`);
      };

      this.ws.onmessage = (event) => {
        try {
          const data: WSEvent = JSON.parse(event.data);
          this.callbacks.forEach((cb) => cb(data));
        } catch (e) {
          console.error("[WS] Failed to parse message:", e);
        }
      };

      this.ws.onclose = () => {
        this._isConnected = false;
        console.log(`[WS] Disconnected from camera ${this.cameraId}`);
        this.reconnect();
      };

      this.ws.onerror = (error) => {
        console.error(`[WS] Error for camera ${this.cameraId}:`, error);
      };
    } catch (e) {
      console.error(`[WS] Connection failed:`, e);
      this.reconnect();
    }
  }

  private reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[WS] Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    setTimeout(() => {
      const token = typeof window !== "undefined"
        ? localStorage.getItem("access_token") || ""
        : "";
      this.connect(token);
    }, delay);
  }

  onMessage(callback: WSCallback) {
    this.callbacks.push(callback);
    return () => {
      this.callbacks = this.callbacks.filter((cb) => cb !== callback);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this._isConnected = false;
  }

  get isConnected() {
    return this._isConnected;
  }
}

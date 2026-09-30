# API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints except `/auth/login` and `/auth/register` require a Bearer token:
```
Authorization: Bearer <access_token>
```

## Authentication

### POST /auth/login
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### POST /auth/register
Create a new user account.

### GET /auth/me
Get current user profile.

### POST /auth/refresh
Exchange refresh token for new tokens.

---

## Cameras

### GET /cameras
List all cameras.

### POST /cameras
Register a new camera.

**Request:**
```json
{
  "name": "Main Entrance",
  "source_type": "rtsp",
  "source_reference": "rtsp://192.168.1.100:554/stream",
  "location_label": "Building A"
}
```

### GET /cameras/{id}
Get camera details.

### PATCH /cameras/{id}
Update camera metadata.

### DELETE /cameras/{id}
Delete camera and associated data.

### POST /cameras/{id}/test
Test camera source connectivity.

### GET /cameras/{id}/status
Get camera health and processing metrics.

---

## Zones

### GET /cameras/{camera_id}/zones
List zones for a camera.

### POST /cameras/{camera_id}/zones
Create a new zone.

**Request:**
```json
{
  "name": "Restricted Area",
  "type": "restricted",
  "polygon": [
    {"x": 100, "y": 100},
    {"x": 400, "y": 100},
    {"x": 400, "y": 300},
    {"x": 100, "y": 300}
  ]
}
```

### PATCH /zones/{id}
### DELETE /zones/{id}

---

## Rules

### GET /cameras/{camera_id}/rules
List rules for a camera.

### POST /cameras/{camera_id}/rules
Create an event rule.

**Request:**
```json
{
  "rule_type": "dwell",
  "configuration": {
    "zone_id": "...",
    "dwell_threshold_seconds": 30,
    "confidence_threshold": 0.5
  }
}
```

---

## Events

### GET /events
Paginated event search with filters:
- `camera_id` — Filter by camera
- `event_type` — RESTRICTED_ENTRY, LOITERING, LINE_CROSSING, CROWD, ANOMALY
- `severity` — INFO, WARNING, CRITICAL
- `status` — NEW, ACKNOWLEDGED, DISMISSED
- `start_date`, `end_date` — Date range
- `page`, `page_size` — Pagination

### GET /events/{id}
Get event details with explanation.

### GET /events/{id}/evidence`
Get evidence reference (clip/frame path).

### PATCH /events/{id}
Update event status (acknowledge/dismiss).

---

## Analytics

### GET /analytics/summary
Aggregated operational metrics.

### GET /analytics/events-over-time?hours=24
Event counts bucketed by hour.

### GET /analytics/camera-health`
Health status for all cameras.

---

## WebSocket

### ws://localhost:8000/ws/cameras/{camera_id}?token=<jwt>

**Messages:**
```json
{
  "type": "detection_update",
  "timestamp": "2024-01-01T00:00:00Z",
  "tracks": [...]
}
```

```json
{
  "type": "alert",
  "event_id": "...",
  "event_type": "RESTRICTED_ENTRY",
  "confidence": 0.91
}
```

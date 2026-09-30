# Security

## Authentication & Authorization

- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- Role-based access control: ADMIN and OPERATOR
- All camera/event resources are authorization-checked server-side

## Data Protection

- Camera credentials are never stored in plaintext
- Evidence access is controlled per user
- Sensitive configuration is in environment variables, not code

## Privacy

**The system does NOT implement:**
- Facial recognition
- Biometric identification
- Demographic inference
- Persistent personal identification

**The system focuses on:**
- Object/scene-level operational safety
- Scene-level behavior analysis
- Anomalous pattern detection
- Track IDs are internal identifiers, not human identities

## Infrastructure

- Rate limiting on API endpoints
- Input validation on all endpoints
- CORS configuration for allowed origins
- Secure WebSocket authentication
- Encrypted transport (TLS in production)
- Secret management via environment variables
- Structured audit logging

## Evidence Retention

- Configurable retention period (default: 30 days)
- Automatic cleanup of expired evidence
- Access-controlled evidence retrieval
- No unnecessary raw video storage

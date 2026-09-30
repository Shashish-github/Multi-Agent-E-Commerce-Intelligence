# Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+
- FFmpeg

## Quick Start with Docker

```bash
# Clone and enter the project
cd surveillance-platform

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations and seed data
docker-compose exec backend python -m database.seed.seed_data
```

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit ../.env with your local settings

# Start PostgreSQL and Redis (or use Docker)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Seed initial data
python -m database.seed.seed_data

# Start the backend
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Testing

```bash
# Backend tests
cd backend
pip install pytest pytest-asyncio aiosqlite httpx
pytest

# Frontend tests
cd frontend
npm test
```

## Demo Data

The seed script creates:
- Admin: `admin@surveillance.local` / `changeme`
- Operator: `operator@surveillance.local` / `operator123`
- Sample camera: "Main Entrance Camera" (video file source)
- Sample restricted zone
- Sample dwell rule

## Environment Variables

See `.env.example` for all configurable options. Key settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://surveillance:surveillance@localhost:5432/surveillance` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `YOLO_MODEL` | YOLO model file | `yolov8n.pt` |
| `YOLO_DEVICE` | Inference device | `cpu` |
| `FRAME_BUFFER_SIZE` | Max frames in buffer | `64` |
| `FRAME_SKIP_INTERVAL` | Detection frequency | `2` |

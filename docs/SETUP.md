# Local Setup & Deployment Guide

## Prerequisites
- **Python 3.10+** (Tested on Python 3.11 / 3.13)
- **Node.js 18+** & **npm**
- **Docker & Docker Compose** (Optional, for full containerized stack)

---

## 1. Quick Start (Local Development)

### 1.1 Backend Setup
1. Navigate to the repository root and install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Start the FastAPI backend server:
   ```bash
   python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
   ```
   *The server will automatically initialize the database schema and seed the catalog from `seed_data/catalog.json` on first run.*
   - API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### 1.2 Frontend Setup
1. Open a new terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open your browser at `http://localhost:5173` (or the URL printed by Vite).

---

## 2. Running Test Suite & Evaluation

### 2.1 Backend Tests
Run the comprehensive Pytest suite:
```bash
pytest backend/tests/ -v
```

### 2.2 100-Query Benchmark Evaluation
Run the reproducible evaluation suite:
```bash
python evaluation/run_benchmarks.py
```
This evaluates the multi-agent pipeline against keyword and single-model baselines and updates `docs/EVALUATION.md`.

---

## 3. Docker Compose Deployment

To deploy the entire production stack (PostgreSQL + pgvector, Redis, FastAPI Backend, Nginx/React Frontend) with a single command:

```bash
docker-compose up --build
```

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000/api/v1`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`

# AquaGuard Production Deployment Guide

This guide details step-by-step procedures for deploying **AquaGuard** in production.

---

## 1. Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Python 3.11+
- Node.js 20+
- Domain name with SSL/TLS certificate (for Nginx HTTPS reverse proxy)

---

## 2. Docker Deployment

### Step 1: Environment Setup
Copy the production environment file:
```bash
cp .env.production .env
```

### Step 2: Build & Start Containers
Launch PostGIS, FastAPI backend, Next.js frontend, and Nginx reverse proxy:
```bash
docker compose -f deployment/docker-compose.yml up --build -d
```

### Step 3: Run Database Migrations
Apply Alembic database migrations:
```bash
docker exec -it aquaguard_prod_backend alembic upgrade head
```

### Step 4: Verify Deployment
Check health status endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

---

## 3. SIH Demo Mode Execution

To run AquaGuard in offline hackathon demonstration mode using real historical snapshots:

```bash
python scripts/seed_demo_data.py
```
This loads real previously collected satellite observation snapshots tagged with `"Data snapshot: 2026-08-14"`.

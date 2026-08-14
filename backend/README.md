# AquaGuard Production FastAPI Backend

Production-ready asynchronous FastAPI backend providing REST APIs for water body surveillance, PostGIS geospatial queries, satellite & climate observations, and AI/ML restoration priority predictions.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn
- **Database**: PostgreSQL with PostGIS extension (SQLAlchemy + GeoAlchemy2 ORM)
- **Validation**: Pydantic v2
- **AI/ML**: Scikit-learn, Joblib (AquaGuard ML Model)
- **Testing**: Pytest & HTTPX
- **Migrations**: Alembic

---

## 🚀 Getting Started

### 1. Environment Setup
```bash
cp backend/.env.example backend/.env
pip install -r backend/requirements.txt
```

### 2. Run Local Development Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

Access Interactive API Documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Pytest Unit Tests

```bash
pytest backend/tests/
```

---

## 🐳 Docker Deployment

```bash
docker build -t aquaguard-backend -f backend/Dockerfile .
docker run -p 8000:8000 aquaguard-backend
```

# Quick Start Guide - Backend Developer

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.11+
- PostgreSQL 15 (or use Docker)
- Redis (or use Docker)

---

## Option 1: Docker (Easiest) ⭐ RECOMMENDED

```bash
# Navigate to project
cd c:\Users\HP\PycharmProjects\cpe

# Start everything
docker-compose up

# That's it! API is running at http://localhost:5000
```

The Docker Compose will automatically:

- Start PostgreSQL on port 5432
- Start Redis on port 6379
- Run database migrations
- Seed initial data
- Start Flask app on port 5000

---

## Option 2: Local Development

### Step 1: Install Dependencies

```bash
# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Set Up Database

**Option A: Use PostgreSQL**

```bash
# Install PostgreSQL and create database
createdb nexus_platform

# Update .env file
# DATABASE_URL=postgresql://username:password@localhost/nexus_platform
```

**Option B: Use SQLite (Development)**

```bash
# Nothing to install - SQLite is built-in
# The app will create data-dev.sqlite automatically
```

### Step 3: Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your settings (optional for SQLite)
```

### Step 4: Initialize Database

```bash
# Run initialization script
python -c "from backend.init_db import init_db; init_db()"
```

You should see:

```
✓ Database tables created
✓ Seeded 8 model assumptions
✓ Seeded 3 example scenarios
✓ Database initialized successfully!
```

### Step 5: Start the Server

```bash
python run.py
```

You should see:

```
* Running on http://127.0.0.1:5000
```

---

## Test the API

### Using Browser

Open: http://localhost:5000/api/models/info

### Using curl

```bash
# Get all scenarios
curl http://localhost:5000/api/scenarios

# Get model info
curl http://localhost:5000/api/models/info

# Create a scenario
curl -X POST http://localhost:5000/api/scenarios \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test\",\"parameters\":{\"renewable_energy_share\":0.8}}"
```

---

## Run Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=backend

# Specific test file
pytest backend/tests/test_scenarios.py

# Watch mode (install pytest-watch)
ptw
```

---

## Project Structure (What You Built)

```
backend/
├── app.py                    # Flask app factory with caching
├── config.py                 # PostgreSQL + Redis configuration
├── init_db.py                # Database seeding script
├── models/
│   └── scenario.py          # Scenario, ModelAssumption models
├── routes/
│   ├── scenarios.py         # 12 scenario endpoints
│   └── models.py            # 4 model info endpoints
├── services/
│   ├── model_service.py     # Nexus calculations + sensitivity
│   ├── cache_service.py     # Redis caching layer
│   └── export_service.py    # CSV/JSON/TXT exports
├── utils/
│   ├── validators.py        # Parameter validation
│   └── explainer.py         # What-changed explanations
└── tests/
    ├── test_scenarios.py    # 15+ API tests
    └── test_models.py       # 6+ model tests
```

---

## Key Files to Know

| File                                | Purpose                               |
| ----------------------------------- | ------------------------------------- |
| `run.py`                            | Start the application                 |
| `backend/config.py`                 | Environment configuration             |
| `backend/routes/scenarios.py`       | Main API endpoints                    |
| `backend/services/model_service.py` | Nexus model calculations              |
| `.env`                              | Environment variables (don't commit!) |

---

## Common Commands

```bash
# Start server
python run.py

# Run tests
pytest

# Initialize/reset database
python -c "from backend.init_db import init_db; init_db()"

# Python shell with app context
flask shell

# Database migrations (when you change models)
flask db migrate -m "Your change description"
flask db upgrade
```

---

## Next Steps for Development

### 1. Enhance the Model

Edit `backend/services/model_service.py`:

- Update coefficients with real data
- Add non-linear relationships
- Implement more feedback loops

### 2. Add New Endpoints

Edit `backend/routes/scenarios.py`:

```python
@bp.route('/your-endpoint', methods=['POST'])
def your_function():
    # Your logic here
    return jsonify(result)
```

### 3. Add Model Assumptions

```bash
curl -X POST http://localhost:5000/api/models/assumptions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Coefficient",
    "category": "food",
    "value": 2.5,
    "unit": "kg",
    "description": "Your description"
  }'
```

### 4. Update Tests

Edit `backend/tests/test_scenarios.py` and run:

```bash
pytest backend/tests/test_scenarios.py
```

---

## Troubleshooting

### Port Already in Use

```bash
# Windows: Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <process_id> /F
```

### Database Connection Error

- Check PostgreSQL is running: `psql -U postgres`
- Verify connection string in `.env`
- For Docker: `docker-compose ps` to check services

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Redis Connection Error

- Check Redis is running: `redis-cli ping`
- For Docker: Redis is included in docker-compose
- Fallback: Set `CACHE_TYPE=simple` in `.env` for in-memory cache

---

## Working with Your Team

### Frontend Developer Needs:

- **API Base URL**: `http://localhost:5000/api`
- **Documentation**: See `API_DOCUMENTATION.md`
- **CORS**: Already configured for `http://localhost:3000`

### Data Scientist Needs:

- **Model file**: `backend/services/model_service.py`
- **Current assumptions**: `GET /api/models/assumptions`
- **Test calculations**: Use `/api/scenarios` endpoint

### QA Tester Needs:

- **Run tests**: `pytest`
- **API docs**: `API_DOCUMENTATION.md`
- **Sample data**: 3 scenarios seeded automatically

---

## Production Deployment

### Quick Production Setup

1. **Set environment variables**:

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-postgres-url>
REDIS_URL=<production-redis-url>
```

2. **Use Gunicorn**:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

3. **Or use Docker**:

```bash
docker-compose up -d
```

---

## Resources

- **Full Documentation**: `README.md`
- **API Reference**: `API_DOCUMENTATION.md`
- **Implementation Plan**: See artifacts
- **Walkthrough**: See artifacts

---

## Support

For questions or issues:

1. Check the README.md
2. Review API_DOCUMENTATION.md
3. Check the test files for examples
4. Ask your team!

---

**Happy Coding! 🎉**

You now have a production-ready Flask backend for the Nexus Scenario Modeling Platform!

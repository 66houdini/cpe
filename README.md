# Interactive Nexus Scenario Modeling Platform - Backend

## Overview

This is the Flask-based backend for the Interactive Nexus Scenario Modeling Platform, a tool for analyzing trade-offs and synergies across food, energy, and water systems.

## Features

- ✅ **Scenario Management**: Create, read, update, delete (CRUD) scenarios
- ✅ **Advanced Modeling**: System dynamics model with feedback loops
- ✅ **Sensitivity Analysis**: One-at-a-time parameter variation analysis
- ✅ **Uncertainty Quantification**: Monte Carlo simulation with confidence intervals
- ✅ **Time-Series Projections**: 5-50 year forecasts
- ✅ **What-Changed Explanations**: Human-readable comparisons between scenarios
- ✅ **Caching**: Redis-based caching for expensive calculations
- ✅ **Data Export**: CSV, JSON, and text summary formats
- ✅ **API Documentation**: RESTful API with comprehensive endpoints

## Technology Stack

- **Framework**: Flask 3.0+
- **Database**: PostgreSQL 15 (SQLite for development)
- **Caching**: Redis 7
- **ORM**: SQLAlchemy
- **Scientific Computing**: NumPy, SciPy, Pandas
- **Testing**: Pytest

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Flask)
docker-compose up

# The API will be available at http://localhost:5000
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from backend.init_db import init_db; init_db()"

# Run development server
python run.py
```

## Project Structure

```
cpe/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # Flask app factory
│   ├── config.py              # Configuration
│   ├── init_db.py            # Database initialization
│   ├── models/
│   │   └── scenario.py       # Database models
│   ├── routes/
│   │   ├── scenarios.py      # Scenario endpoints
│   │   └── models.py         # Model info endpoints
│   ├── services/
│   │   ├── model_service.py  # Nexus calculations
│   │   ├── cache_service.py  # Caching logic
│   │   └── export_service.py # Data export
│   ├── utils/
│   │   ├── validators.py     # Parameter validation
│   │   └── explainer.py      # What-changed logic
│   └── tests/
│       ├── test_scenarios.py # API tests
│       └── test_models.py    # Model tests
├── run.py                     # Application entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

### Scenarios

| Method   | Endpoint              | Description          |
| -------- | --------------------- | -------------------- |
| `GET`    | `/api/scenarios`      | List all scenarios   |
| `POST`   | `/api/scenarios`      | Create new scenario  |
| `GET`    | `/api/scenarios/<id>` | Get scenario details |
| `PUT`    | `/api/scenarios/<id>` | Update scenario      |
| `DELETE` | `/api/scenarios/<id>` | Delete scenario      |

### Analysis

| Method | Endpoint                          | Description                  |
| ------ | --------------------------------- | ---------------------------- |
| `POST` | `/api/scenarios/compare`          | Compare multiple scenarios   |
| `POST` | `/api/scenarios/<id>/sensitivity` | Run sensitivity analysis     |
| `POST` | `/api/scenarios/what-changed`     | Explain scenario differences |
| `POST` | `/api/scenarios/<id>/projection`  | Get time-series projection   |

### Export

| Method | Endpoint                                 | Description            |
| ------ | ---------------------------------------- | ---------------------- |
| `GET`  | `/api/scenarios/<id>/export?format=csv`  | Export as CSV          |
| `GET`  | `/api/scenarios/<id>/export?format=json` | Export as JSON         |
| `GET`  | `/api/scenarios/<id>/export?format=txt`  | Export as text summary |
| `POST` | `/api/scenarios/compare/export`          | Export comparison      |

### Model Information

| Method | Endpoint                  | Description            |
| ------ | ------------------------- | ---------------------- |
| `GET`  | `/api/models/info`        | Get model card         |
| `GET`  | `/api/models/parameters`  | Get parameter metadata |
| `GET`  | `/api/models/assumptions` | List model assumptions |
| `POST` | `/api/models/assumptions` | Add model assumption   |

## API Usage Examples

### Create a Scenario

```bash
curl -X POST http://localhost:5000/api/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Transition",
    "description": "High renewable energy scenario",
    "parameters": {
      "food_production_intensity": 0.6,
      "renewable_energy_share": 0.8,
      "water_conservation_level": 0.7,
      "population_growth": 1.01
    }
  }'
```

### Run Sensitivity Analysis

```bash
curl -X POST http://localhost:5000/api/scenarios/1/sensitivity \
  -H "Content-Type: application/json" \
  -d '{
    "parameter": "renewable_energy_share"
  }'
```

### Compare Scenarios

```bash
curl -X POST http://localhost:5000/api/scenarios/compare \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_ids": [1, 2, 3]
  }'
```

### Export Scenario

```bash
# CSV export
curl http://localhost:5000/api/scenarios/1/export?format=csv > scenario.csv

# JSON export
curl http://localhost:5000/api/scenarios/1/export?format=json > scenario.json
```

## Model Parameters

| Parameter                   | Range       | Default | Description                            |
| --------------------------- | ----------- | ------- | -------------------------------------- |
| `food_production_intensity` | 0.0 - 1.0   | 0.5     | Agricultural intensification level     |
| `renewable_energy_share`    | 0.0 - 1.0   | 0.3     | Fraction of energy from renewables     |
| `water_conservation_level`  | 0.0 - 1.0   | 0.5     | Effectiveness of conservation measures |
| `population_growth`         | 0.95 - 1.10 | 1.01    | Annual population growth multiplier    |

## Output Metrics

- **Food Production**: Total food output (kg)
- **CO2 Emissions**: Total emissions (kg CO2)
- **Water Demand**: Total water consumption (liters)
- **Water Stress Index**: 0-1 scale, higher = more stress
- **Food Security Index**: 0-1 scale, higher = more secure
- **Energy Security Index**: 0-1 scale
- **Sustainability Score**: Overall 0-1 score

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_models.py

# Run specific test
pytest backend/tests/test_scenarios.py::TestScenarioAPI::test_create_scenario
```

## Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Revert migration
flask db downgrade
```

## Environment Variables

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nexus_platform
DEV_DATABASE_URL=sqlite:///data-dev.sqlite

# Redis Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Model Configuration
MC_SIMULATIONS=100
```

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Use PostgreSQL database
- [ ] Configure Redis cache
- [ ] Set `FLASK_ENV=production`
- [ ] Use WSGI server (Gunicorn)
- [ ] Set up HTTPS
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging
- [ ] Regular database backups

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Contributing

1. Create feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation
5. Submit pull request

## Team Roles

- **Backend Developer**: API development, model orchestration, caching **(You are here!)**
- **Data Scientist**: Enhance model calculations, calibrate parameters
- **UX Designer**: Frontend scenario composer
- **Docs/QA**: API documentation, testing

## License

Academic use only. See project documentation for details.

## Support

For questions or issues, contact the development team or open an issue in the project repository.

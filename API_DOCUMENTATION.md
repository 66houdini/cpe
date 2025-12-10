# API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. This may change in future versions.

## Response Format

All responses are in JSON format.

Success Response:

```json
{
  "data": {...}
}
```

Error Response:

```json
{
  "error": "Error message",
  "details": "Optional detailed information"
}
```

## Scenario Endpoints

### Create Scenario

**POST** `/scenarios`

Create a new scenario with parameters and get calculated results.

**Request Body:**

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "parameters": {
    "food_production_intensity": 0.0-1.0,
    "renewable_energy_share": 0.0-1.0,
    "water_conservation_level": 0.0-1.0,
    "population_growth": 0.95-1.10
  }
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "name": "Green Transition",
  "description": "High renewable scenario",
  "created_at": "2025-12-06T09:00:00Z",
  "updated_at": "2025-12-06T09:00:00Z",
  "parameters": {...},
  "results": {
    "food_production": 1020.5,
    "co2_emissions": 500.0,
    "water_demand": 3200.5,
    "water_stress_index": 0.320,
    "food_security_index": 0.850,
    "energy_security_index": 1.000,
    "sustainability_score": 0.725,
    "uncertainties": {
      "co2_emissions": {
        "p10": 450.0,
        "p50": 500.0,
        "p90": 550.0
      }
    }
  }
}
```

### Get All Scenarios

**GET** `/scenarios`

Retrieve all scenarios, ordered by creation date (newest first).

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Scenario 1",
    ...
  },
  {
    "id": 2,
    "name": "Scenario 2",
    ...
  }
]
```

### Get Single Scenario

**GET** `/scenarios/:id`

Retrieve a specific scenario by ID.

**Response:** `200 OK` or `404 Not Found`

### Update Scenario

**PUT** `/scenarios/:id`

Update scenario metadata or parameters. If parameters are updated, results are automatically recalculated.

**Request Body:**

```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "parameters": {...} // (optional, triggers recalculation)
}
```

**Response:** `200 OK`

### Delete Scenario

**DELETE** `/scenarios/:id`

Delete a scenario permanently.

**Response:** `204 No Content`

---

## Analysis Endpoints

### Compare Scenarios

**POST** `/scenarios/compare`

Compare multiple scenarios side-by-side.

**Request Body:**

```json
{
  "scenario_ids": [1, 2, 3]
}
```

**Response:** `200 OK`

```json
{
  "scenarios": [
    {scenario1_data},
    {scenario2_data},
    {scenario3_data}
  ],
  "metrics": {
    "co2_emissions": {
      "min": 400.0,
      "max": 600.0,
      "mean": 500.0,
      "values": [400.0, 500.0, 600.0]
    },
    "water_demand": {...},
    ...
  }
}
```

### Sensitivity Analysis

**POST** `/scenarios/:id/sensitivity`

Run sensitivity analysis on a scenario, varying one or all parameters.

**Request Body:**

```json
{
  "parameter": "renewable_energy_share" // optional, omit for all parameters
}
```

**Response:** `200 OK`

```json
{
  "baseline": {
    "parameters": {...},
    "results": {...}
  },
  "analysis": {
    "renewable_energy_share": {
      "variations": [
        {
          "parameter_value": 0.0,
          "results": {...}
        },
        {
          "parameter_value": 0.1,
          "results": {...}
        },
        ...
      ],
      "sensitivity_scores": {
        "co2_emissions": {
          "sensitivity": 0.456,
          "min": 300.0,
          "max": 800.0,
          "range": 500.0
        },
        ...
      }
    }
  }
}
```

### What Changed

**POST** `/scenarios/what-changed`

Explain the differences between two scenarios in human-readable format.

**Request Body:**

```json
{
  "scenario1_id": 1,
  "scenario2_id": 2
}
```

**Response:** `200 OK`

```json
{
  "scenario1": {
    "id": 1,
    "name": "Baseline"
  },
  "scenario2": {
    "id": 2,
    "name": "Green Transition"
  },
  "explanation": {
    "parameter_changes": [
      {
        "parameter": "renewable_energy_share",
        "parameter_name": "Renewable Energy Share",
        "old_value": 0.3,
        "new_value": 0.8,
        "change": 0.5,
        "percent_change": 166.7,
        "magnitude": "major",
        "description": "Renewable Energy Share increased by 166.7%"
      }
    ],
    "outcome_changes": [
      {
        "metric": "co2_emissions",
        "metric_name": "Co2 Emissions",
        "old_value": 600.0,
        "new_value": 400.0,
        "change": -200.0,
        "percent_change": -33.3,
        "is_improvement": true,
        "description": "Co2 Emissions decreased by 33.3%"
      }
    ],
    "key_insights": [
      "Increasing renewable energy share by 50% reduced CO2 emissions by 33.3%",
      "This scenario shows net positive outcomes across multiple sustainability metrics"
    ],
    "trade_offs": [
      {
        "improved": "Co2 Emissions",
        "worsened": "Water Demand",
        "description": "Improving co2 emissions came at the cost of water demand"
      }
    ]
  }
}
```

### Time-Series Projection

**POST** `/scenarios/:id/projection`

Project scenario impacts over time (1-50 years).

**Request Body:**

```json
{
  "years": 10
}
```

**Response:** `200 OK`

```json
{
  "parameters": {...},
  "years": 10,
  "projections": [
    {
      "year": 0,
      "results": {...}
    },
    {
      "year": 1,
      "results": {...}
    },
    ...
  ]
}
```

---

## Export Endpoints

### Export Scenario

**GET** `/scenarios/:id/export?format={csv|json|txt}`

Export scenario data in specified format.

**Query Parameters:**

- `format`: Export format (`csv`, `json`, or `txt`)

**Response:** File download

### Export Comparison

**POST** `/scenarios/compare/export`

Export scenario comparison.

**Request Body:**

```json
{
  "scenario_ids": [1, 2, 3],
  "format": "csv" // or "json"
}
```

**Response:** File download

---

## Model Information Endpoints

### Get Model Info

**GET** `/models/info`

Get model card with metadata, assumptions, and limitations.

**Response:** `200 OK`

```json
{
  "name": "Food-Energy-Water Nexus Model",
  "version": "1.0.0",
  "description": "...",
  "model_type": "System Dynamics with Monte Carlo",
  "categories": ["food", "energy", "water"],
  "assumptions": [...],
  "limitations": [...],
  "use_cases": [...]
}
```

### Get Parameters

**GET** `/models/parameters`

Get metadata for all model parameters.

**Response:** `200 OK`

```json
{
  "food_production_intensity": {
    "name": "Food Production Intensity",
    "description": "Level of agricultural intensification",
    "min": 0.0,
    "max": 1.0,
    "default": 0.5,
    "unit": "normalized",
    "category": "food",
    "impact": "Higher values increase food output but also water and energy demands"
  },
  ...
}
```

### Get Assumptions

**GET** `/models/assumptions`

List all model assumptions.

**Query Parameters:**

- `category`: Filter by category (optional)

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Food Water Coefficient",
    "category": "food",
    "value": 2.5,
    "unit": "liters/kg",
    "description": "Water required per kg of food"
  },
  ...
]
```

### Create Assumption

**POST** `/models/assumptions`

Add a new model assumption.

**Request Body:**

```json
{
  "name": "string (required)",
  "category": "string (optional)",
  "value": number (required),
  "unit": "string (optional)",
  "description": "string (optional)"
}
```

**Response:** `201 Created`

---

## Error Codes

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request (validation error)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in production.

## Caching

Expensive calculations (model results, sensitivity analysis, comparisons) are cached with the following TTLs:

- Model results: 1 hour
- Sensitivity analysis: 2 hours
- Comparisons: 30 minutes

Cache is automatically invalidated when scenario parameters change.

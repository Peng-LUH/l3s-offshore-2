# L3S Offshore 2

A Flask-based API for offshore wind farm installation planning and simulation.

**Key Features:**
- **Flask-RESTx** API with auto-generated Swagger documentation
- **Petri Net simulation** for installation scheduling (via gspn4py)
- **Process Mining** utilities for event log analysis
- **Docker** containerization for deployment
- Tox/pytest for testing

## Table of Contents
1. [Setup & Installation](#setup--installation)
2. [Running Locally](#running-locally)
3. [API Overview](#api-overview)
4. [API Architecture (Important)](#api-architecture)
5. [Deployment with Docker](#deployment-with-docker)
6. [Testing](#testing)


---

## Setup & Installation

```bash
# 1) Clone the repo
git clone https://github.com/Peng-LUH/l3s-offshore-2
cd l3s_offshore_2

# 2) Create & Activate Virtual Environment (optional, recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3) Install dependencies in editable mode
pip install -e .
```

If you also want the development/testing tools (`black`, `flake8`, etc.):

```bash
pip install -e .[dev]
```

---

## Running Locally

We rely on a small `run.py` that uses the `create_app` factory from `src/l3s_offshore_2/__init__.py`.  
Make sure `FLASK_APP=run.py` and `FLASK_DEBUG=true` are set in your environment (or `.env` file). Then:

```bash
flask run --host=0.0.0.0 --port=9040
```

Navigate to:  
- **Swagger UI**: [http://localhost:9040/l3s-offshore-2/](http://localhost:9040/l3s-offshore-2/)
- **OpenAPI Spec (JSON)**: [http://localhost:9040/l3s-offshore-2/swagger.json](http://localhost:9040/l3s-offshore-2/swagger.json)

---

## API Overview

The API provides four namespaces:

| Namespace | Path | Description |
|-----------|------|-------------|
| **Offshore Plan** | `/offshore-plan/*` | Simulation and scheduling (production) |
| **Simulation** | `/simulation-petri-nets/*` | Generic Petri net simulation |
| **Process Mining** | `/process-mining/*` | Event log analysis utilities |
| **DTO** | `/dto/*` | Parameter defaults and examples |

### Main Endpoints

**Offshore Planning (Simulation):**
- `POST /offshore-plan/calc-opt-install-cycle-single-vessel` – Run single installation cycle simulation
- `POST /offshore-plan/calc-opt-schedule-single-vessel-to-horizon` – Run simulation to planning horizon
- `POST /offshore-plan/display-single-vessel-schedule` – Generate schedule PDF
- `GET /offshore-plan/get-tpn-cyclic-model` – Get Petri net model definition

**Parameter Defaults:**
- `GET /dto/planning/defaults` – Get default parameters (for Frontend display)
- `GET /dto/example/scenario` – Get example scenario configuration

All endpoints are documented via **Swagger UI** at runtime.  

---

## API Architecture

> ⚠️ **Important**: This project contains two API services with **incompatible parameter formats**.

### The Two-Service Problem

| Service | Path | Format | Purpose |
|---------|------|--------|---------|
| `dto_srv` | `/dto/*` | Nested, modern | Frontend defaults display |
| `offshore_plan_srv` | `/offshore-plan/*` | Flat, MATLAB-style | Actual simulation |

### Quick Reference

| Use Case | Endpoint |
|----------|----------|
| Get parameter defaults (Frontend) | `GET /dto/planning/defaults` |
| Run actual simulation | `POST /offshore-plan/calc-opt-*` |
| Generate schedule PDF | `POST /offshore-plan/display-single-vessel-schedule` |

### Known Limitations

1. **Format Incompatibility**: `dto_srv` uses nested JSON, `offshore_plan_srv` uses flat JSON
2. **No simulation in dto_srv**: The `POST /dto/planning` endpoint returns mock data only
3. **No defaults in offshore_plan_srv**: No `/defaults` endpoint available

**For detailed documentation, see:** [`src/l3s_offshore_2/api/API_ARCHITECTURE.md`](src/l3s_offshore_2/api/API_ARCHITECTURE.md)

---

## Deployment with Docker

We’ve included a `Dockerfile` that sets up a Python 3.9 environment, installs dependencies, and launches the Flask app:
```bash
docker build -t l3s_offshore_2 .
docker run -p 9040:9040 l3s_offshore_2
```
After the container starts, you can hit `[host machine IP]:9040/l3s-offshore-2` to see your API.

---

## Testing

We use **pytest** for tests and **tox** for environment isolation. Make sure you have installed dev dependencies:
```bash
pip install -e .[dev]
tox
```
This runs lint checks (flake8) and any unit tests you create. See `pytest.ini` for configuration.


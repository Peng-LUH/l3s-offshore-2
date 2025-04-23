# L3S Offshore 2

A boilerplate Flask API that demonstrates:
- **Flask-RESTx** routing and auto-docs,
- **SQLAlchemy** (basic setup),
- **Workforce Management (WFM)**, **Scenario** and **Petri Net (PN)** parameter handling,
- A **Docker** environment for containerization,
- Jenkins pipeline for CI/CD,
- Tox/pytest for testing.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Setup & Installation](#setup--installation)
3. [Running Locally](#running-locally)
4. [API Overview](#api-overview)
5. [Workforce & Petri-Net Parameters](#workforce--petri-net-parameters)
6. [Deployment with Docker](#deployment-with-docker)
7. [Testing](#testing)

---

## Project Structure

```
.
├── Dockerfile
├── Jenkinsfile
├── pyproject.toml
├── pytest.ini
├── README.md
├── run.py
├── setup.py
├── src
│   └── l3s_offshore_2
│       ├── __init__.py
│       ├── api
│       │   ├── __init__.py
│       │   ├── model_x_srv
│       │   │   ├── __init__.py
│       │   │   ├── dto.py
│       │   │   ├── endpoints.py
│       │   │   └── logic.py
│       │   ├── random
│       │   │   ├── __init__.py
│       │   │   ├── dto.py
│       │   │   ├── endpoints.py
│       │   │   └── logic.py
│       │   └── test
│       │       ├── __init__.py
│       │       ├── dto.py
│       │       └── endpoints.py
│       ├── config.py
│       └── util
│           ├── datetime_util.py
│           └── result.py
└── tox.ini
```

---

## Setup & Installation

```bash
# 1) Clone the repo
git clone https://github.com/Peng-LUH/l3s-offshore-2
cd l3s_offshore_2

# 2) Create & Activate Virtual Environment (optional, recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

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
[http://localhost:9040/l3s-offshore-2/](http://localhost:9040/l3s-offshore-2/)  
You’ll see the root redirect (if `HOST_IP` is set). Or access the **Swagger UI** at:  
[http://localhost:9040/l3s-offshore-2/swagger.json](http://localhost:9040/l3s-offshore-2/swagger.json) or wherever the docs are generated.

---

## API Overview

We have three primary namespaces right now:

1. **`test`** – Example endpoints demonstrating GET/POST with a simple `test_model`.
2. **`random`** – Provides a `get-random-recommendation` POST endpoint that reads a JSON from local disk and returns random items.
3. **`model_x`** – The main area for the planning scenario:
   - **GET** `/model-x/planning` – retrieve the current in-memory plan
   - **POST** `/model-x/planning` – create a new plan from WFM + PN parameters
   - **PUT** `/model-x/planning` – update or merge changes into the existing plan

All endpoints are documented via **Swagger** courtesy of **Flask-RESTx**.  

---

## Workforce & Petri-Net Parameters

The core parameters for scenario, workforce management and the Petri net simulation are defined in `dto.py` inside the `model_x_srv` folder.

For further documentation access the **Swagger UI** at:  
[http://localhost:9040/l3s-offshore-2/swagger.json](http://localhost:9040/l3s-offshore-2/swagger.json)

### The following part is outdated!

### Workforce Management

| Parameter                | Description                                                           |
|--------------------------|-----------------------------------------------------------------------|
| `performWFM`            | Boolean to toggle workforce management on/off                         |
| `epsilon`               | Penalization factor for changing assigned crew or persons often       |
| `maxHoursPerDay`        | Array of max daily hours for each ruleset ID                          |
| `maxHoursPerWeek`       | Array of max weekly hours for each ruleset ID                         |
| `minPauseBlock`         | Array of minimum rest (in hours) between shifts                       |
| `minSmallPause`         | Array of short break durations (in hours)                             |
| `minSmallPausePerHours` | After how many hours a short break is needed                          |
| `skills`                | List of skill names (e.g. "Install", "Vessel", "Agency")              |
| `jobTypeSkills`         | Mapping from job type to required skill set                           |
| `personTypeSkills`      | Mapping from person type to possessed skill set                       |
| `persons`               | List of persons or roles                                              |
| `costPerson`            | Cost per person (parallel to `persons`)                               |
| `location`              | Vessel ID or 0=port for each person                                   |
| `ruleset`               | Which ruleset each person adheres to for hours/pauses                 |

### Petri Net (PN)

| Parameter           | Description                                                    |
|---------------------|----------------------------------------------------------------|
| `start_date`        | Date the simulation starts                                    |
| `end_date`          | Date the simulation ends                                      |
| `delta_time`        | Simulation-step increment                                     |
| `max_loop`          | Maximum loop iterations                                       |
| `print_loop_number` | Whether to log loop numbers for debugging                     |
| `owf_size`          | Size of the offshore wind farm (# of turbines)               |
| `ini_storage`       | Initial storage capacity in port                              |
| `storage_max`       | Maximum storage capacity                                      |
| `sotrage_min`       | Minimum storage threshold (typo kept for code-compatibility)  |
| `num_agent`         | Number of installation vessels used                           |
| `capacity_iv`       | Capacity of each vessel                                      |
| `operation_duration`| Time spent on each operation (e.g. load, move, jack up, etc.)|
| `lim_weather`       | Weather constraints (wind & wave) per operation step         |
| `fair_mode`         | Fairness approach for scheduling                             |
| `pruning_flag`      | How aggressively the search space is pruned                  |
| `tau`               | Tolerance parameter for pruning                              |
| `search_space`      | BFS/DFS limit or branching factor                            |
| `windDataFile`      | CSV path for wind data                                       |
| `waveDataFile`      | CSV path for wave data                                       |

Example JSON for a `POST` request to `/model-x/planning` might look like:
```json
{
  "wfm": {
    "performWFM": true,
    "epsilon": 10,
    "maxHoursPerDay": [14, 12, 10],
    "maxHoursPerWeek": [72, 48, 40],
    "...": "... more WFM fields ..."
  },
  "pn": {
    "start_date": "2025-03-17",
    "end_date": "2025-03-27",
    "delta_time": 1,
    "...": "... more PN fields ..."
  }
}
```

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


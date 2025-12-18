# API Architecture Documentation

## Overview

This document describes the current API architecture of L3S-Offshore-2, focusing on the
relationship between `dto_srv` and `offshore_plan_srv` services and their respective
parameter formats.

**Status**: This is a historical/transitional architecture. For L3S-Offshore-3,
consider unifying to a single parameter format and service.

---

## Table of Contents

1. [Service Overview](#service-overview)
2. [The Two-Format Problem](#the-two-format-problem)
3. [Parameter Format Comparison](#parameter-format-comparison)
4. [Endpoint Reference](#endpoint-reference)
5. [Current Usage Patterns](#current-usage-patterns)
6. [Known Limitations](#known-limitations)
7. [Recommendations for L3S-Offshore-3](#recommendations-for-l3s-offshore-3)

---

## Service Overview

### Registered API Namespaces

| Namespace | Path | Purpose | Status |
|-----------|------|---------|--------|
| `dto_srv` | `/dto/*` | Parameter defaults for Frontend | Active (limited) |
| `offshore_plan_srv` | `/offshore-plan/*` | Actual simulation execution | Active (production) |
| `simulation_srv` | `/simulation-petri-nets/*` | Generic Petri net simulation | Active |
| `process_mining_srv` | `/process-mining/*` | Process mining utilities | Active |

### Service Responsibilities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                        │
│                                                                              │
│   ┌──────────────────────┐              ┌────────────────────────────────┐  │
│   │  Parameter Display   │◄─────────────│  GET /dto/planning/defaults    │  │
│   │  Panel (UI)          │              │  (dto_srv - nested format)     │  │
│   └──────────────────────┘              └────────────────────────────────┘  │
│                                                                              │
│              │                                                               │
│              │  NOT CONNECTED (simulation not implemented in Frontend)       │
│              ▼                                                               │
│                                                                              │
│   ┌──────────────────────┐              ┌────────────────────────────────┐  │
│   │  Simulation Trigger  │─────────────?│  POST /offshore-plan/calc-*    │  │
│   │  (not implemented)   │              │  (offshore_plan_srv - flat)    │  │
│   └──────────────────────┘              └────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Two-Format Problem

Two independent parameter formats exist in this project:

### Format A: dto_srv (Nested, Modern)

- **Location**: `src/l3s_offshore_2/api/dto_srv/dto.py`
- **Style**: Hierarchically nested JSON with descriptive field names
- **Naming**: `snake_case`, grouped by domain concept
- **Purpose**: Originally designed as the "ideal" API structure based on paper analysis
- **Simulation**: NOT IMPLEMENTED (placeholder logic only)

### Format B: offshore_plan_srv (Flat, MATLAB-compatible)

- **Location**: `src/l3s_offshore_2/api/offshore_plan_srv/dto.py`
- **Style**: Flat JSON structure, all fields at root level
- **Naming**: `camelCase` / MATLAB variable naming conventions
- **Purpose**: Direct compatibility with MATLAB codebase and gspn4py
- **Simulation**: FULLY IMPLEMENTED with gspn4py integration

### Why Two Formats Exist

1. `dto_srv` was designed as the "ideal" modern API based on requirements analysis
2. `offshore_plan_srv` was implemented with actual simulation logic for practical use
3. The two were never unified due to time constraints
4. Frontend currently only uses `dto_srv` for parameter display

---

## Parameter Format Comparison

### Core Parameters Mapping

| Concept | dto_srv (nested) | offshore_plan_srv (flat) |
|---------|------------------|--------------------------|
| OWTs to build | `scenario_definition.owf_target_size` | `scenario_OWTsToBuild` |
| Vessel capacity | `scenario_definition.vessel_config.capacity_owt` | `vessel_capacity` |
| Number of vessels | `scenario_definition.vessel_config.num_installation_vessels` | `vessel_numInstallationVessels` |
| Port storage | `scenario_definition.port_config.max_owt_components` | `basePort_storageCapacity` |
| Initial storage | `scenario_definition.port_config.initial_owt_components` | `state_basePort_currentStorage` |
| Simulation start | `simulation_config.simulation_start_datetime` | `scenario_simulationStartDate` |
| Time step | `simulation_config.time_step_hours` | `pn_deltaTime` |
| Wind limits | `operations[].weather_limits.max_wind_speed_m_s` | `operation_wind` |
| Wave limits | `operations[].weather_limits.max_wave_height_m` | `operation_wave` |

### Date/Time Format Difference

| Format | dto_srv | offshore_plan_srv |
|--------|---------|-------------------|
| Style | ISO 8601 | MATLAB datestr |
| Example | `"2024-01-01T00:00:00Z"` | `"15-Jun-2000-00"` |

### Structure Comparison

**dto_srv (nested):**
```json
{
  "scenario_definition": {
    "scenario_id": "DefaultScenario",
    "owf_target_size": 40,
    "port_config": {
      "initial_owt_components": 20,
      "max_owt_components": 50
    },
    "vessel_config": {
      "num_installation_vessels": 1,
      "capacity_owt": 4
    },
    "operations": [
      {
        "operation_id": "Load_Components",
        "base_duration_hours": 12.0,
        "weather_limits": {
          "max_wind_speed_m_s": 99.0,
          "max_wave_height_m": 99.0
        }
      }
    ]
  },
  "simulation_config": {
    "simulation_start_datetime": "2024-01-01T00:00:00Z",
    "time_step_hours": 1
  }
}
```

**offshore_plan_srv (flat):**
```json
{
  "scenario_OWTsToBuild": 50,
  "vessel_numInstallationVessels": 2,
  "vessel_capacity": [4, 4],
  "basePort_storageCapacity": 32,
  "state_basePort_currentStorage": 20,
  "scenario_simulationStartDate": "15-Jun-2000",
  "pn_deltaTime": 1,
  "operation_name": ["Install Tower", "Install Nacelle", "..."],
  "operation_duration": [3, 3, 2, 2, 2, 2, 4, 1, 2, 2, 12],
  "operation_wind": [12, 12, 10, 10, 10, 12, 21, 14, 14, 14, 99],
  "operation_wave": [99, 99, 99, 99, 99, 99, 2.5, 2, 1.8, 1.8, 99]
}
```

---

## Endpoint Reference

### dto_srv Endpoints (`/dto/*`)

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/dto/planning/defaults` | GET | ✅ ACTIVE | Returns default parameters (nested format) for Frontend |
| `/dto/planning` | POST | ⚠️ PLACEHOLDER | Returns mock data, not connected to simulation |
| `/dto/example/scenario` | GET | ✅ ACTIVE | Returns example scenario (flat format from file) |
| `/dto/example/descriptor` | GET | ✅ ACTIVE | Returns method descriptor for Valuetools2025 |
| `/dto/example/schedule` | GET | ✅ ACTIVE | Returns example schedule output |
| `/dto/example/operation-mapping` | GET | ✅ ACTIVE | Returns operation ID mapping |

### offshore_plan_srv Endpoints (`/offshore-plan/*`)

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/offshore-plan/get-tpn-cyclic-model` | GET | ✅ ACTIVE | Returns Petri net model definition |
| `/offshore-plan/calc-operation-duration` | POST | ✅ ACTIVE | Calculates expected operation duration |
| `/offshore-plan/calc-opt-install-cycle-single-vessel` | POST | ✅ ACTIVE | Runs single installation cycle simulation |
| `/offshore-plan/calc-opt-schedule-single-vessel-to-horizon` | POST | ✅ ACTIVE | Runs simulation to planning horizon |
| `/offshore-plan/display-single-vessel-schedule` | POST | ✅ ACTIVE | Generates PDF visualization |
| `/offshore-plan/defaults` | GET | ❌ MISSING | No defaults endpoint available |

---

## Current Usage Patterns

### Frontend (PNML Viewer)

```
1. Page Load
   └── GET /dto/planning/defaults
       └── Display parameters in UI panel (nested format)

2. User Interaction
   └── Edit parameters in UI (not persisted)
   
3. Simulation (NOT IMPLEMENTED)
   └── Would require: Format conversion + POST to offshore_plan_srv
```

### Demo Notebooks

```
demos/demo_request.ipynb:
   └── POST /offshore-plan/calc-opt-schedule-single-vessel-to-horizon
       └── Uses flat format directly (no dto_srv involvement)
```

### Valuetools2025 / Benchmarking

```
GET /dto/example/scenario     → Returns scenario.json (flat format)
GET /dto/example/descriptor   → Returns descriptor_dto.json
```

---

## Known Limitations

### 1. Format Incompatibility

The two formats cannot be used interchangeably. Any integration requires explicit conversion.

### 2. No Defaults in offshore_plan_srv

`offshore_plan_srv` does not expose a `/defaults` endpoint. Defaults are embedded in the
Flask-RESTx Model definitions but not accessible via API.

### 3. Placeholder Simulation in dto_srv

The `POST /dto/planning` endpoint returns mock data:
```python
# From dto_srv/logic.py
placeholder_results = {
    "schedule_gantt": [...],  # Static mock data
    "kpis": {...}             # Not calculated from actual simulation
}
```

### 4. Example Endpoints Return Mixed Formats

- `/dto/planning/defaults` returns **nested** format
- `/dto/example/scenario` returns **flat** format (loaded from file)

This inconsistency can cause confusion.

---

## Feature Comparison Matrix

| Feature | dto_srv | offshore_plan_srv |
|---------|---------|-------------------|
| Defaults endpoint | ✅ `/planning/defaults` | ❌ Not available |
| Actual simulation | ❌ Placeholder only | ✅ gspn4py integration |
| Example data | ✅ Multiple endpoints | ❌ None |
| PDF export | ❌ | ✅ `/display-single-vessel-schedule` |
| Swagger documentation | ✅ Detailed | ✅ Basic |
| MATLAB compatibility | ❌ | ✅ Direct |
| Frontend integration | ✅ Defaults display | ❌ Not connected |
| Tests | ❌ None | ❌ None |

---

## Recommendations for L3S-Offshore-3

### Option 1: Unify on Flat Format (Recommended)

Adopt the `offshore_plan_srv` flat format as the single standard:

**Advantages:**
- Direct MATLAB compatibility
- Already integrated with gspn4py
- Simpler data structure
- No conversion needed

**Required Changes:**
- Add `/defaults` endpoint to offshore_plan_srv
- Update Frontend to use flat format
- Deprecate dto_srv

### Option 2: Unify on Nested Format

Adopt the `dto_srv` nested format and implement simulation:

**Advantages:**
- More modern, self-documenting structure
- Better for complex scenarios
- Easier to extend

**Required Changes:**
- Implement simulation logic in dto_srv
- Add format conversion layer for gspn4py
- Higher maintenance burden

### Option 3: Keep Both with Conversion Layer

Maintain both formats with automatic conversion:

**Advantages:**
- Backward compatibility
- Flexibility for different use cases

**Disadvantages:**
- Higher complexity
- More code to maintain
- Potential for conversion bugs

---

## Quick Reference: Which Service to Use?

| Use Case | Service | Endpoint |
|----------|---------|----------|
| Get parameter defaults (Frontend) | dto_srv | `GET /dto/planning/defaults` |
| Run actual simulation | offshore_plan_srv | `POST /offshore-plan/calc-*` |
| Get example scenario data | dto_srv | `GET /dto/example/scenario` |
| Generate schedule PDF | offshore_plan_srv | `POST /offshore-plan/display-single-vessel-schedule` |
| Get Petri net model | offshore_plan_srv | `GET /offshore-plan/get-tpn-cyclic-model` |

---

## File Locations

```
src/l3s_offshore_2/api/
├── __init__.py                    # API registration (both services)
├── API_ARCHITECTURE.md            # This document
├── dto_srv/
│   ├── __init__.py                # Architectural notice
│   ├── dto.py                     # Nested DTO definitions
│   ├── endpoints.py               # /dto/* endpoints
│   └── logic.py                   # Placeholder logic
└── offshore_plan_srv/
    ├── __init__.py
    ├── dto.py                     # Flat DTO definitions
    ├── endpoints.py               # /offshore-plan/* endpoints
    └── logic.py                   # Actual simulation logic (gspn4py)
```

---

## Changelog

- **2025-12-18**: Initial documentation created (architectural freeze for L3S-Offshore-2)

---

*Document Author: Martin Krause*  
*Last Updated: 2025-12-18*

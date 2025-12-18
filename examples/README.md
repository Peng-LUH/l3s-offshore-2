# Example Data Files

This directory contains static example data files used by the API for documentation,
testing, and demonstration purposes.

## Files

### scenario.json

**Served by**: `GET /dto/example/scenario`

A complete simulation scenario configuration in **FLAT format** (MATLAB-style).
This is the same format expected by `offshore_plan_srv` simulation endpoints.

**Contents**:
- Optimization parameters (`optim_*`): GUROBI settings, time limits
- Petri net parameters (`pn_*`): Time step, pruning, search config
- Scenario definition (`scenario_*`): Start date, target OWTs
- Operations (`operation_*`): Names, durations, weather limits
- Vessel configuration (`vessel_*`): Number, capacity
- Port configuration (`basePort_*`): Storage, coordinates
- Transport configuration (`transport_*`): Cycle times, routes
- Cost parameters (`cost_*`): Offshore, fuel, penalties
- Initial state (`state_*`): Current positions, storage levels
- Workforce management (`performWFM`, `wfm`): Optional WFM config

**Usage**: Use as template for `POST /offshore-plan/calc-opt-*` requests.

---

### payload.json

Similar to `scenario.json` but with different parameter values.
Can be used for testing alternative scenarios.

**Key differences from scenario.json**:
- `optim_maxOptimTime`: 900 (vs 43200)
- `scenario_simulationStartDate`: ISO format "2000-04-01T00:00:00"

---

### descriptor_dto.json

**Served by**: `GET /dto/example/descriptor`

A metadata schema template for describing simulation methods.
All fields are empty/false - fill in to describe your specific method.

**Structure**:
- `modelID`: Unique identifier for the method
- `typology`: Application context, model formalism, structure, features
- `performance`: Solution quality metrics, robustness information
- `complexity`: Hyperparameters, flexibility options
- `viability`: Correctness verification, traceability

**Usage**: Method registration, benchmarking frameworks, documentation.

---

## Format Notes

### FLAT vs NESTED Format

These files use the **FLAT format** (all parameters at root level).
This is different from `dto_srv`'s `/planning/defaults` endpoint which
returns **NESTED format** (hierarchical structure).

The two formats are **NOT compatible** without conversion.

| Concept | FLAT (these files) | NESTED (dto_srv) |
|---------|-------------------|------------------|
| OWTs to build | `scenario_OWTsToBuild` | `scenario_definition.owf_target_size` |
| Vessel capacity | `vessel_capacity` | `scenario_definition.vessel_config.capacity_owt` |

### Production Endpoints

For actual simulations, use `offshore_plan_srv` endpoints with FLAT format:
- `POST /offshore-plan/calc-opt-install-cycle-single-vessel`
- `POST /offshore-plan/calc-opt-schedule-single-vessel-to-horizon`

See `src/l3s_offshore_2/api/API_ARCHITECTURE.md` for full documentation.

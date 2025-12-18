# =============================================================================
#DTO_SRV - ARCHITECTURAL NOTICE
# =============================================================================
#
# STATUS: ACTIVE BUT LIMITED (Frontend Defaults Only)
#
# This service provides parameter defaults for the Frontend UI but does NOT
# execute actual simulations. The simulation logic exists in `offshore_plan_srv`.
#
# IMPORTANT: Two incompatible parameter formats exist in this project:
#   - dto_srv:          Nested, modern format (this service)
#   - offshore_plan_srv: Flat, MATLAB-compatible format (actual simulation)
#
# For detailed documentation, see:
#   - src/l3s_offshore_2/api/API_ARCHITECTURE.md
#   - README.md section "API Architecture"
#
# For L3S-Offshore-3: Consider unifying to a single parameter format.
# =============================================================================

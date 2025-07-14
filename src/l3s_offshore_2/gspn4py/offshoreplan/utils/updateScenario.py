import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from wfm.updateScenarioWFM import update_scenario_wfm 

def update_scenario(scenario):
     # Updates dependent values of a scenario in case the base values were
    # modified. Careful, replaces dependent values with calculated ones.
    # Make sure to change these after possible updates.

    scenario.N = scenario.P * scenario.T
    scenario.vesselStart[:] = scenario.startDate
    scenario.currentDate = scenario.startDate
    scenario.currentLocation = np.zeros(scenario.numInstallationVessels)
    scenario.currentCapacity = np.zeros(scenario.numInstallationVessels)
    scenario.vesselStart = np.array([datetime.fromtimestamp(scenario.startDate.timestamp())] * scenario.numInstallationVessels)
    scenario.costOffshore = np.ones(scenario.numInstallationVessels) * 1800  # Costs for not being in port
    scenario.costFuel = np.ones(scenario.numInstallationVessels) * 600  # Costs for each hour driving the ship
    scenario.maxShipCapacities = np.ones(scenario.numInstallationVessels) * 4

    scenario = update_scenario_wfm(scenario)
    
    return scenario
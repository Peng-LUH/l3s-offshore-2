import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from wfm.updateScenarioWFM import update_scenario_wfm 
from utils.updateScenario import update_scenario

class WorkforceManagement:
    pass  # Implement WorkforceManagement class if needed

class Scenario:
    pass  # Implement Scenario class if needed

def make_default_scenario():
    scenario = Scenario()

    # OPTIMIZER AND ALGORITHM SETTINGS
    scenario.maxOptimTime = 5 * 60

    # Old Solutions
    scenario.useHistoricSolutions = 1
    scenario.useInitialPoint = 1
    scenario.useHistoricTillIteration = 9999

    # Forecasts
    scenario.useForecasts = 1
    scenario.applyWithRealWeatherData = 1

    # Planning Data
    scenario.T = 168
    scenario.P = 2
    scenario.N = scenario.P * scenario.T
    scenario.mpcIterations = 9999

    # SCENARIO DATA
    scenario.startDate = datetime(2000, 6, 1)
    
    # Limits
    scenario.targetPlanTime = 999999
    scenario.OWTsToBuild = 50

    # Process data
    scenario.opName = ["Install Tower", "Install Nacelle", "Install Blade 1", "Install Blade 2", "Install Blade 3",
                       "Install Hub", "Move", "Reposition in Field", "Jack-up", "Jack-Down", "Load OWT Components", "Install OWT"]
    scenario.opData = np.array([
        [3, 3, 2, 2, 2, 2, 4, 1, 2, 2, 12, 14],
        [12.0, 12.0, 10.0, 10.0, 10.0, 12.0, 21.0, 14.0, 14.0, 14.0, 99.0, 10.0],
        [99.0, 99.0, 99.0, 99.0, 99.0, 99.0, 2.5, 2.0, 1.8, 1.8, 99.0, 99.0]
    ])
    scenario.processChain_Install = [7, 8, 0, 1, 2, 3, 4, 5, 9]
    scenario.processChain_Move = [6]
    scenario.processChain_Load = [10]

    # Port Data
    scenario.numLoadingBaysInPort = 1
    scenario.maximumPortCapacity = 32
    scenario.portRestockAmount = 8
    scenario.portRestockFrequency = 312

    # Vessel Data
    scenario.numInstallationVessels = 1
    scenario.maxShipCapacities = [4, 4, 4]

    # Cost Function Settings
    scenario.costOffshore = np.array([1800.0, 1800.0, 1800.0])
    scenario.costPortOp = 1200.0
    scenario.costFuel = np.array([600.0, 600.0, 600.0])

    scenario.benefitForFinishingAnOWT = np.mean(75.0 * scenario.costOffshore)
    scenario.maxBenefitForFinishingEarly = scenario.benefitForFinishingAnOWT * 0.06
    scenario.storagePenalty = -10.0

    # SCENARIO: TRANSPORT
    scenario.locationBasePort = [53.454399, 6.838584]
    scenario.locationTower = [53.865448, 8.72604]
    scenario.locationBlades = [53.543192, 8.567501]
    scenario.locationNacelle = [53.543192, 8.567501]
    scenario.transport_vesselSpeed = 9.5
    scenario.transport_maxSpace = 2646.0
    scenario.transport_maxWeight = 8900.0
    scenario.transport_componentSpace = np.array([650, 300, 263])
    scenario.transport_componentWeight = np.array([600, 120, 500])
    scenario.transport_componentSetUpTime = np.array([0, 0, 0])
    scenario.transport_componentLoadingTime = np.array([2., 8., 10.])
    scenario.transport_componentUnloadTime = np.array([1.2, 4.8, 6.0])

    # CURRENT STATE

    # Project
    scenario.BuiltOWTs = 0
    scenario.currentDate = datetime(2000, 6, 1)

    # Vessels
    scenario.currentLocation = np.array([0, 0, 0])
    scenario.currentCapacity = np.array([0, 0, 0])
    scenario.vesselStart = np.array([datetime(2000, 6, 1), datetime(2000, 6, 1), datetime(2000, 6, 1)])

    # Port
    scenario.portRestockEarliest = 312
    scenario.currentPortCapacity = 20
    scenario.currentPlans_ops = np.array([])
    scenario.currentPlans_start = np.array([])
    scenario.currentPlans_end = np.array([])

    # WORKFORCE MANAGEMENT
    scenario.performWFM = 0

    # Parameters and rules
    scenario.wfm = WorkforceManagement()
    scenario.wfm.epsilon = 10  # Weight factor to suppress changing of persons
    #Indexes 0: VesselCrew, 1: ProjectCrew, 2: LandCrew
    scenario.wfm.maxHoursPerDay =        np.array([14, 12, 10])  # Max hours per day
    scenario.wfm.maxHoursPerWeek =       np.array([72, 48, 40])  # Max hours per week
    scenario.wfm.minPauseBlock =         np.array([6 , 11, 11])  # Min rest between shifts
    scenario.wfm.minSmallPause =         np.array([1 , 1 , 1])  # Small pause ...
    scenario.wfm.minSmallPausePerHours = np.array([10, 10, 8])  # every n hours

    # Skills
    scenario.wfm.Skills = np.array(["Install", "Vessel", "Port"])  # Existing skill types
    scenario.wfm.JobTypeSkills = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # Mapping of skill types to amounts - JOBS
    scenario.wfm.PersonTypeSkills = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # Mapping of skill types to an array - PERSONS

    # Persons
    # V1
    scenario.wfm.Persons = np.array(["Install", "Install", "Install", "Vessel", "Vessel", "Port", "Port", "Port", "Port"])
    scenario.wfm.costPerson = np.ones(len(scenario.wfm.Persons)) * 100 + np.arange(1, len(scenario.wfm.Persons) + 1)
    scenario.wfm.atVessel = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0])
    scenario.wfm.ruleset = np.array([1, 1, 1, 0, 0, 2, 2, 2, 2])

    # V2
    #scenario.wfm.Persons = np.array(["Install", "Install", "Install", "Vessel", "Vessel", "Install", "Install", "Install",
    #                         "Vessel", "Vessel", "Port", "Port", "Port", "Port"])
    #scenario.wfm.costPerson = np.ones(len(scenario.wfm.Persons)) * 100 + 10 * np.arange(1, len(scenario.wfm.Persons) + 1)
    #scenario.wfm.atVessel = np.array([1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 0, 0, 0, 0])
    #scenario.wfm.ruleset = np.array([1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 2, 2, 2, 2])

    # V1 Low Personnel
    #scenario.wfm.Persons = np.array(["Install", "Install", "Vessel", "Vessel", "Port", "Port", "Port", "Port"])
    #scenario.wfm.costPerson = np.ones(len(scenario.wfm.Persons)) * 100 + np.arange(1, len(scenario.wfm.Persons) + 1)
    #scenario.wfm.atVessel = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    #scenario.wfm.ruleset = np.array([1, 1, 0, 0, 2, 2, 2, 2])

    # V2 Low Personnel
    #scenario.wfm.Persons = np.array(["Install", "Install", "Vessel", "Vessel", "Install", "Install", "Vessel", "Vessel",
    #                         "Port", "Port", "Port", "Port"])
    #scenario.wfm.costPerson = np.ones(len(scenario.wfm.Persons)) * 100 + 10 * np.arange(1, len(scenario.wfm.Persons) + 1)
    #scenario.wfm.atVessel = np.array([1, 1, 1, 1, 2, 2, 2, 2, 0, 0, 0, 0])
    #scenario.wfm.ruleset = np.array([1, 1, 0, 0, 1, 1, 0, 0, 2, 2, 2, 2])

    # JOBS
    scenario.wfm.Jobs = []
    scenario.wfm.jobStart = np.array([])
    scenario.wfm.jobDuration = np.array([])
    scenario.wfm.jobEnd = np.array([])
    scenario.wfm.jobLocation = np.array([0])

    # APPEND FALLBACK SKILL
    scenario.wfm.maxHoursPerDay = np.append(scenario.wfm.maxHoursPerDay, 24)
    scenario.wfm.maxHoursPerWeek = np.append(scenario.wfm.maxHoursPerWeek, 168)
    scenario.wfm.minPauseBlock = np.append(scenario.wfm.minPauseBlock, 1)
    scenario.wfm.minSmallPause = np.append(scenario.wfm.minSmallPause, 1)
    scenario.wfm.minSmallPausePerHours = np.append(scenario.wfm.minSmallPausePerHours, 24)
    scenario.wfm.Skills = np.append(scenario.wfm.Skills, "Agency")

    scenario.wfm.JobTypeSkills = np.vstack([scenario.wfm.JobTypeSkills, np.zeros_like(scenario.wfm.JobTypeSkills[0, :])])
    scenario.wfm.PersonTypeSkills = np.vstack([scenario.wfm.PersonTypeSkills, np.zeros_like(scenario.wfm.PersonTypeSkills[0, :])])
    scenario.wfm.JobTypeSkills = np.hstack([scenario.wfm.JobTypeSkills, np.zeros((len(scenario.wfm.JobTypeSkills[:, 0]), 1))])
    scenario.wfm.PersonTypeSkills = np.hstack([scenario.wfm.PersonTypeSkills, np.ones((len(scenario.wfm.PersonTypeSkills[:, 0]), 1))])

    for l in np.unique(scenario.wfm.atVessel):
        scenario.wfm.Persons = np.append(scenario.wfm.Persons, "Agency")
        scenario.wfm.costPerson = np.append(scenario.wfm.costPerson, 999999)
        scenario.wfm.atVessel = np.append(scenario.wfm.atVessel, l)
        scenario.wfm.ruleset = np.append(scenario.wfm.ruleset, len(scenario.wfm.maxHoursPerDay)-1)

    scenario.wfm.usedCrew = np.zeros(len(scenario.wfm.Persons))

    # CURRENT State
    scenario.wfm.weekStart = 1
    scenario.wfm.dayStart = 1
    scenario.wfm.needsPauseStartBeforeFirstDay = np.zeros(len(scenario.wfm.Persons))
    scenario.wfm.needsPauseEndBeforeFirstDay = np.zeros(len(scenario.wfm.Persons))
    scenario.wfm.hoursWorkedToday = np.zeros(len(scenario.wfm.Persons))
    scenario.wfm.hoursWorkedThisWeek = np.zeros(len(scenario.wfm.Persons))
    scenario.wfm.pauseAtEndOfLastIteration = np.zeros(len(scenario.wfm.Persons))
    scenario.wfm.planned = np.zeros((len(scenario.wfm.Persons), scenario.P * scenario.T))

    # Update Scenario and go on
    scenario = update_scenario_wfm(scenario)
    scenario = update_scenario(scenario)

    return scenario

# Example usage
if __name__ == "__main__":
    default_scenario = make_default_scenario()
    print(default_scenario)

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ..offshore_utils.application_settings import SETTINGS

def update_scenario_wfm(scenario):
    
    # Workforce Management
    if hasattr(scenario, 'wfm'):
        scenario.wfm.horizon = max(scenario.wfm.jobEnd) if scenario.wfm.jobEnd else 0
        scenario.wfm.nSkills = len(scenario.wfm.Skills)
        scenario.wfm.nPersons = len(scenario.wfm.Persons)
        scenario.wfm.nJobs = len(scenario.wfm.jobStart)
        scenario.wfm.atLocation = scenario.wfm.jobLocation == scenario.wfm.atVessel
        
        scenario.wfm.personHasSkill = np.zeros((scenario.wfm.nPersons, len(scenario.wfm.Skills)))
        for i in range(scenario.wfm.nPersons):
            scenario.wfm.personHasSkill[i,:] = np.sum(scenario.wfm.PersonTypeSkills[:, np.array(scenario.wfm.Skills) == scenario.wfm.Persons[i]], axis=1)
        
        scenario.wfm.jobReqSkills = np.zeros((scenario.wfm.nJobs, len(scenario.wfm.Skills)))
        for i in range(scenario.wfm.nJobs):
            scenario.wfm.jobReqSkills[i, :] = np.sum(scenario.wfm.JobTypeSkills[:, scenario.wfm.Skills == scenario.wfm.Jobs[i]], axis=1)
        
        if scenario.performWFM == 1:
            SETTINGS['USE_SLIDINGWINDOW'] = 1 #USE_SLIDINGWINDOW = 1
        
        if len(scenario.wfm.planned[0, :]) < scenario.wfm.horizon:
            scenario.wfm.planned = np.column_stack([scenario.wfm.planned, np.zeros((len(scenario.wfm.planned), scenario.wfm.horizon - len(scenario.wfm.planned[0, :])))])

        scenario.wfm.dayStart = (24 - int(scenario.currentDate.hour)) % 24 + 1
        scenario.wfm.weekStart = (7 - (scenario.currentDate.weekday() + 1) % 7) * 24 % 168 + scenario.wfm.dayStart
        if scenario.currentDate.hour == 0:
            scenario.wfm.weekStart += 24

    return scenario
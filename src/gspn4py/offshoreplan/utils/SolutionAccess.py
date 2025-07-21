import numpy as np
import os
from utils.application_settings import SETTINGS
from utils.printMsg import printMsg

def try_save_stored_solution(scenario_org, solution, durations):
    global solutions_keyset, solutions_values, solutions_durations

    solutions_keyset = SETTINGS['solutions_keyset']
    solutions_values = SETTINGS['solutions_values']
    solutions_durations = SETTINGS['solutions_durations']

    saveResult = 0
    saveDuration = 0
    saveBackup = 0

    printMsg("> Trying to save solution")
    scenario = createSaveStruct(scenario_org)

    if os.path.isfile('solutions/solutions_keyset.npy'):
        if not solutions_keyset:
            solutions_keyset = np.load('solutions/solutions_keyset.npy', allow_pickle=True)
        if not solutions_values:
            solutions_values = np.load('solutions/solutions_values.npy', allow_pickle=True)
        if not solutions_durations:
            if os.path.isfile('solutions/solutions_durations.npy'):
                solutions_durations = np.load('solutions/solutions_durations.npy', allow_pickle=True)
            else:
                solutions_durations = {'expectedDuration': np.array([]),
                                       'realDuration': np.array([]),
                                       'wind': np.array([]),
                                       'wave': np.array([])}

        idx = len(solutions_keyset) + 1
        idx_d = idx

        # Search for similar entry
        for i, keyset in enumerate(solutions_keyset):
            if np.array_equal(createSaveStruct(keyset), scenario):
                sol = solutions_values[i]
                idx_d = i

                if (
                    (sol['cost'] > solution['cost']) or  # Solution is better OR
                    (
                        (solution['optim_exitflag'] == 1 or solution['optim_exitflag'] == 5) and  # New solution is optimal AND
                        (sol['optim_exitflag'] != 1 and sol['optim_exitflag'] != 5)  # Stored one isn't
                    )
                ):
                    printMsg(">> Found weaker solution in storage: Replace")
                    idx = i
                else:
                    printMsg(">> Found better or equal solution in storage: Keep")
                    idx = -1
                break

        if idx > 0:
            saveResult = 1
            if not solutions_keyset:
                solutions_keyset = np.array([scenario])
                solutions_values = np.array([solution])
                solutions_durations = np.array([durations])
            else:
                solutions_keyset[idx - 1] = scenario
                solutions_values[idx - 1] = solution
                solutions_durations[idx - 1] = durations
            printMsg(">> Saved solution")
        else:
            # Save durations to "reproduce" for old results
            if len(solutions_durations) < idx_d or not np.array_equal(solutions_durations[idx_d - 1], durations):
                solutions_durations[idx_d - 1] = durations
                saveDuration = 1
    else:
        printMsg(">> No saved solutions found: creating save struct")
        solutions_keyset = np.array([scenario])
        solutions_values = np.array([solution])
        solutions_durations = np.array([durations])
        saveResult = 1
        saveDuration = 1

    if saveResult:
        np.save('solutions/solutions_keyset.npy', solutions_keyset)
        np.save('solutions/solutions_values.npy', solutions_values)
        saveDuration = 1
        saveBackup = 1

    if saveDuration:
        np.save('solutions/solutions_durations.npy', solutions_durations)
        saveBackup = 1

    if saveBackup:
        np.savez('solutions/solutions_backup.npz', solutions_keyset=solutions_keyset,
                 solutions_values=solutions_values, solutions_durations=solutions_durations)

    printMsg("> Saved solution files")

def try_get_stored_solution(scenario_org):
    solutions_keyset = SETTINGS['solutions_keyset']
    solutions_values = SETTINGS['solutions_values']
    solutions_durations = SETTINGS['solutions_durations']
    loadedSolutions = SETTINGS['loadedSolutions']

    sol = None
    durs = {'expectedDuration': np.array([]),
            'realDuration': np.array([]),
            'wind': np.array([]),
            'wave': np.array([])}

    if os.path.isfile('solutions/solutions_keyset.npy'):
        if not solutions_keyset:
            solutions_keyset = np.load('solutions/solutions_keyset.npy', allow_pickle=True)
        if not solutions_values:
            solutions_values = np.load('solutions/solutions_values.npy', allow_pickle=True)
        if not solutions_durations:
            if os.path.isfile('solutions/solutions_durations.npy'):
                solutions_durations = np.load('solutions/solutions_durations.npy', allow_pickle=True)
            else:
                solutions_durations = {'expectedDuration': np.array([]),
                                       'realDuration': np.array([]),
                                       'wind': np.array([]),
                                       'wave': np.array([])}

        scenario = createSaveStruct(scenario_org)

        for i, keyset in enumerate(solutions_keyset):
            if np.array_equal(createSaveStruct(keyset), scenario):
                printMsg(">>> Retrieving saved solution")
                sol = solutions_values[i]
                loadedSolutions = np.append(loadedSolutions, i)
                if i < len(solutions_durations):
                    durs = solutions_durations[i]
                break
    else:
        printMsg(">>> No historic solutions found")

    return sol, durs

def createSaveStruct(scenario):
    # Removes values from the scenario that are not important to the problem/solution
    overridden_keys = {
        'maxOptimTime', 'targetPlanTime', 'OWTsToBuild', 'BuiltOWTs', 'startDate',
        'useInitialPoint', 'useHistoricSolutions', 'applyWithRealWeatherData',
        'useCPLEX', 'pathCPLEX', 'pathGUROBI', 'pathCPLEXexamples',
        'searchModeCPLEX', 'threadsCPLEX', 'mpcIterations',
        'useHistoricTillIteration', 'performWFM', 'wfm'
    }

    scen = {key: getattr(scenario, key) for key in dir(scenario) if key not in overridden_keys}

    # Add the keys explicitly overridden in createSaveStruct
    scen.update({
        'maxOptimTime': 1,
        'targetPlanTime': 1,
        'OWTsToBuild': 1,
        'BuiltOWTs': 1,
        'startDate': 1,
        'useInitialPoint': 0,
        'useHistoricSolutions': 1,
        'applyWithRealWeatherData': 1,
        'useCPLEX': 0,
        'pathCPLEX': '',
        'pathGUROBI': '',
        'pathCPLEXexamples': '',
        'searchModeCPLEX': 0,
        'threadsCPLEX': 0,
        'mpcIterations': 0,
        'useHistoricTillIteration': 0,
        'performWFM': 1,
        'wfm': []
    })

    return scen

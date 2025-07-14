import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from mainFunctions.computeClosedLoop import compute_closed_loop

def fmain(scenario, allResults=None, saveImages=None):
    if saveImages is None:
        saveImages = {
            'imgsize': [16, 16],
            'figureFormat': '-dpng',
            'doSave': 0,
            'prefix': "",
            'postfix': "",
            'includeLegend': 0
        }

    t_start = datetime.now()
    useBudgetingWithOverallDuration = 0
    stopTime = datetime.now() + timedelta(seconds=scenario.targetPlanTime)

    results, aborted = compute_closed_loop(scenario, useBudgetingWithOverallDuration, stopTime)

    # Plot solution
    plot_Result(results, scenario.numInstallationVessels, 1, saveImages)
    
    printMsg(f' !! OWTs finished in {scenario.targetPlanTime / (7*24)} weeks: {np.sum(results.applied_all.optimOperation[results.applied_all.end < scenario.targetPlanTime] == 1)}')
    printMsg(f' !! Plans needed {len(results.tracePlan)}')
    printMsg(f' !! Started: {t_start}; Ended: {datetime.now()}; Total: {datetime.now()-t_start} hours')
    printMsg(f' !! ************************************************')

    # Create Trace
    nr = createTrace(scenario, results)

    if scenario.performWFM == 1:
        traceWFM = plotWFMall(results, saveImages)
        nr.update(traceWFM)

    if allResults is None or allResults.empty:
        allResults = pd.DataFrame(nr, index=[0])
    else:
        # Check if DataFrame already contains a row with these keys
        idx = getTrace(nr['month'], nr['nOWT'], nr['vessels'], nr['bays'], nr['capacity'],
                       nr['initialInventory'], nr['T'], nr['P'], nr['benefitEarly'], nr['benefitOWT'],
                       nr['benefitInventory'], nr['maxOptimTime'], allResults)
        if np.sum(idx) > 0:
            allResults = allResults.drop(index=idx)
        allResults = pd.concat([allResults, pd.DataFrame(nr, index=[0])], ignore_index=True)

    return results, allResults, aborted

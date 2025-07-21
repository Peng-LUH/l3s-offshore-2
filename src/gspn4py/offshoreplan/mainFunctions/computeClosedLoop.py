import numpy as np
from datetime import datetime, timedelta
from utils.printMsg import printMsg
from utils.hours import hours
from mainFunctions.computeOpenLoopSolution import compute_open_loop_solution

def compute_closed_loop(scenario, useBudgetingWithOverallDuration, stopTime):
    global PAUSE

    if 'PAUSE' not in globals():
        PAUSE = 0

    traceStateX0 = np.empty(scenario.mpcIterations, dtype=object)
    tracePlan = np.empty(scenario.mpcIterations, dtype=object)
    traceData = np.empty(scenario.mpcIterations, dtype=object)
    traceApplied = np.empty(scenario.mpcIterations, dtype=object)
    traceStateX1 = np.empty(scenario.mpcIterations, dtype=object)
    traceWFM = np.empty(scenario.mpcIterations, dtype=object)
    traceStateWFMx0 = np.empty(scenario.mpcIterations, dtype=object)

    for i in range(1, scenario.mpcIterations + 1):
        aborted = False
        printMsg("---------------------------------")
        printMsg(f"--- Closed Loop Iteration {i:3d} ---")
        printMsg("---------------------------------")

        if useBudgetingWithOverallDuration == 1:
            scenario.maxOptimTime = round(getOptimBudget(scenario.mpcIterations, i, stopTime))

        printMsg(f">> Allocated solution time:  {scenario.maxOptimTime / 60:.5f} min ({scenario.maxOptimTime / 3600:.3f} hours)")

        solution, values = compute_open_loop_solution(scenario, i)
        traceStateX0[i - 1] = scenario
        tracePlan[i - 1] = solution
        traceData[i - 1] = values

        # Extract and Apply control from plan
        control = extractControl(scenario, solution)
        scenario, applied = applyControl(scenario, control, values, solution)

        # Do Workforce Management if requested
        if scenario.performWFM == 1:
            controlWFM = extractControlForWFM(traceStateX0[i - 1], solution)
            _, appliedForWFM = applyControl(traceStateX0[i - 1], controlWFM, values, solution, 0)
            scenarioWFM, _ = upgradePlanforWFM(traceStateX0[i - 1], appliedForWFM)
            resultWFM = optimizeWorkforce(scenarioWFM)
            scenarioWFM.wfm.nextIteration = hours(scenario.currentDate - scenarioWFM.currentDate)
            scenario, resultWFM.carryover = applyWFM(scenarioWFM, resultWFM, scenario, applied)
            traceStateWFMx0[i - 1] = scenarioWFM
            traceWFM[i - 1] = resultWFM

        traceApplied[i - 1] = applied
        traceStateX1[i - 1] = scenario

        # Check aborting plans
        if hours(traceStateX1[i - 1].currentDate - traceStateX0[0].currentDate) >= scenario.targetPlanTime:
            printMsg(f"> Aborting plan generation at timestamp {hours(traceStateX1[i - 1].currentDate - traceStateX0[0].currentDate):5d} (iteration {i:2d}). Target plan length of {scenario.targetPlanTime:5d} reached.")
            aborted = True
            break

        if scenario.BuiltOWTs >= scenario.OWTsToBuild:
            printMsg(f"> Aborting plan generation at timestamp {hours(traceStateX1[i - 1].currentDate - traceStateX0[0].currentDate):5d} (iteration {i:2d}). Target number of {scenario.OWTsToBuild:3d} OWTs reached.")
            aborted = True
            break

        if PAUSE == 1:  # PAUSE IF ACTIVATED
            d_now = datetime.now()
            d_break = datetime(d_now.year, d_now.month, d_now.day, 22, 0, 0)
            if d_now + timedelta(seconds=scenario.maxOptimTime) > d_break:
                input(' >>> Press key for next iteration <<< ')

    # ITERATIONS FINISHED, COMBINE SINGLE RESULTS TO OBJECT
    applied_all = traceApplied[0].copy()
    wfm_all = None
    if scenario.performWFM == 1:
        wfm_all = traceWFM[0].copy()
        wfm_all.jobNames = wfm_all.jobNames[:len(wfm_all.carryover.assignedByJob[0])]

    for i in range(1, len(traceStateX0)):
        t_offset = hours(traceStateX0[i].currentDate - traceStateX0[i].startDate)
        applied_all.optimOperation = np.concatenate([applied_all.optimOperation, traceApplied[i].optimOperation])
        applied_all.start = np.concatenate([applied_all.start, (traceApplied[i].start + t_offset)])
        applied_all.end = np.concatenate([applied_all.end, (traceApplied[i].end + t_offset)])
        applied_all.result = np.concatenate([applied_all.result, traceApplied[i].result])
        applied_all.portRestockAt = np.concatenate([applied_all.portRestockAt, (traceApplied[i].portRestockAt + t_offset)])
        applied_all.portStorage = np.concatenate([applied_all.portStorage, traceApplied[i].portStorage])

        if scenario.performWFM == 1:
            wfm_all.jobNames = np.concatenate([wfm_all.jobNames, traceWFM[i].jobNames[:len(traceWFM[i].carryover.assignedByJob[0])]])
            wfm_all.assigned = np.concatenate([wfm_all.assigned, np.round(traceWFM[i].carryover.assignedByJob)])
            wfm_all.start = np.concatenate([wfm_all.start, (traceStateWFMx0[i].wfm.jobStart[:len(traceWFM[i].carryover.assignedByJob[0])] + t_offset)])
            wfm_all.end = np.concatenate([wfm_all.end, (traceStateWFMx0[i].wfm.jobEnd[:len(traceWFM[i].carryover.assignedByJob[0])] + t_offset)])

    # Calculate location of vessel
    isOffshore = {}
    for v in range(1, scenario.numInstallationVessels + 1):
        m_out = applied_all.start[v - 1, applied_all.optimOperation[v - 1, :] == 3]
        m_in = applied_all.end[v - 1, applied_all.optimOperation[v - 1, :] == 2]

        lastEntry = len(applied_all.optimOperation[v - 1, :])
        for k in range(lastEntry, 0, -1):
            if applied_all.optimOperation[v - 1, k - 1] != 0:
                lastEntry = k
                break

        if len(m_out) == len(m_in) + 1:
            m_in = np.append(m_in, applied_all.end[v - 1, lastEntry - 1])

        if len(m_out) == len(m_in):
            if len(m_out) != 0:
                isOffshore[(v, 'start')] = m_out
                isOffshore[(v, 'duration')] = m_in - m_out
            else:
                isOffshore[(v, 'start')] = np.array([0])
                isOffshore[(v, 'duration')] = np.array([0])
        else:
            printMsg("WARNING: INCONSISTENCIES IN DRIVING OUT AND BACK IN")
            isOffshore[(v, 'start')] = np.array([0])
            isOffshore[(v, 'duration')] = np.array([0])

    # Results struct and save
    results = {
        'traceApplied': traceApplied,
        'traceData': traceData,
        'tracePlan': tracePlan,
        'traceStateX0': traceStateX0,
        'traceStateX1': traceStateX1,
        'applied_all': applied_all,
        'isOffshore': isOffshore
    }

    if scenario.performWFM == 1:
        results['traceStateWFMx0'] = traceStateWFMx0
        results['traceWFM'] = traceWFM
        results['wfm_all'] = wfm_all

    return results

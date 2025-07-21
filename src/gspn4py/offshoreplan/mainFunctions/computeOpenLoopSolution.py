import numpy as np
from utils.printMsg import printMsg

from utils.application_settings import SETTINGS

from utils.SolutionAccess import try_get_stored_solution
from utils.WeatherAccess import get_weather_data
from utils.WeatherAccess import get_forecast
from utils.WeatherAccess import get_duration_owt_markoff
from utils.WeatherAccess import get_probability_for_operations_naive
from utils.WeatherAccess import get_duration_for_operation_naive
from utils.WeatherAccess import get_duration_OWT_naive
from mainFunctions.OptimizationModels import generate_plan

def compute_open_loop_solution(scenario, current_iteration):

    N_Data = scenario.N + max(2 * 168, scenario.T)
    N_Data_Long = scenario.N + (2 * (N_Data - scenario.N))
    
    solution = None
    values = {
        'expectedDuration': None,
        'realDuration': None,
        'wind': None,
        'wave': None
    }

    tmp_solution, tmp_values = try_get_stored_solution(scenario)

    if tmp_solution is not None and ((scenario.useHistoricSolutions == 1 and current_iteration <= scenario.useHistoricTillIteration) or \
            ((tmp_solution.optim_exitflag == 1 or tmp_solution.optim_exitflag == 5) and SETTINGS['USE_SAVED_OPTIMALSOLUTION'] == 1)):
        solution = tmp_solution
        values = tmp_values

    if values['realDuration'] is None:
        # Get Weather data
        printMsg("> Retrieving weather info")
        w_wind, w_waves = get_weather_data(scenario.currentDate.year,
                                         scenario.currentDate.month, scenario.currentDate.day,
                                         scenario.currentDate.hour, N_Data_Long)

        # Generate Forecast
        printMsg("> Generating Forecast")
        waves, wind = get_forecast(w_wind, w_waves)

        if SETTINGS['USE_SLIDINGWINDOW'] == 1:
            # Estimate Duration for OWT NAIVE
            printMsg("> Estimating durations with sliding windows")
            printMsg(">> Calculating Probability to complete operation o at time t")
            probabilities, probabilities_real = get_probability_for_operations_naive(
                N_Data_Long, wind, waves, scenario.opData)

            printMsg(">> Estimating duration for operations")
            expDurComp, realDurComp, expProbComp = get_duration_for_operation_naive(
                N_Data, N_Data_Long, probabilities, probabilities_real, scenario.opData, SETTINGS['USE_SLIDINGWINDOW_OMEGA'])

            printMsg(">> Estimating duration for OWT")
            expDurOWT, realDurOWT, expProb = get_duration_OWT_naive(
                scenario.N, expDurComp, realDurComp, expProbComp, scenario.processChain_Install)

            expectedDuration = np.vstack([expDurOWT,
                                          expDurComp[scenario.processChain_Move, 0:scenario.N],
                                          expDurComp[scenario.processChain_Move, 0:scenario.N],
                                          expDurComp[scenario.processChain_Load, 0:scenario.N]])
            realDuration = np.vstack([realDurOWT,
                                      realDurComp[scenario.processChain_Move, 0:scenario.N],
                                      realDurComp[scenario.processChain_Move, 0:scenario.N],
                                      realDurComp[scenario.processChain_Load, 0:scenario.N]])

        else:
            # Estimate Duration for OWT MARKOV
            wind_r = np.column_stack([wind[:, 1] - 0.01, wind[:, 1], wind[:, 1] + 0.01])
            waves_r = np.column_stack([waves[:, 1] - 0.01, waves[:, 1], waves[:, 1] + 0.01])

            printMsg("> Estimating duration for OWT markoff style")
            jobsInCorrectOrder = scenario.opData[:, scenario.processChain_Install]
            marDurOWT = get_duration_owt_markoff(
                np.column_stack([wind, waves]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))

            marDurOWT_r = get_duration_owt_markoff(
                np.column_stack([wind_r, waves_r]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))
                
            jobsInCorrectOrder = scenario.opData[:, scenario.processChain_Move]
            marDurMove = get_duration_owt_markoff(
                np.column_stack([wind, waves]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))

            marDurMove_r = get_duration_owt_markoff(
                np.column_stack([wind_r, waves_r]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))
                
            jobsInCorrectOrder = scenario.opData[:, scenario.processChain_Load]
            marDurLoad = get_duration_owt_markoff(
                np.column_stack([wind, waves]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))

            marDurLoad_r = get_duration_owt_markoff(
                np.column_stack([wind_r, waves_r]), scenario.N, jobsInCorrectOrder[0, :],
                np.column_stack([jobsInCorrectOrder[1, :], jobsInCorrectOrder[2, :]]))
        
            expectedDuration = np.vstack([marDurOWT, marDurMove, marDurMove, marDurLoad])
            realDuration = np.vstack([marDurOWT_r, marDurMove_r, marDurMove_r, marDurLoad_r])

        expectedDuration = np.round(expectedDuration)
        realDuration = np.round(realDuration)

        if scenario.useForecasts == 0:
            expectedDuration = realDuration

        # Run optimizer to generate plan
        values['expectedDuration'] = expectedDuration
        values['realDuration'] = realDuration
        values['wind'] = wind
        values['wave'] = waves

    printMsg("> Run optimizer to generate plan")

    if solution is None:
        solution, exitflag = generate_plan(expectedDuration, scenario)

        solution.optim_exitflag = exitflag

        for v in range(scenario.numInstallationVessels):
            solution.x[v, 0, :] = solution.xOWT[v, :]
            solution.x[v, 1, :] = solution.xToPort[v, :]
            solution.x[v, 2, :] = solution.xToSite[v, :]
            solution.x[v, 3, :] = solution.xPortOp[v, :]
            solution.x[v, 4, :] = solution.xPortRestockOp[v, :]
            solution.x[v, 5, :] = solution.xBusy[v, :]
            solution.x[v, 6, :] = solution.xPortOpD[v, :]
            solution.x[v, 7, :] = solution.xOWT_TimeFinished[v, :]
            solution.x[v, 8, :] = solution.xMinorOps_TimeFinished[v, :]

        try_save_stored_solution(scenario, solution, values)
        solution.x = np.round(solution.x)
        solution.cost = np.round(solution.cost)
        solution.capacity = np.round(solution.capacity)
        solution.location = np.round(solution.location)

    else:
        try_save_stored_solution(scenario, solution, values)
        solution.x = np.round(solution.x)
        solution.cost = np.round(solution.cost)
        solution.capacity = np.round(solution.capacity)
        solution.location = np.round(solution.location)

    return solution, values

# Define or replace missing functions like  
# getWeatherData, getForecast, try_get_stored_solution, 
# getProbabilityForOperations_naive, getDurationForOperation_naive, 
# getDurationOWT_naive, getDurationOWT_markoff, generatePlan, 
# generatePlan_makespan, try_save_stored_solution, #
# getDurationOWT_markoff_old as per your implementation.

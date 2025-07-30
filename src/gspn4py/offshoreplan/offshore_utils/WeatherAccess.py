import numpy as np
import scipy

def get_weather_data(start_year, start_month, start_day, start_hour, N_Data):
    # Load weather data from the hard disk
    weatherdata = np.load('data/weatherdata.npy')

    # Get the index for the specified start date and time
    idx1 = date_to_weather_index(start_year, start_month, start_day, start_hour)

    # Extract wind and waves data for the specified range
    w_wind = weatherdata[0, idx1:idx1+N_Data]
    w_waves = weatherdata[1, idx1:idx1+N_Data]

    return w_wind, w_waves

def date_to_weather_index(year, month=1, day=1, hour=1):
    # Returns the index of the weather slot in the weather data (429191x2)
    # Input:
    #   year    integer
    #   month   integer (optional)  if left blank, the first month will be selected
    #   day     integer (optional)  if left blank, the first day will be selected
    #   hour    integer (optional)  if left blank, the first hour will be selected
    # Output:
    #   index   integer

    if month is None:
        month = 1
    if day is None:
        day = 1
    if hour is None:
        hour = 1

    month_lengths = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    index = (year - 1958) * 8759 + np.sum(month_lengths[:month-1]) * 24 + (day - 1) * 24 + hour - 1

    return index


def get_forecast(w_wind, w_wave):
    # Utility - length of the dataset
    length = len(w_wind)
    
    # Get mean windspeed and wave height for forecasting
    avg_wind = np.mean(w_wind)
    avg_wave = np.mean(w_wave)
    
    # Create container. 1= lower bound 2=real value 3=upper bound
    wind = np.zeros((length, 3))
    waves = np.zeros((length, 3))
    
    # Apply Uncertainty
    for i in range(length):
        v1 = w_wind[i]
        v2 = w_wave[i]
        
        # Calculate uncertainty for timestep.
        # Calc difference in hours between start and now,
        # and then get the corresponding multiplier from get_uncertainty
        uc = np.abs(get_uncertainty(i+1))   #added +1 to conform to matlab and anylogic
 
        # Fill arrays as 1= lower bound 2=real value 3= upper bound
        wind[i, 0] = v1 - avg_wind * uc
        wind[i, 1] = v1
        wind[i, 2] = v1 + avg_wind * uc
    
        waves[i, 0] = v2 - avg_wave * uc
        waves[i, 1] = v2
        waves[i, 2] = v2 + avg_wave * uc
    
    # Prevent data from becoming negative:
    wind = np.maximum(wind, 0)
    waves = np.maximum(waves, 0)
    
    return waves, wind

# Regression for basic accuracies
# 5Days ~ 90%; 7Days ~80%; 14Days ~50%;
# (21Days ~ https://scijinks.gov/forecast-reliability/)
def get_uncertainty(distH):
    x = [0, 168, 336, 504, 9999999]
    y = [0, 0.25, 0.65, 0.95, 0.99]
    uncertainty = np.interp(distH, x, y)
    return uncertainty


def get_duration_owt_markoff(weather, K, jobs_duration, jobs_requirements):
    estimated_duration = np.zeros(K)

    for i in range(K):
        estimated_duration[i] = get_duration_owt_markoff_single(weather[i:], jobs_duration, jobs_requirements)

    return estimated_duration



def get_duration_owt_markoff_single(weather, jobs_duration, jobs_requirements):
    n_jobs = len(jobs_duration)
    z0 = np.zeros(int(np.sum(jobs_duration)) + 1)
    z0[0] = 1
    zk = z0
    estimated_duration = 0

    for k in range(int(weather.shape[0] - np.max(jobs_duration))):
        probabilities = np.ones(n_jobs)
        for job in range(n_jobs):
            job_req = jobs_requirements[job, :]
            probabilities[job] = get_prob(weather[k : k + int(jobs_duration[job]), :], job_req)

        M = generate_markoff(probabilities, jobs_duration)
        probability_before = zk[-1]
        zk = np.dot(zk, M)
        estimated_duration += (k+1) * (zk[-1] - probability_before)

        if zk[-1] > 0.9973:  # 3 sigma
            break
        print("")

    if zk[-1] < 0.9973:
        print(f"Not enough forecast time to estimate sufficiently. Only {zk[-1]} of 1")

    return estimated_duration


def get_prob(weather, job_requirements):
    p = 1
    for k in range(weather.shape[0]):
        for r in range(2):  # requirements
            if p != 0:
                weather_max = weather[k, r * 3 + 2]
                weather_min = weather[k, 1 + 3 * r-1]
                jobs_req = job_requirements[r]

                if weather_max == weather_min:
                    if weather_min > jobs_req:
                        p = 0
                else:
                    if weather_max > jobs_req:
                        p = min(p, scipy.stats.norm.cdf(jobs_req, (weather_max + weather_min) / 2, (weather_max - (weather_max + weather_min) / 2) / 3))
                    elif weather_min > jobs_req:
                        p = 0

    return p

def generate_markoff(probabilities, durations):
    dim = int(np.sum(durations)) + 1
    M = np.zeros((dim, dim))

    for t in range(len(durations)):
        for step in range(int(durations[t])):
            idx1 = int(np.sum(durations[:t]))
            idx2 = int(np.sum(durations[:t])) + 1
                
            if step == 0:
                M[idx1, idx1] = 1 - probabilities[t]
                M[idx1, idx2] = probabilities[t]
            else:
                M[idx1 + step, idx2 + step] = 1

    M[int(np.sum(durations)) , int(np.sum(durations))] = 1

    return M

def get_probability_for_operations_naive(N_Data, wind, wave, opData):
    # Calculate Probabilities from uniform distrib w(1) <= rw = mean() <= w(3)
    #
    #  Input
    #   N_Data          integer         length of the Dataset
    #   wind            double 3xN      wind speed at timestep
    #                                   min(1)<real(2)<max(3)
    #   wave            double 3xN      wind speed at timestep
    #                                   min(1)<real(2)<max(3)
    #   opData          integer 3xNOp   1:Duration, 2:Max Wind, 3: Max Wave
    #
    #  Output:
    #   probabilities   double NOp x N_Data  Probability that an operation can
    #                   0-1                  can be performed at a given time
    #                                        based on min/max
    #   probabilities_real
    #                    double NOp x N_Data Probability that an operation can
    #                    0 or 1              can be performed at a given time
    #                                        based on real value 

    nOps = opData.shape[1]    
    probabilities = np.zeros((nOps, N_Data))
    probabilities_real = np.zeros((nOps, N_Data))
    
    wind = np.round(wind, 5)
    wave = np.round(wave, 5)
    
    for op in range(nOps):
        r_w = opData[1, op]
        r_v = opData[2, op]
        for idx in range(N_Data):
            
            # Get range of distribution
            range_w = np.abs(wind[idx, 2] - wind[idx, 0])
            range_v = np.abs(wave[idx, 2] - wave[idx, 0])
            
            # Get size of "acceptable" conditions
            bot_w = r_w - wind[idx, 0]
            bot_v = r_v - wave[idx, 0]
            
            # Normalize both values and clamp to 0-1
            prob_w = np.maximum(np.minimum(bot_w / max(range_w, 0.001), 1), 0)
            prob_v = np.maximum(np.minimum(bot_v / max(range_v, 0.001), 1), 0)
    
            # Just a boolean if possible or not in this window
            probabilities_real[op, idx] = min(wind[idx, 1] <= r_w, wave[idx, 1] <= r_v)
    
            # Overall we use the minimum probability for waves and wind
            probabilities[op, idx] = min(prob_w, prob_v)
    
    return probabilities, probabilities_real


def get_duration_for_operation_naive(N, N_Data, probabilities, probabilities_real, opData, minProbabilityForSlotAccepance):
    """
    Calculates the expected duration to perform a task using the provided
    probabilities for each time slot

    Args:
        N (int): Length of the prediction horizon (P*T)
        N_Data (int): Length of the forecasts. Should be larger than N to still have data at the end of N
        probabilities (ndarray): Probability [0; 1] if an operation can be performed at this time step.
                                Shape: (NumOperations x N_Data)
        probabilities_real (ndarray): Binary Array if an operation can be performed at this time step.
                                      Shape: (NumOperations x N_Data)
        opData (ndarray): Operation data, currently 3x9,
                          1st row = Duration
                          2nd row = Maximum Wind Speed
                          3rd row = Maximum Wave height
        minProbabilityForSlotAccepance (float): Slots will only be accepted if their cumulative probability is
                                                 greater or equal than this

    Returns:
        expDurComp (ndarray): Expected duration of operation at timestep
                              Shape: (9xN)
        realDurComp (ndarray): Actual duration of operation at timestep
                               Shape: (9xN)
        expProbComp (ndarray): Expected probability of operation to be done at this timeslot
                                Shape: (9xN)
    """
    expDurComp = np.zeros((len(opData[0]), N))
    realDurComp = np.zeros((len(opData[0]), N))
    expProbComp = np.zeros((len(opData[0]), N))

    for op in range(len(opData[0])):
        for t in range(N):
            # Shift forward until we find a long enough window
            # (opDuration) with a high enough probability (minProbabilityForSlotAccepance)
            # to perform the operation.
            # Expected duration is shift + dur
            # Probability for that slot is the product of every entry.
            for shift in range(N_Data - t - int(opData[0, op]) + 1):
                # Start
                s = t + shift
                # End
                e = t + shift + int(opData[0, op]) - 1
                # Probabilities in Window
                vals = probabilities[op, s:e + 1]
                # Probability in Slot
                prob_slot = np.prod(vals)
                # If Probability is good enough, save duration and probability
                # and break the for loop.
                if prob_slot >= minProbabilityForSlotAccepance:
                    expDurComp[op, t] = shift + opData[0, op]
                    expProbComp[op, t] = prob_slot
                    break

            # Do the same for the "real" duration. Here the probabilities
            # should always be 1 or 0 (can or can't do now)
            for shift in range(N_Data - t - int(opData[0, op]) + 1):
                s = t + shift
                e = t + shift + int(opData[0, op]) - 1
                vals = probabilities_real[op, s:e + 1]
                prob_slot = np.prod(vals)
                if prob_slot >= 0.1:
                    realDurComp[op, t] = shift + opData[0, op]
                    break

    return expDurComp, realDurComp, expProbComp


def get_duration_OWT_naive(N, eDC, rDC, eDP, processChain):
    # Inputs:
    #       N           integer scalar      Length of planning horizon
    #       eDC         numpy array          Expected duration to finish
    #                   (NOperations x N_Data) operation at timestep
    #       rDC         numpy array          Real duration to finish
    #                   (NOperations x N_Data) operation at timestep
    #       eDP         numpy array          Probability to finish operation
    #                   (NOperations x N_Data) at this time step
    #       processChain   numpy array       Array containing the sequence of
    #                                       operations needed to build an OWT
    # Outputs:
    #       expDur      numpy array         expected duration to finish an owt
    #                                       if started in timestep
    #       realDur     numpy array         real duration to finish an owt
    #                                       if started in timestep    
    #       expProb     numpy array         cumulative probability over all
    #                                       operations

    expDur = np.zeros(N)
    realDur = np.zeros(N)
    expProb = np.ones(N)
    
    # Now we know how long each op takes at each point in time
    # So, now let's use these to build the duration for one complete owt at
    # each timestep.
    for t in range(N):
        # current Time expected
        t0e = t
        # current Time for real weather data
        t0r = t
        # Get index of operation
        for idx_op in range(len(processChain)):
            # If we can't finish in time we set the duration to N
            if t0e >= len(eDC[0]):
                expDur[t] = N
                realDur[t] = N
                expProb[t] = 0
                t0r = N
                t0e = N
                print('Estimation for operations is not long enough to estimate installation duration')
            # Get operation
            op = processChain[idx_op]
            # Get duration for expected and real
            de = eDC[op, t0e]
            dr = rDC[op, t0r]
            # Add up in the results array
            expDur[t] += de
            realDur[t] += dr
            expProb[t] *= eDP[op, t0e]
            # Increase current time to the end of the selected operation
            t0e += int(de)
            t0r += int(dr)
            
    return expDur, realDur, expProb

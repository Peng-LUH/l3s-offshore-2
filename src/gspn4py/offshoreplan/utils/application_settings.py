import numpy as np

SETTINGS = { 
    'USE_SLIDINGWINDOW' : 1,
    'USE_NUMEICS' : 1,
    'PAUSE' : 0,
    'USE_SLIDINGWINDOW_OMEGA' : 0.45,
    'USE_SAVED_OPTIMALSOLUTION' : 0,

    'solutions_keyset' : np.array([]),
    'solutions_values' : np.array([]),
    'solutions_durations' : np.array([]),
    'loadedSolutions' : np.array([])
    }


#USE_SLIDINGWINDOW = 0
#USE_NUMEICS = 1
#PAUSE = 0
#USE_SLIDINGWINDOW_OMEGA = 0.45
#USE_SAVED_OPTIMALSOLUTION = 0

#solutions_keyset = np.array([])
#solutions_values = np.array([])
#solutions_durations = np.array([])
#loadedSolutions = np.array([])
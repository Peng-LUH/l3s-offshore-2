import numpy as np
import h5py

# Load data from MATLAB .mat file using h5py
with h5py.File('weatherdata.mat', 'r') as mat_file:
    # Extract the variable you want to save (adjust the dataset name accordingly)
    weatherdata = mat_file['weatherdata'][:]

# Save the data to a NumPy .npy file
np.save('weatherdata.npy', weatherdata)
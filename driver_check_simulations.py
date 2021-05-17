# -*- coding: utf-8 -*-
"""
Created on Mon May 17 09:33:12 2021

@author: nicol
"""


# Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tqdm


# Model parameters
param = pd.read_csv('data/param.csv')


#%%  Check Aggregate Infection Status

scenario = 3
sim = 0

# Preallocate for infection process
yt = np.zeros((param['simulation_length'][0], 4))


# Preallocate for demographic numbers
pt = np.zeros((param['simulation_length'][0], 4))


# Iterate over all output files
for t in tqdm.tqdm(range(0, param['simulation_length'][0])):


    # Read in file
    meta = pd.read_feather('simulations/output/scenario_' + str(scenario) + '/simulation_' + str(sim) + '/timestep' + str(param['partner_burn_in'][0] + t) + '.ftr')


    # Compute the number in each infectious state
    yt[t,:] = [sum(meta.state == 'S'),
               sum( (meta.state == 'I') & ( (meta.site0_t0 > t) & (meta.site1_t0 > t) & (meta.site2_t0 > t) ) ),
               sum( (meta.state == 'I') & ( (meta.site0_t0 < t) | (meta.site1_t0 < t) | (meta.site2_t0 < t) ) ),
               sum(meta.state == 'R')]


    # Compute the number in each age group
    pt[t,:] = [sum(meta.age_group == 0),
               sum(meta.age_group == 1),
               sum(meta.age_group == 2),
               sum(meta.age_group == 3)]


#%% Make plots


# Plot aggregate infection levels
t = range(0, param['simulation_length'][0])
# plt.plot(t, yt[:,0], label = 'S')
plt.plot(t, yt[:,1], label = 'E')
plt.plot(t, yt[:,2], label = 'I')
plt.plot(t, yt[:,3], label = 'R')
plt.legend()
plt.show()


# Plot the number in each age group
plt.plot(t, pt[:,0], label = '16-19')
plt.plot(t, pt[:,1], label = '20-24')
plt.plot(t, pt[:,2], label = '25-30')
plt.plot(t, pt[:,3], label = 'Over 30')
plt.legend()


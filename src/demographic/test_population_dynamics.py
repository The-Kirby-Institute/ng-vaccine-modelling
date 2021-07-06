# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 09:57:13 2021

@author: nicol
"""


#%% SETUP Modules


# Standard modules
import numpy as np
import pandas as pd
import tqdm as tqdm
import matplotlib.pyplot as plt
import time


# My modules
import src.demographic.generate_population as pop
import src.demographic.population_dynamics as demo
import src.calibration.setup as setup


run_mode = 'serial'
scenario = 3
population_no = 0


#%% SETUP Parse simulation data


# Parse population parameters
pop_parameters = pop.setup_data(scenario, run_mode)


# Parse infection parameters
# Pass this function which numbered parameter set you want to use
# Will default back to the baseline parameter set
inf_parameters = setup.parse_parameters('calibration', scenario)


# Read in population data
meta = pd.read_feather('simulations/populations/scenario_' + str(scenario) + '/population_' + str(population_no) + '.ftr')


# Initilise partnership data
partner_matrix = pop.initilise_partner_matrix(pop_parameters)
partner_expire = pop.initilise_partner_duration(pop_parameters)


# Initilise importation data
pop_parameters = demo.initilise_demographic_dynamics(pop_parameters, inf_parameters, meta)


# Print
if run_mode == 'serial':
    print('Parsing scenario ' + str(scenario))
    print('Parameter set: default')
    print('Population set: ' + str(population_no) + '\n')


#%% RUN Simulation


# Track partnership numbers
n_steps = 5*365
tt = range(0, n_steps)
compartments = np.zeros((n_steps, 10))
import_count = np.zeros((n_steps, 10))


# Time code
t0 = time.time()


# Check to see if this dataset has been run to completion
( print('Running simulation...\n', flush = True) if run_mode == 'serial' else [] )
# for t in tqdm.tqdm(range(sim_parameters.partner_burn_in[0], sim_parameters.partner_burn_in[0] + sim_parameters.simulation_length[0])):
# for t in range(sim_parameters.partner_burn_in[0], sim_parameters.partner_burn_in[0] + sim_parameters.simulation_length[0]):
for t in tqdm.tqdm(tt):


    # Update population
    meta, partner_matrix, partner_expire = demo.update_population(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


    # How many are in each compartment?
    compartments[t, 0] = sum(pop_parameters['lookup']['GA00'])
    compartments[t, 1] = sum(pop_parameters['lookup']['GA01'])
    compartments[t, 2] = sum(pop_parameters['lookup']['GA02'])
    compartments[t, 3] = sum(pop_parameters['lookup']['GA03'])
    compartments[t, 4] = sum(pop_parameters['lookup']['GA04'])
    compartments[t, 5] = sum(pop_parameters['lookup']['GA10'])
    compartments[t, 6] = sum(pop_parameters['lookup']['GA11'])
    compartments[t, 7] = sum(pop_parameters['lookup']['GA12'])
    compartments[t, 8] = sum(pop_parameters['lookup']['GA13'])
    compartments[t, 9] = sum(pop_parameters['lookup']['GA14'])


    # Specifically, how many have been imported?
    new_import = meta.import_time == t
    import_count[t, 0] = sum((pop_parameters['lookup']['GA00']) & new_import)
    import_count[t, 1] = sum((pop_parameters['lookup']['GA01']) & new_import)
    import_count[t, 2] = sum((pop_parameters['lookup']['GA02']) & new_import)
    import_count[t, 3] = sum((pop_parameters['lookup']['GA03']) & new_import)
    import_count[t, 4] = sum((pop_parameters['lookup']['GA04']) & new_import)
    import_count[t, 5] = sum((pop_parameters['lookup']['GA10']) & new_import)
    import_count[t, 6] = sum((pop_parameters['lookup']['GA11']) & new_import)
    import_count[t, 7] = sum((pop_parameters['lookup']['GA12']) & new_import)
    import_count[t, 8] = sum((pop_parameters['lookup']['GA13']) & new_import)
    import_count[t, 9] = sum((pop_parameters['lookup']['GA14']) & new_import)


# Print update
runtime = (time.time() - t0)/60
rt_min = int(np.floor(runtime))
rt_sec = int(60 * (runtime - rt_min))
print('\nRuntime: ' + str(rt_min) + ' min ' + str(rt_sec) + ' seconds')


#%% GRAPHS


# Initilise figure
fig, axs = plt.subplots(5, 2)


# Number in the compartment
axs[0, 0].plot(tt, compartments[:,0])
axs[1, 0].plot(tt, compartments[:,1])
axs[2, 0].plot(tt, compartments[:,2])
axs[3, 0].plot(tt, compartments[:,3])
axs[4, 0].plot(tt, compartments[:,4])

axs[0, 1].plot(tt, compartments[:,5])
axs[1, 1].plot(tt, compartments[:,6])
axs[2, 1].plot(tt, compartments[:,7])
axs[3, 1].plot(tt, compartments[:,8])
axs[4, 1].plot(tt, compartments[:,9])


# Target number for compartments
targetF = pop_parameters['age_dist'].ave[pop_parameters['age_dist'].sex == 0].reset_index(drop=True) * (1-pop_parameters['sex_dist']['pMale'].iloc[0]) * pop_parameters['n']
targetM = pop_parameters['age_dist'].ave[pop_parameters['age_dist'].sex == 1].reset_index(drop=True) * pop_parameters['sex_dist']['pMale'].iloc[0] * pop_parameters['n']
axs[0, 0].plot(tt, ([targetF[0]] * len(tt)), linestyle = '--')
axs[1, 0].plot(tt, ([targetF[1]] * len(tt)), linestyle = '--')
axs[2, 0].plot(tt, ([targetF[2]] * len(tt)), linestyle = '--')
axs[3, 0].plot(tt, ([targetF[3]] * len(tt)), linestyle = '--')
axs[4, 0].plot(tt, ([targetF[4]] * len(tt)), linestyle = '--')

axs[0, 1].plot(tt, ([targetM[0]] * len(tt)), linestyle = '--')
axs[1, 1].plot(tt, ([targetM[1]] * len(tt)), linestyle = '--')
axs[2, 1].plot(tt, ([targetM[2]] * len(tt)), linestyle = '--')
axs[3, 1].plot(tt, ([targetM[3]] * len(tt)), linestyle = '--')
axs[4, 1].plot(tt, ([targetM[4]] * len(tt)), linestyle = '--')


# Axis labels
plt.suptitle('Demographic Sizes Over Time')
axs[0, 0].set_title('Females')
axs[0, 1].set_title('Males')
axs[0, 0].set_ylabel('16-19')
axs[1, 0].set_ylabel('20-24')
axs[2, 0].set_ylabel('25-29')
axs[3, 0].set_ylabel('30-34')
axs[4, 0].set_ylabel('35')
axs[4, 0].set_xlabel('Day')
axs[4, 1].set_xlabel('Day')
plt.show()


## Importations


# Initilise figure
fig, axs = plt.subplots(5, 2)


# Number of imports
import_count[0,:] = 0
axs[0, 0].plot(tt, import_count[:,0])
axs[1, 0].plot(tt, import_count[:,1])
axs[2, 0].plot(tt, import_count[:,2])
axs[3, 0].plot(tt, import_count[:,3])
axs[4, 0].plot(tt, import_count[:,4])

axs[0, 1].plot(tt, import_count[:,5])
axs[1, 1].plot(tt, import_count[:,6])
axs[2, 1].plot(tt, import_count[:,7])
axs[3, 1].plot(tt, import_count[:,8])
axs[4, 1].plot(tt, import_count[:,9])


# Mean import_count
import_count[0,:] = 0
axs[0, 0].plot(tt, len(tt) * [np.mean(import_count[:,0])], linestyle = '--')
axs[1, 0].plot(tt, len(tt) * [np.mean(import_count[:,1])], linestyle = '--')
axs[2, 0].plot(tt, len(tt) * [np.mean(import_count[:,2])], linestyle = '--')
axs[3, 0].plot(tt, len(tt) * [np.mean(import_count[:,3])], linestyle = '--')
axs[4, 0].plot(tt, len(tt) * [np.mean(import_count[:,4])], linestyle = '--')

axs[0, 1].plot(tt, len(tt) * [np.mean(import_count[:,5])], linestyle = '--')
axs[1, 1].plot(tt, len(tt) * [np.mean(import_count[:,6])], linestyle = '--')
axs[2, 1].plot(tt, len(tt) * [np.mean(import_count[:,7])], linestyle = '--')
axs[3, 1].plot(tt, len(tt) * [np.mean(import_count[:,8])], linestyle = '--')
axs[4, 1].plot(tt, len(tt) * [np.mean(import_count[:,9])], linestyle = '--')


# Axis labels
plt.suptitle('Number of Importations')
axs[0, 0].set_title('Females')
axs[0, 1].set_title('Males')
axs[0, 0].set_ylabel('16-19')
axs[1, 0].set_ylabel('20-24')
axs[2, 0].set_ylabel('25-29')
axs[3, 0].set_ylabel('30-34')
axs[4, 0].set_ylabel('35')
axs[4, 0].set_xlabel('Day')
axs[4, 1].set_xlabel('Day')
plt.show()


## Net change


# Initilise figure
fig, axs = plt.subplots(5, 2)


# Net change in population size
axs[0, 0].plot(tt[1:len(tt)], (compartments[1:len(tt),0] - compartments[0:(len(tt)-1),0] - import_count[1:len(tt),0]))
axs[1, 0].plot(tt[1:len(tt)], (compartments[1:len(tt),1] - compartments[0:(len(tt)-1),1] - import_count[1:len(tt),1]))
axs[2, 0].plot(tt[1:len(tt)], (compartments[1:len(tt),2] - compartments[0:(len(tt)-1),2] - import_count[1:len(tt),2]))
axs[3, 0].plot(tt[1:len(tt)], (compartments[1:len(tt),3] - compartments[0:(len(tt)-1),3] - import_count[1:len(tt),3]))
axs[4, 0].plot(tt[1:len(tt)], (compartments[1:len(tt),4] - compartments[0:(len(tt)-1),4] - import_count[1:len(tt),4]))

axs[0, 1].plot(tt[1:len(tt)], (compartments[1:len(tt),5] - compartments[0:(len(tt)-1),5] - import_count[1:len(tt),5]))
axs[1, 1].plot(tt[1:len(tt)], (compartments[1:len(tt),6] - compartments[0:(len(tt)-1),6] - import_count[1:len(tt),6]))
axs[2, 1].plot(tt[1:len(tt)], (compartments[1:len(tt),7] - compartments[0:(len(tt)-1),7] - import_count[1:len(tt),7]))
axs[3, 1].plot(tt[1:len(tt)], (compartments[1:len(tt),8] - compartments[0:(len(tt)-1),8] - import_count[1:len(tt),8]))
axs[4, 1].plot(tt[1:len(tt)], (compartments[1:len(tt),9] - compartments[0:(len(tt)-1),9] - import_count[1:len(tt),9]))


# Mean net change
axs[0, 0].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),0] - compartments[0:(len(tt)-1),0] - import_count[1:len(tt),0]))], linestyle = '--')
axs[1, 0].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),1] - compartments[0:(len(tt)-1),1] - import_count[1:len(tt),1]))], linestyle = '--')
axs[2, 0].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),2] - compartments[0:(len(tt)-1),2] - import_count[1:len(tt),2]))], linestyle = '--')
axs[3, 0].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),3] - compartments[0:(len(tt)-1),3] - import_count[1:len(tt),3]))], linestyle = '--')
axs[4, 0].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),4] - compartments[0:(len(tt)-1),4] - import_count[1:len(tt),4]))], linestyle = '--')

axs[0, 1].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),5] - compartments[0:(len(tt)-1),5] - import_count[1:len(tt),5]))], linestyle = '--')
axs[1, 1].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),6] - compartments[0:(len(tt)-1),6] - import_count[1:len(tt),6]))], linestyle = '--')
axs[2, 1].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),7] - compartments[0:(len(tt)-1),7] - import_count[1:len(tt),7]))], linestyle = '--')
axs[3, 1].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),8] - compartments[0:(len(tt)-1),8] - import_count[1:len(tt),8]))], linestyle = '--')
axs[4, 1].plot(tt, len(tt) * [np.mean((compartments[1:len(tt),9] - compartments[0:(len(tt)-1),9] - import_count[1:len(tt),9]))], linestyle = '--')


# Axis labels
plt.suptitle('Change in Age Groups (Age Dynamics)')
axs[0, 0].set_title('Females')
axs[0, 1].set_title('Males')
axs[0, 0].set_ylabel('16-19')
axs[1, 0].set_ylabel('20-24')
axs[2, 0].set_ylabel('25-29')
axs[3, 0].set_ylabel('30-34')
axs[4, 0].set_ylabel('35')
axs[4, 0].set_xlabel('Day')
axs[4, 1].set_xlabel('Day')
plt.show()
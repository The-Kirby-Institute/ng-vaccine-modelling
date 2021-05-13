# -*- coding: utf-8 -*-
"""
Created on Wed May  5 12:59:05 2021

@author: Nicolas Rebuli

This script will generate a number of synthetic populations and then run
the partnership dynamics for a burn in period before saving the output.

The parameters are as follows:
    param.n_populations = the number of populations to simulate
    param.partner_burn_in = the number of days to run the partnership dynamics for
"""


#%% SETUP Load Modules


# Load libraries
import numpy as np
import pandas as pd
# import feather
# import matplotlib.pyplot as plt
import tqdm as tqdm


# For clearing out directories
import os
import glob


# Load modules for simulation script
import src.demographic.generate_population as pop
import src.partners.partners as prt
# import src.infections.ng as ng
# import src.treatment.simple as trt


# Load in graphing modules
import src.partners.summary_stats as pstat
# import src.infections.summary_stats as istat


# Read in simulation parameters
param = pd.read_csv("data/param.csv")


#%% SETUP Script parameters


# Which things should be generated here
generate_populations = True
burn_in_partnerships = True
track_partnership_rates = True


# Set whether or not you want to overwrite the existing data
recovery_mode = True


#%% RUN Generate Populations


# Continue if populations have been asked to be regenrated
if generate_populations:


    # Print an update
    print('Generating ' + str(param.n_populations[0]) + ' synthetic populations for each scenario\n', flush = True)


    # Purge the directory if not in recovery mode
    if recovery_mode == False:


        # Identify all existing population data
        files = \
            glob.glob('simulations/populations/scenario_1/*') + \
            glob.glob('simulations/populations/scenario_2/*') + \
            glob.glob('simulations/populations/scenario_3/*')


        # Delete them all
        for f in files:
            os.remove(f)


    # Iterate over the scenario number
    for scenario in [1, 2, 3]:


        # Parse demographic parameters for population
        pop_parameters = pop.setup_data(scenario)


        # Iterate over the simulation number
        for i in tqdm.tqdm(range(0, param.n_populations[0])):


            # Check if the file is there already or not
            file_name = 'simulations/populations/scenario_' + str(scenario) + '/population_' + str(i)
            if os.path.exists(file_name + '.ftr') == False:


                # Generate population
                meta = pop.generate_population(pop_parameters)


                # Store population
                meta.to_feather(file_name + '.ftr')


                # Make graphs of the population
                pop.graph_population(pop_parameters, meta, file_name)


#%% RUN Burn in Partnership Networks


# Continue if this has been asked for
if burn_in_partnerships:


    # Purge the directory if not in recovery mode
    if recovery_mode == False:


        # Identify all existing partnership data
        files = \
            glob.glob('simulations/partnerships/scenario_1/*') + \
            glob.glob('simulations/partnerships/scenario_2/*') + \
            glob.glob('simulations/partnerships/scenario_3/*')


        # Delete them all
        for f in files:
            os.remove(f)


    # Iterate over the scenario number
    for scenario in [1, 2, 3]:


        # Parse demographic parameters for population
        pop_parameters = pop.setup_data(scenario)


        # Iterate over the simulation number
        for i in range(0, param.n_populations[0]):
            print('Burn in for population ' + str(i) + ' of scenario ' + str(scenario) + '\n', flush = True)


            # Skip file if it is already there
            save_dir = 'simulations/partnerships/scenario_' + str(scenario) + '/population_' + str(i)
            if os.path.exists(save_dir + '_matrix.npy') == False:


                # Initilise data for burn in
                n_days = param.partner_burn_in[0]
                p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt, _, _, _, _, _ = pstat.initilise_partner_number_tracking(n_days)
                partner_matrix = pop.initilise_partner_matrix(pop_parameters)
                partner_expire = pop.initilise_partner_duration(pop_parameters)
                file_name_pop = 'simulations/populations/scenario_' + str(scenario) + '/population_' + str(i) + '.ftr'
                meta = pd.read_feather(file_name_pop)


                # Run Partnership Dynamics
                for t in tqdm.tqdm(range(0, n_days)):
                    meta, partner_matrix, partner_expire, d0ti, d1ti, d2ti, d3ti = prt.new_partnership(meta, partner_matrix, partner_expire, t)
                    meta, partner_matrix, partner_expire = prt.old_partnerships(meta, partner_matrix, partner_expire, t)
                    if track_partnership_rates:
                        p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt = pstat.update_partnership_types(meta, partner_matrix, t, p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt)


                # Store data for later
                meta.to_feather(file_name_pop)
                np.save(save_dir + '_matrix.npy', partner_matrix)
                np.save(save_dir + '_expire.npy', partner_expire)


                # Graph Partnership dynamics
                if track_partnership_rates:
                    pstat.graph_partnership_numbers(meta, n_days, p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt, save_dir)









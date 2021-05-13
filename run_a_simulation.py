# -*- coding: utf-8 -*-
"""
Created on Fri May  7 08:21:20 2021

@author: Nicolas Rebuli

This script will run a fully fledged
"""
scenario = 3
parameter_no = 2
out_dir = 'simulations/output/scenario_' + str(scenario) +'/simulation_' + str(parameter_no)


#%% SETUP Modules


# Standard modules
import numpy as np
import pandas as pd
import tqdm as tqdm
import random
import shelve
from pathlib import Path
import shutil
import os


# My modules
import src.demographic.generate_population as pop
import src.demographic.population_dynamics as demo
import src.partners.partners as prt
import src.calibration.setup as setup
import src.infections.ng as ng


#%% SETUP Simulation data


# Read in simulation parameters
sim_parameters = pd.read_csv('data/param.csv')


# Parse infection parameters
# Pass this function which numbered parameter set you want to use
# Will default back to the baseline parameter set
inf_parameters = setup.parse_parameters(parameter_no)


# Parse demographic parameters for population
# Pass this function the scenario number
# Will default back to scenario 0
pop_parameters = pop.setup_data(scenario)


# Parse simulated population
# Pass this function the scenario number and which simulated population to use
# Will default back to scenario 1 and population 0 if none selected
population_no = random.randint(0, sim_parameters.n_populations[0]-1)
meta, partner_expire, partner_matrix = setup.parse_population_data(scenario, population_no)


#%% SETUP Output Directory


# Clean out directory from any previous results
dirpath = Path(out_dir)
if dirpath.exists() and dirpath.is_dir():
    shutil.rmtree(dirpath)


# Remake the directory
os.mkdir(dirpath)


#%% RUN


for t in tqdm.tqdm(range(sim_parameters.partner_burn_in[0], sim_parameters.partner_burn_in[0] + sim_parameters.simulation_length[0])):


    # Update population
    meta, partner_matrix, partner_expire = demo.update_population(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


    # Update partnerships
    meta, partner_matrix, partner_expire = prt.update_partnerships(meta, partner_matrix, partner_expire, t)


    # Update infections
    meta = ng.update_infections(inf_parameters, meta, partner_matrix, t)


    # Dump simulation output
    meta.to_feather(out_dir + '/timestep' + str(t) + '.ftr')


#%% SAVE OUTPUT


# Shelve variables
my_shelf = shelve.open(out_dir + '_workspace.out', 'n')
for key in dir():
    try:
        my_shelf[key] = globals()[key]
    except:
        #
        # __builtins__, my_shelf, and imported modules can not be shelved.
        #
        print('ERROR shelving: {0}'.format(key))
my_shelf.close()



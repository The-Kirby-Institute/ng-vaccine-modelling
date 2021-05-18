# -*- coding: utf-8 -*-
"""
Created on Fri May  7 10:22:21 2021

@author: Nicolas Rebuli
"""

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


run_mode = 'parallel'


#%% FUN parse_population_data()
#
#
# A function which loads in population data
#
#
def parse_population_data(scenario = 'default', set = 0):


    # Work out if you need to read in the default set or not
    if scenario == 'default':
        # Read in the default set
        ( print('Parsing default population dataset (scenario 1 and population 0).\n', flush = True) if run_mode == 'serial' else [] )
        scenario = 1
        set = 0

    else:
        # Read in a specific set
        ( print('Parsing simulated population dataset ' + str(set) + '.\n', flush = True) if run_mode == 'serial' else [] )


    # Read in the population metadata dataframe
    meta = pd.read_feather('simulations/populations/scenario_' + str(scenario) + '/population_' + str(set) + '.ftr')


    # Check that the duration exposed is correct in meta
    sim_parameters = pd.read_csv('data/param.csv')
    meta.loc[meta.site0 == 1, 'site0_t0'] = sim_parameters.partner_burn_in[0] + sim_parameters.init_duration_exposed[0] * np.random.random(sum(meta.site0 == 1))
    meta.loc[meta.site1 == 1, 'site1_t0'] = sim_parameters.partner_burn_in[0] + sim_parameters.init_duration_exposed[0] * np.random.random(sum(meta.site1 == 1))
    meta.loc[meta.site2 == 1, 'site2_t0'] = sim_parameters.partner_burn_in[0] + sim_parameters.init_duration_exposed[0] * np.random.random(sum(meta.site2 == 1))


    # Read in the simulated partnership data arrays
    partner_expire = np.load('simulations/partnerships/scenario_' + str(scenario) + '/population_' + str(set) + '_expire.npy')
    partner_matrix = np.load('simulations/partnerships/scenario_' + str(scenario) + '/population_' + str(set) + '_matrix.npy')


    # Return data
    return meta, partner_expire, partner_matrix


#%% FUN parse_default_parameters()
#
#
# A function to parse the standard model parameters stored in the data folder.
#
#
def parse_default_parameters():


    # Parse parameters controlling infection dynamics and regular clinical treatment
    infection = pd.read_csv('data/ng_anatomical_site_infectious_period.csv')


    # Parse parameters controlling the probability of engaging in different
    # sexual acts. Read matrices as the probability of somebody of sex i
    # engaging in the given sex act with somebody of sex j. Where the order
    # of i and j are female then male.
    p_anal = pd.read_csv('data/sexual_act_probability_anal.csv').to_numpy()
    p_oral = pd.read_csv('data/sexual_act_probability_oral.csv').to_numpy()
    p_kiss = pd.read_csv('data/sexual_act_probability_kiss.csv').to_numpy()
    p_rim = pd.read_csv('data/sexual_act_probability_rim.csv').to_numpy()
    p_sex = pd.read_csv('data/sexual_act_probability_sex.csv').to_numpy()


    # Parse parameters controlling the probability of anatomical site specific
    # transmission as a result of engaging in particular sex acts


    # Form the site-to-site transmission probability matrix for convenience.
    # Read as the probability of transmission from site i to site j
    # Sites are in the order: rectal, urethral, pharangeal
    s2s = pd.read_csv('data/ng_anatomical_site_to_site_transmission_probabilities.csv').to_numpy()


    # Compose matrix with transmission probabilities as a result of anal sex
    trans_anal = np.array([[0,          s2s[0,1],   0],
                           [s2s[1,0],   0,          0],
                           [0,          0,          0]])


    # Compose matrix with transmission probabilities as a result of oral sex
    trans_oral = np.array([[0,          0,          0],
                           [0,          0,          s2s[1,2]],
                           [0,          s2s[2,1],   0]])


    # Compose matrix with transmission probabilities as a result of kissing
    trans_kiss = np.array([[0,          0,          0],
                           [0,          0,          0],
                           [0,          0,          s2s[2,2]]])


    # Compose matrix with transmission probabilities as a result of rimming
    trans_rim = np.array([[0,           0,          s2s[0,2]],
                          [0,           0,          0],
                          [s2s[2,0],    0,          0]])


    # Compose matrix with transmission probabilities as a result of sex
    trans_sex = np.array([[0,           0,          0],
                          [0,           s2s[1,1],   0],
                          [0,           0,          0]])


    # Combine everything into a dictionary
    parameters = {'set': 'default',
                  'infection': infection,
                  'p_anal': p_anal,
                  'p_oral': p_oral,
                  'p_kiss': p_kiss,
                  'p_sex': p_sex,
                  'p_rim': p_rim,
                  'trans_anal': trans_anal,
                  'trans_oral': trans_oral,
                  'trans_kiss': trans_kiss,
                  'trans_sex': trans_sex,
                  'trans_rim': trans_rim}


    # Return the parameters in dictionary form
    return parameters


#%% FUN parse_custom_parameters()
#
#
# A function to parse the model parameters stored in a csv to the
# format that the code requires.
#
#
def parse_custom_parameters(i):


    # Access the relevent set of parameters
    parameters = pd.read_csv('simulations/parameters.csv')
    parameters = parameters.iloc[i,:]


    # Parse parameters controlling infection dynamics and regular clinical treatment
    infection   = pd.DataFrame({'sex': ['F', 'M'],
                                'mean_rectal': [parameters.mean_rectal] * 2,
                                'var_rectal': [parameters.var_rectal] * 2,
                                'symptoms_rectal': [parameters.symptoms_rectal] * 2,

                                'mean_urethral': [parameters.mean_ural_female, parameters.mean_ural_male],
                                'var_urethral': [parameters.var_ural_female, parameters.var_ural_male],
                                'symptoms_urethral': [parameters.symptoms_ural_female, parameters.symptoms_ural_male],

                                'mean_pharyngeal': [parameters.mean_phar] * 2,
                                'var_pharyngeal': [parameters.var_phar] * 2,
                                'symptoms_pharyngeal': [parameters.symptoms_phar] * 2,

                                'latent_period': [parameters.latent_period] * 2,

                                'treatment_mean': [parameters.treat_mean] * 2,
                                'treatment_var': [parameters.treat_var] * 2,

                                'immunity_mean': [parameters.immune_mean] * 2,
                                'immunity_var': [parameters.immune_var] * 2,

                                'import_prob': [parameters.import_prob] * 2})


    # Parse parameters controlling the probability of engaging in different
    # sexual acts. Read matrices as the probability of somebody of sex i
    # engaging in the given sex act with somebody of sex j. Where the order
    # of i and j are female then male.


    # Probabilities of engaging in anal sex
    p_anal = np.array([[0, 0],
                       [parameters.p_anal_MF, parameters.p_anal_MM]])


    # Probabilities of engaging in oral sex
    p_oral = np.array([[parameters.p_oral_FF, parameters.p_oral_FM],
                       [parameters.p_oral_MF, parameters.p_oral_MM]])


    # Proibabilities of kissing
    p_kiss = np.array([[parameters.p_kiss, parameters.p_kiss],
                       [parameters.p_kiss, parameters.p_kiss]])


    # Probabilities of engaging in sex or a related genital-to-genital act
    p_sex  = np.array([[parameters.p_sex_FF, parameters.p_sex_MF],
                       [parameters.p_sex_MF, parameters.p_sex_MM]])


    # Proibabilities of rimming (throat to butt)
    p_rim  = np.array([[parameters.p_rim, parameters.p_rim],
                       [parameters.p_rim, parameters.p_rim]])


    # Parse parameters controlling the probability of anatomical site specific
    # transmission as a result of engaging in particular sex acts


    # Form the site-to-site transmission probability matrix for convenience.
    # Read as the probability of transmission from site i to site j
    # Sites are in the order: rectal, urethral, pharangeal
    s2s = np.array([[0,              parameters.pru, parameters.prp],
                    [parameters.pur, parameters.puu, parameters.pup],
                    [parameters.ppr, parameters.ppu, parameters.ppp]])


    # Compose matrix with transmission probabilities as a result of anal sex
    trans_anal = np.array([[0,          s2s[0,1],   0],
                           [s2s[1,0],   0,          0],
                           [0,          0,          0]])


    # Compose matrix with transmission probabilities as a result of oral sex
    trans_oral = np.array([[0,          0,          0],
                           [0,          0,          s2s[1,2]],
                           [0,          s2s[2,1],   0]])


    # Compose matrix with transmission probabilities as a result of kissing
    trans_kiss = np.array([[0,          0,          0],
                           [0,          0,          0],
                           [0,          0,          s2s[2,2]]])


    # Compose matrix with transmission probabilities as a result of rimming
    trans_rim = np.array([[0,           0,          s2s[0,2]],
                          [0,           0,          0],
                          [s2s[2,0],    0,          0]])


    # Compose matrix with transmission probabilities as a result of sex
    trans_sex = np.array([[0,           0,          0],
                          [0,           s2s[1,1],   0],
                          [0,           0,          0]])


    # Combine everything into a dictionary
    parameters = {'set': 'simulation set ' + str(i),
                  'infection': infection,
                  'p_anal': p_anal,
                  'p_oral': p_oral,
                  'p_kiss': p_kiss,
                  'p_sex': p_sex,
                  'p_rim': p_rim,
                  'trans_anal': trans_anal,
                  'trans_oral': trans_oral,
                  'trans_kiss': trans_kiss,
                  'trans_sex': trans_sex,
                  'trans_rim': trans_rim}


    # Return the parameters in dictionary form
    return parameters


#%% FUN parse_parameters()
#
#
# A function to load parameters.
#
# Loads the defaults if no file number is specified
#
#
def parse_parameters(set = 'default'):


    # Work out if you need to read in the default set or not
    if set == 'default':
        # Read in the default set
        ( print('Parsing default parameter set.\n') if run_mode == 'serial' else [] )
        parameters = parse_default_parameters()

    else:
        # Read in the numbered set
        ( print('Parsing simulated parameter set ' + str(set) + '.\n') if run_mode == 'serial' else [] )
        parameters = parse_custom_parameters(set)


    return parameters


#%% FUN run_one_parameter_set()
def run_one_parameter_set(parameter_no):


    # Run first parameter set
    ( print('\nRunning scenario 1 - with parameter set ' + str(parameter_no) + '\n===========================================') if run_mode == 'serial' else [] )
    run_one_simulation(1, parameter_no)


    # Run second parameter set
    # print('\nRunning scenario 2 - with parameter set ' + str(parameter_no) + '\n===========================================')
    # run_one_simulation(2, parameter_no)


    # Run third parameter set
    # print('\nRunning scenario 3 - with parameter set ' + str(parameter_no) + '\n===========================================')
    # run_one_simulation(3, parameter_no)


#%% FUN run_one_simulation()
def run_one_simulation(scenario, parameter_no):


    # SETUP Simulation data


    # Read in simulation parameters
    ( print('Parsing global simulation settings.\n') if run_mode == 'serial' else [] )
    sim_parameters = pd.read_csv('data/param.csv')


    # Parse infection parameters
    # Pass this function which numbered parameter set you want to use
    # Will default back to the baseline parameter set
    inf_parameters = setup.parse_parameters(parameter_no)


    # Parse demographic parameters for population
    # Pass this function the scenario number
    # Will default back to scenario 0
    pop_parameters = pop.setup_data(scenario, run_mode)


    # Parse simulated population
    # Pass this function the scenario number and which simulated population to use
    # Will default back to scenario 1 and population 0 if none selected
    population_no = random.randint(0, sim_parameters.n_populations[0]-1)
    meta, partner_expire, partner_matrix = setup.parse_population_data(scenario, population_no)


    # Print update
    ( print('Running parameter set: ' + str(parameter_no) + ' on scenario: ' + str(scenario) + ' with population: ' + str(population_no)) if run_mode == 'parallel' else [] )


    #% SETUP Output Directory


    # Clean out directory from any previous results
    ( print('Purging simulation output directory.\n') if run_mode == 'serial' else [] )
    out_dir = 'simulations/output/scenario_' + str(scenario) +'/simulation_' + str(parameter_no)
    dirpath = Path(out_dir)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)


    # Remake the directory
    os.mkdir(dirpath)


    #% RUN


    ( print('Running simulation...\n') if run_mode == 'serial' else [] )
    # for t in tqdm.tqdm(range(sim_parameters.partner_burn_in[0], sim_parameters.partner_burn_in[0] + sim_parameters.simulation_length[0])):
    for t in range(sim_parameters.partner_burn_in[0], sim_parameters.partner_burn_in[0] + sim_parameters.simulation_length[0]):


        # Update population
        meta, partner_matrix, partner_expire = demo.update_population(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


        # Update partnerships
        meta, partner_matrix, partner_expire = prt.update_partnerships(meta, partner_matrix, partner_expire, t)


        # Update infections
        meta = ng.update_infections(inf_parameters, meta, partner_matrix, t)


        # Dump simulation output
        meta.to_feather(out_dir + '/timestep' + str(t) + '.ftr')


    ( print('\n\nSimulation complete!\n') if run_mode == 'serial' else [] )


    #% SAVE OUTPUT


    # Shelve variables
    ( print('Shelving environment variables.\n') if run_mode == 'serial' else [] )
    my_shelf = shelve.open(out_dir + '_workspace.out', 'n')
    for key in dir():
        try:
            my_shelf[key] = globals()[key]
        except:
            #
            # __builtins__, my_shelf, and imported modules can not be shelved.
            #
            ( print('ERROR shelving: {0}'.format(key)) if run_mode == 'serial' else [] )
    my_shelf.close()
    ( print('\nComplete!\n\n\n\n') if run_mode == 'serial' else [] )

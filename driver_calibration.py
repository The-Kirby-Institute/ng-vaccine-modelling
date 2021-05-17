# -*- coding: utf-8 -*-
"""
Created on Thu May 13 16:32:39 2021

@author: nicol
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


# Parallel processing
import multiprocessing
from time import sleep


# My modules
import src.demographic.generate_population as pop
import src.demographic.population_dynamics as demo
import src.partners.partners as prt
import src.calibration.setup as calibrate
import src.infections.ng as ng


#%% RUN


# Identify the total number of parameter sets to run
sim_parameters = pd.read_csv('data/param.csv')


# calibrate.run_one_simulation(1, 0)


# Run them all in serial
for i in range(0, sim_parameters['n_parameter_sets'][0]):
    calibrate.run_one_parameter_set(i)
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
from multiprocessing import Pool


# My modules
import src.demographic.generate_population as pop
import src.demographic.population_dynamics as demo
import src.partners.partners as prt
import src.calibration.setup as calibrate
import src.infections.ng as ng


#%% RUN in serial


#for i in range(0, sim_parameters['n_parameter_sets'][0]):
#    calibrate.run_one_parameter_set(i)


#%% RUN in parallel


# Identify the total number of parameter sets to run
sim_parameters = pd.read_csv('data/param.csv')
sim_parameters = list(range(0, sim_parameters['n_parameter_sets'][0]))


# Define function for running the code
def worker(it):
    calibrate.run_one_parameter_set(it)


# Define function for handling the parallel pool
def pool_handler():
    p = Pool(12)
    p.map(worker, sim_parameters)


if __name__ == '__main__':
    pool_handler()



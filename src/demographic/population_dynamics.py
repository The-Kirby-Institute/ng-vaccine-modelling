# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 09:57:13 2021

@author: nicol
@profile
"""


#%% Setup Libraries


# Load libraries
import numpy as np
import pandas as pd
import copy


# My modules
import src.demographic.generate_population as pop
import src.partners.partners as prt
import src.infections.ng as ng


# Parse general simulation parameters
sim_parameters = pd.read_csv('data/param.csv')


#%% FUN update_population()
#
#
# Function to implement all of the population dynamics
#
#
def update_population(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t):


    # Mobility dynamics
    meta, partner_matrix, partner_expire = mobility(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


    # Make people older by a day
    meta.loc[:, 'age'] = meta.loc[:, 'age'] + (1/365)
    meta.loc[:, 'age_group'] = np.floor((meta.age - 15)/5)


    # Update demographic indexing
    pop_parameters = update_demographic_compartments(pop_parameters, meta)


    return meta, partner_matrix, partner_expire


#%% FUN mobility()
#
#
# Implement an importation event.
#
# The imported case is infectious at one site and immediately joins a short
# term relationship at random.
#
#
def mobility(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t):


    # Make things a little easier
    imports = pop_parameters['imports']
    lookup = pop_parameters['lookup']


    # Iterate over all age and gender combinations
    array_in = []
    list_out = []
    for gender in [0, 1]:


        # Age groups
        for age_group in [0, 1, 2, 3, 4]:


            # Set target
            target = pop_parameters['target'][str(gender)]


            # Sample the number of new people to come in
            n_cohort = sum(lookup['GA' + str(gender) + str(age_group)])
            n_new = np.random.poisson(max(1, target[age_group] - n_cohort) * inf_parameters['infection']['pop_annual_turnover_rate'][0])


            # If this is the 16 y/o group, add in some more in
            if age_group == 0:
                n_debut = np.random.poisson(target[age_group]/(4*365))
            else:
                n_debut = 0


            # sample the people to add to the population
            temp = sample_from_imports(imports, age_group, gender, n_new + n_debut)


            # Change the age to 16 for some individuals
            if n_debut > 0:
                temp.loc[0:n_debut, 'age'] = 16


            # Concatinate with any other new people to come in
            if (len(temp) > 0) & (len(array_in) == 0):
                array_in = temp
            elif len(temp) > 0:
                array_in = array_in.append(temp).reset_index(drop = True)


            # Sample a list of people to leave
            n_out = np.random.poisson(max(1, n_cohort - target[age_group]) * inf_parameters['infection']['pop_annual_turnover_rate'][0])
            list_out = list_out + ([] if n_out == 0 else np.random.choice(meta.index[lookup['GA' + str(gender) + str(age_group)]], n_out).tolist())


            # Identify anybody over 36 to also leave
            list_out = list_out + list(meta.index[meta.age > 36])


    # Change some attributes of the imports
    if len(array_in) > 0:
        # Change infectious people to already be infectious upon entering the population
        infected = array_in.state == 'E'
        site0 = array_in.site0 == int(1)
        site1 = array_in.site1 == int(1)
        site2 = array_in.site2 == int(1)
        array_in.loc[infected, 'state'] = 'I'
        array_in.loc[(infected) & (site0), 'site0_t0'] = t
        array_in.loc[(infected) & (site1), 'site1_t0'] = t
        array_in.loc[(infected) & (site2), 'site2_t0'] = t
        array_in.loc[(infected) & (site0), 'site0_t1'] = t + ng.duration_rectal(inf_parameters, array_in.loc[(infected) & (site0), ])
        array_in.loc[(infected) & (site1), 'site1_t1'] = t + ng.duration_urethral(inf_parameters, array_in.loc[(infected) & (site1), ])
        array_in.loc[(infected) & (site2), 'site2_t1'] = t + ng.duration_pharyngeal(inf_parameters, array_in.loc[(infected) & (site2), ])
        array_in.loc[:, 'import_time'] = t


        # Update the meta-population data
        meta, partner_matrix, partner_expire = add_to_meta(meta, partner_matrix, partner_expire, array_in, t)


    # Take some people out if needed
    if len(list_out) > 0:


        # Update partner indicies in meta
        meta, partner_matrix, partner_expire = remove_from_meta(meta, partner_matrix, partner_expire, list_out)


    return meta, partner_matrix, partner_expire



#%% FUN initilise_importations()
#
#
# Pre-compute a bunch of people to use as imports later.
#
#
def initilise_demographic_dynamics(pop_parameters, inf_parameters, meta):


    # Preallocate
    n_gen = 10000
    t0 = -1
    imports = dict()


    # Generate list of people for future importations
    for i in [0, 1]:
        for j in [0, 1, 2, 3, 4]:
            imports.update({str(i) + str(j) : import_particular_age_group_and_gender(pop_parameters, inf_parameters, j, i, n_gen, t0)})


    # Save in pop_parameters
    pop_parameters.update({'imports': imports})


    # Run the demographic indexer
    pop_parameters = update_demographic_compartments(pop_parameters, meta)


    return pop_parameters


#%% FUN update_demographic_compartments()
#
#
#
#
#
def update_demographic_compartments(pop_parameters, meta):
    # Experimental: some way of cutting out the number of logicals being used


    # Identifier for all the base line age and sex cohorts
    lookup = {'G0': meta.gender == 0,
               'G1': meta.gender == 1,
               'A0': meta.age_group == 0,
               'A1': meta.age_group == 1,
               'A2': meta.age_group == 2,
               'A3': (meta.age_group == 3) & (meta.age < 35),
               'A4': meta.age >= 35}


    # Identifier for all the age and sex combinations
    lookup.update({'GA00': lookup['G0'] & lookup['A0'],
                    'GA01': lookup['G0'] & lookup['A1'],
                    'GA02': lookup['G0'] & lookup['A2'],
                    'GA03': lookup['G0'] & lookup['A3'],
                    'GA04': lookup['G0'] & lookup['A4'],
                    'GA10': lookup['G1'] & lookup['A0'],
                    'GA11': lookup['G1'] & lookup['A1'],
                    'GA12': lookup['G1'] & lookup['A2'],
                    'GA13': lookup['G1'] & lookup['A3'],
                    'GA14': lookup['G1'] & lookup['A4']})


    # Store in pop parameters
    pop_parameters.update({'lookup': lookup})


    return pop_parameters


#%% HELPER import_particular_age_group_and_gender()
#
#
# Helper for just importing people from one age group
#
#
def import_particular_age_group_and_gender(pop_parameters, inf_parameters, age_group, gender, n, t):


    # Set the desired age distribution
    temp = copy.deepcopy(pop_parameters)
    temp['age_dist'].loc[:, 'cdf'] = 0
    temp['age_dist'].loc[temp['age_dist'].age_upper == min(20 + 5*age_group, 36), 'cdf'] = 1


    # Set the desired gender distribution
    temp['sex_dist'].loc[:, 'pMale'] = gender


    # Generate new people for the population
    new = pop.generate_population(temp, n, inf_parameters['infection'].prob_import_infectious[0], 0)
    new.loc[:, 'import_time'] = t


    return new


#%% HELPER sample_from_imports()
#
#
# Select n individuals from imports dataset
#
#
def sample_from_imports(imports, age, gender, n_sample):


    # Select a few rows from the imports sample cohort at random
    cohort = str(gender) + str(age)
    temp = np.random.choice(imports[cohort].index, n_sample)
    temp = imports[cohort].loc[temp, :]
    temp = temp.reset_index(drop = True)


    return temp


#%% HELPER add_to_meta()
#
#
# Function which adds a new person into the meta dataframe and the
# associated matrices
#
#
def add_to_meta(meta, partner_matrix, partner_expire, new_person, t):


    # Put the new person into the meta-population
    meta = meta.append(new_person).reset_index(drop = True)
    pop_tot = len(meta)
    n_new = len(new_person)


    # Put the new person into the partner matrix
    # new_col = np.zeros((pop_tot-n_new, n_new))
    # new_row = np.zeros((n_new, pop_tot))
    # partner_matrix = np.hstack((partner_matrix, new_col))
    # partner_matrix = np.vstack((partner_matrix, new_row))
    partner_matrix = add_to_array(partner_matrix, pop_tot, 0)


    # Put the new person into the partner duration matrix
    # new_col = float('inf') * np.ones((pop_tot-n_new, n_new))
    # new_row = float('inf') * np.ones((n_new, pop_tot))
    # partner_expire = np.hstack((partner_expire, new_col))
    # partner_expire = np.vstack((partner_expire, new_row))
    partner_expire = add_to_array(partner_expire, pop_tot, float('inf'))


    # Test to see if they want a partner
    new_cases = new_person.index[new_person.state == 'I']
    for i in new_cases:
        ii = pop_tot - (n_new-(i+1)) - 1
        jj = prt.find_partner(meta, partner_matrix, ii)


        # Check somebody was found
        if jj != -1:


            # Sample a duration
            duration = prt.relationship_duration(meta, ii, jj, 1)


            # Update partnership array
            partner_matrix[ii, jj] = 1
            partner_matrix[jj, ii] = 1


            # Update partnership duration matrix
            partner_expire[ii, jj] = t + duration
            partner_expire[jj, ii] = t + duration


    return meta, partner_matrix, partner_expire


#%% HELPER remove_from_meta()
def remove_from_meta(meta, partner_matrix, partner_expire, leave):


    # Take them out of the population
    # partner_matrix = np.delete(partner_matrix, leave, 0)
    # partner_matrix = np.delete(partner_matrix, leave, 1)
    # partner_expire = np.delete(partner_expire, leave, 0)
    # partner_expire = np.delete(partner_expire, leave, 1)
    partner_matrix = delete_from_array(partner_matrix, leave, len(meta))
    partner_expire = delete_from_array(partner_expire, leave, len(meta))


    # Terminate long term relationships with these guys
    meta.loc[meta.partner.isin(leave), 'partner'] = -1


    # Take them out of meta
    meta = meta.drop(leave, 0).reset_index()


    # Isolate how the indicies have changed
    old_index = meta['index']
    new_index = meta.index


    # Adjust the partnership indicies in meta
    old_partners = meta.partner[meta.partner > -1]
    for ii in old_partners.index:
        meta.loc[ii, 'partner'] = new_index[old_index == old_partners[ii]]
    meta = meta.drop('index', axis = 1)


    return meta, partner_matrix, partner_expire


#%% HELPER delete_from_array()
#
#
# Helper function to delete a row and column from an array
#
#
def delete_from_array(a, leave, n):


    # Drop those entries
    # a = a[keep, :][:, keep]


    # Shuffle unwanted rows and columns to the end of the array but don't delete them
    keep = list(set(range(0, n)) - set(leave))
    permutation = np.array(keep + leave)
    a = a[permutation, :][:, permutation]


    return a


def add_to_array(a, tot_needed, values):


    # Check first that there isn't already an empty row and column lying around
    to_add = tot_needed - len(a)


    # If more rows are needed then do a vstack/hstack
    if to_add > 0:


        # Put the new person into the partner matrix
        new_rows = values * np.ones((to_add, len(a)))
        new_cols = values * np.ones((tot_needed, to_add))

        a = np.vstack((a, new_rows))
        a = np.hstack((a, new_cols))


    return a









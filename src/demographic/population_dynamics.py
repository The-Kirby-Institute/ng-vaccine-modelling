#%% Setup Libraries


# Load libraries
import numpy as np
import pandas as pd
import random


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


    # Test to see if you should import a case
    meta, partner_matrix, partner_expire = imported_case(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


    # Test to see if you should import one or more 16 year old
    meta, partner_matrix, partner_expire = sexual_debut(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t)


    # Test to see if you should take somebody aged 20 or older out
    meta, partner_matrix, partner_expire = leave_population(pop_parameters, meta, partner_matrix, partner_expire)


    # Take peop-le out when they exceed 36
    meta, partner_matrix, partner_expire = too_old(pop_parameters, meta, partner_matrix, partner_expire)


    # Make people older by a day
    meta.loc[:, 'age'] = meta.loc[:, 'age'] + (1/365)
    meta.loc[meta.age < 20, 'age_group'] = 0
    meta.loc[(meta.age >= 20) & (meta.age < 25), 'age_group'] = 1
    meta.loc[(meta.age >= 25) & (meta.age < 30), 'age_group'] = 2
    meta.loc[meta.age >= 30, 'age_group'] = 3


    return meta, partner_matrix, partner_expire


#%% FUN sexual_debut()
#
#
# Bring new 16 year olds into the population
#
#
def sexual_debut(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t):


    # Simulate the number of new people to bring in
    prop_female = pop_parameters['age_dist'].cdf.iloc[0] * (1 - pop_parameters['sex_dist'].pMale)
    prop_male = pop_parameters['age_dist'].cdf.iloc[5] * pop_parameters['sex_dist'].pMale
    debut_rate = pop_parameters['n'] * (prop_female + prop_male) / (4*365)
    n_debut = np.random.poisson(debut_rate)
    n_debut = int(n_debut[0])


    # Bring some people in if needed
    if n_debut > 0:


        # Generate new people for the population
        debut = pop.generate_population(pop_parameters, n_debut, 0)


        # Give them an age of 16
        debut.loc[:, 'age'] = sim_parameters['age_lower_bound'][0]
        debut.loc[:, 'age_group'] = 1


        # Put the new people into the meta-population
        meta = meta.append(debut).reset_index(drop = True)
        n_pop = len(meta)


        # Put the new people into the partner matrix
        new_col = np.zeros((n_pop-n_debut, n_debut))
        new_row = np.zeros((n_debut, n_pop))
        partner_matrix = np.hstack((partner_matrix, new_col))
        partner_matrix = np.vstack((partner_matrix, new_row))


        # Put the new person into the partner duration matrix
        new_col = float('inf') * np.ones((n_pop-n_debut, n_debut))
        new_row = float('inf') * np.ones((n_debut, n_pop))
        partner_expire = np.hstack((partner_expire, new_col))
        partner_expire = np.vstack((partner_expire, new_row))


    return meta, partner_matrix, partner_expire


#%% FUN leave_population()
#
#
# Somebody leaves the population
#
#
def leave_population(pop_parameters, meta, partner_matrix, partner_expire):


    # Compute target population for each age group
    age_dist = pop_parameters['age_dist']
    pMale = pop_parameters['sex_dist']['pMale'].iloc[0]
    n = pop_parameters['n']
    target = ( age_dist.ave[age_dist.sex == 0].reset_index(drop=True) * (1-pMale) + \
               age_dist.ave[age_dist.sex == 1].reset_index(drop=True) * pMale ) * n
    target = np.floor(target)


    # Sample the leaving rate from the 20-24 age group
    n_leave = np.random.poisson( max(0, sum(meta.age_group==1) - max(target[1:4])))
    leave_1 = ([] if n_leave == 0 else np.random.choice(meta.index[meta.age_group == 1], n_leave).tolist())


    # Sample the leaving rate from the 25-29 age group
    n_leave = np.random.poisson( max(0, sum(meta.age_group==2) - max(target[2:4])))
    leave_2 = ([] if n_leave == 0 else np.random.choice(meta.index[meta.age_group == 2], n_leave).tolist())


    # Sample the leaving rate from the 30-34 age group
    n_leave = np.random.poisson( max(0, sum((meta.age > 30) & (meta.age < 35)) - max(target[3:4])))
    leave_3 = ([] if n_leave == 0 else np.random.choice(meta.index[(meta.age > 30) & (meta.age < 35)], n_leave).tolist())


    # Sample the leaving rate from the 35 age group
    n_leave = np.random.poisson( max(0, sum(meta.age > 35) - target[4]))
    leave_4 = ([] if n_leave == 0 else np.random.choice(meta.index[meta.age > 35], n_leave).tolist())


    # Combine everyone
    leave = leave_1 + leave_2 + leave_3 + leave_4


    # Take some people out if needed
    if len(leave) > 0:


        # Terminate long term relationships with these guys
        meta.loc[meta.partner.isin(leave), 'partner'] = -1


        # Take them out of the population
        meta = meta.drop(leave, 0).reset_index(drop = True)
        partner_matrix = np.delete(partner_matrix, leave, 0)
        partner_matrix = np.delete(partner_matrix, leave, 1)
        partner_expire = np.delete(partner_expire, leave, 0)
        partner_expire = np.delete(partner_expire, leave, 1)


    return meta, partner_matrix, partner_expire


#%% FUN too_old()
#
#
# Somebody leaves the population
#
#
def too_old(pop_parameters, meta, partner_matrix, partner_expire):


    # People leave when they are older than 36
    leave = meta.index[meta.age >= 36]


    # Take some people out if needed
    if len(leave) > 0:


        # Terminate long term relationships with these guys
        meta.loc[meta.partner.isin(leave), 'partner'] = -1


        # Take them out of the population
        meta = meta.drop(leave, 0).reset_index(drop = True)
        partner_matrix = np.delete(partner_matrix, leave, 0)
        partner_matrix = np.delete(partner_matrix, leave, 1)
        partner_expire = np.delete(partner_expire, leave, 0)
        partner_expire = np.delete(partner_expire, leave, 1)


    return meta, partner_matrix, partner_expire


#%% FUN imported_case()
#
#
# Implement an importation event.
#
# The imported case is infectious at one site and immediately joins a short
# term relationship at random.
#
#
def imported_case(pop_parameters, inf_parameters, meta, partner_matrix, partner_expire, t):


    # Check to see if somebody new is imported
    u = np.random.random(1)
    if u < inf_parameters['infection'].import_prob[0]:


        # Generate a new individual for the population
        new_person = pop.generate_population(pop_parameters, 1, 1)


        # Give them an infection at at one anatomical site
        site = random.randint(0, 2)
        new_person.loc[0, 'site' + str(site)] = int(1)
        new_person.loc[0, 'site' + str(site) +'_t0'] = t
        new_person.loc[0, 'state'] = 'I'


        # Work out the duration of infection
        if site == 0:
            new_person.loc[0, 'site0_t1'] = t + ng.duration_rectal(inf_parameters, new_person)
        elif site == 1:
            new_person.loc[0, 'site1_t1'] = t + ng.duration_urethral(inf_parameters, new_person)
        else:
            new_person.loc[0, 'site2_t1'] = t + ng.duration_pharyngeal(inf_parameters, new_person)


        # Put the new person into the meta-population
        meta = meta.append(new_person).reset_index(drop = True)
        new_person = len(meta)


        # Put the new person into the partner matrix
        new_col = np.zeros((new_person-1, 1))
        new_row = np.zeros((1, new_person))
        partner_matrix = np.hstack((partner_matrix, new_col))
        partner_matrix = np.vstack((partner_matrix, new_row))


        # Put the new person into the partner duration matrix
        new_col = float('inf') * np.ones((new_person-1, 1))
        new_row = float('inf') * np.ones((1, new_person))
        partner_expire = np.hstack((partner_expire, new_col))
        partner_expire = np.vstack((partner_expire, new_row))


        # Select a partner for the new person
        new_partner = prt.find_partner(meta, partner_matrix, new_person-1)


        # Check somebody was found
        if new_partner != -1:


            # Sample a duration
            duration = prt.relationship_duration(meta, new_person, new_partner, 1)


            # Update partnership array
            partner_matrix[new_person-1, new_partner] = 1
            partner_matrix[new_partner, new_person-1] = 1


            # Update partnership duration matrix
            partner_expire[new_person-1, new_partner] = t + duration
            partner_expire[new_partner, new_person-1] = t + duration


    return meta, partner_matrix, partner_expire
# -*- coding: utf-8 -*-
"""
CODE FOR DOING ALL OF THE INFECTION STUFF

Created on Thu Nov 12 13:00:07 2020

@author: nicol
"""


#%% Setup Libraries
import numpy as np
import pandas as pd
import scipy.stats as sp


#%% FUN update_infections()
#
#
# Function to update the state of infections
#
#
def update_infections(inf_parameters, meta, partner_matrix, t):


    # Implement a transmission event
    meta = new_infections(inf_parameters, meta, partner_matrix, t)


    # Update infectious states
    meta = progress_state_of_infection(meta, t)


    # Implement treatment
    meta = seek_treatment(inf_parameters, meta, partner_matrix, t)


    return meta


#%% FUN duration_rectal()
##  FUNCTION FOR DURATION OF RECTAL INFECTIONS
#
#
# Latent period
#    constant
#
# Duration of rectal infection
#    Infections can be symptomatic or asymptomatic.
#    Duration is drawn from a Gamma distribution with specified mean and var
#
# Duration of urethral infection
#    Infections can be symptomatic or asymptomatic
#    The probability of a symptomatic infection depends on gender
#    Duration is drawn from a Gamma distribution with specified mean and var
#    Mean and var is the same for both genders
#
# Duration of pharyngeal infection
#    All infections assumed to be asymptomatic
#
#
# INPUT
#    infectee = meta.loc[infectee] - used in some functions for convenience
#
#    mean_rectal
#    var_rectal
#    symptomatic_rectal
#
#    mean_urethral
#    var_urethral
#    symptomatic_urethral - 1x2 list, columns correspond to gender
#
#    mean_phar
#    var_rectal
#
#
# OUTPUT
#    duration
#
#
def duration_rectal(inf_parameters, infectee):


    # Simulate duration of natural infection
    duration = np.random.gamma(inf_parameters['infection'].mean_rectal[infectee.gender] / \
                               inf_parameters['infection'].var_rectal[infectee.gender], \
                               inf_parameters['infection'].var_rectal[infectee.gender],
                               len(infectee))


    # Return duration
    return duration


#%% FUN duration_urethral()
def duration_urethral(inf_parameters, infectee):


    # Simulate duration of natural infection
    duration = np.random.gamma(inf_parameters['infection'].mean_urethral[infectee.gender] / \
                               inf_parameters['infection'].var_urethral[infectee.gender], \
                               inf_parameters['infection'].var_urethral[infectee.gender],
                               len(infectee))


    # Return duration
    return duration


#%% FUN duration_pharyngeal()
def duration_pharyngeal(inf_parameters, infectee):


    # Simulate duration of natural infection
    duration = np.random.gamma(inf_parameters['infection'].mean_pharyngeal[infectee.gender] / \
                               inf_parameters['infection'].var_pharyngeal[infectee.gender], \
                               inf_parameters['infection'].var_pharyngeal[infectee.gender],
                               len(infectee))

    # Return duration
    return duration


#%% FUN duration_treatment_immunity()
def duration_treatment_immunity(parameters, treat):


    # All treatment results results in a Gamma distributed immune period
    duration = np.random.gamma(parameters['infection'].immunity_mean[0]/ \
                               parameters['infection'].immunity_var[0], \
                               parameters['infection'].immunity_var[0], len(treat))


    # Return duration
    return duration


#%% FUN latent_period()
def latent_period(inf_parameters, infectee):


    # Just using a constant latent period for now
    out = inf_parameters['infection'].latent_period[infectee.gender]
    out = np.repeat(out, len(infectee))


    return out


#%% FUN transmission_probability()
#
#
# Compute the site-specific transmission probabilities
#
#
def transmission_probability(inf_parameters, vax_parameters, meta, i, j):


    # Pull out some indicies for convenience
    g0 = int(meta.at[i, "gender"])
    g1 = int(meta.at[j, "gender"])
    risk = 1 + meta.at[i, "risk"] + meta.at[j, "risk"]


    # Compose the transition probability matrix
    trans_prob = \
        float(np.random.random(1) < risk * inf_parameters['p_anal'][g0, g1]) * inf_parameters['trans_anal'] + \
        float(np.random.random(1) < risk * inf_parameters['p_oral'][g0, g1]) * inf_parameters['trans_oral'] + \
        float(np.random.random(1) < risk * inf_parameters['p_kiss'][g0, g1]) * inf_parameters['trans_kiss'] + \
        float(np.random.random(1) < risk * inf_parameters['p_rim'][g0, g1]) * inf_parameters['trans_rim'] + \
        float(np.random.random(1) < risk * inf_parameters['p_sex'][g0, g1]) * inf_parameters['trans_sex']


    return trans_prob


#%% FUN symptoms_rectal()
#
#
def symptoms_rectal(inf_parameters,
                    vax_parameters,
                    meta, i, j):
    prob = np.random.random() < inf_parameters['infection'].symptoms_rectal[meta.gender.iloc[j]]
    return prob


#%% FUN symptoms_pharynx()
#
#
def symptoms_pharynx(inf_parameters,
                     vax_parameters,
                     meta, i, j):
    prob = np.random.random() < inf_parameters['infection'].symptoms_pharyngeal[meta.gender.iloc[j]]
    return prob


#%% FUN symptoms_urethra()
#
#
def symptoms_urethra(inf_parameters,
                     vax_parameters,
                     meta, i, j):
    prob = np.random.random() < inf_parameters['infection'].symptoms_urethral[meta.gender.iloc[j]]
    return prob


#%% VAR symptoms_baseline
#
#
symptoms_baseline = {'site0': symptoms_rectal,
                     'site1': symptoms_pharynx,
                     'site2': symptoms_urethra}


#%% VAR duration_baseline
#
#
def duration_baseline_site0(vax_parameters, meta, j): return 1
def duration_baseline_site1(vax_parameters, meta, j): return 1
def duration_baseline_site2(vax_parameters, meta, j): return 1
duration_baseline = {'site0': duration_baseline_site0,
                     'site1': duration_baseline_site1,
                     'site2': duration_baseline_site2}


#%% FUN new_infections()
# LOOK AT ALL PARTNERSHIPS AND SEED NEW INFECTIONS
#
#
# Uses matrices for describing the probability of engaging in certain acts as
# a function of gender. In particular, p_anal, p_oral, p_kiss, p_rim, and p_sex.
# In all cases, read entry (i, j) as the probability that an individual of
# sex i (0=F, 1=M) engaging in that particular act with an individual of sex j.
#
#

#
#
# Decision tree:
#
#    1. Find all individuals in the population who have at least 1 partner
#        and are infections.
#
#    2. For a given person i, look at all their partners j and check that:
#        a. Individual j is not immune
#        b. Individual j is not infected at all 3 sites
#
#    3. Given an infectious individual i and a potentially infectable partner j
#        use the act-specific probabilities to determine whether or not a
#        particular sexual act takes place.
#
#    4. Given a range of sexual acts, use the site-specific probabilities to
#        determine which sites are to be infected.
#
#    5. Seed those sites with an infection. They will not become infectious
#        until the latent period is over.
#
#
# INPUT
#   meta, partner_matrix, t
#   p_anal, The probability of a given sexual act (Act-specific probabilities)
#   p_oral,
#   p_kiss,
#   p_rim,
#   p_sex,
#   trans_anal, The probability of a site-to-site transmission (Site-specific probabilities)
#   trans_oral,
#   trans_kiss,
#   trans_rim,
#   trans_sex
#
# OUTPUT
#   meta
#
#
def new_infections(inf_parameters, meta, partner_matrix, t,
                   susceptible_states = ['S', 'E', 'I'],
                   trans_prob_fun = transmission_probability,
                   vax_parameters = [],
                   symptoms_prob = symptoms_baseline,
                   duration_mod = duration_baseline):


    # Determine whether or not any new infections could possibly occur
    infectors = meta[(meta["state"] == "I") & (np.sum(partner_matrix, axis = 1) > 0)]


    # Iterate over all infectors
    for i in infectors.index:


        # Extract all partners of the infector
        partners = np.asarray(np.where(partner_matrix[i,:] == 1))


        # Remove partners who are either immune or already infected at all sites
        partner_susceptible = meta.loc[partners[0,:], 'state'].isin(susceptible_states)
        partner_site = (meta.loc[partners[0,:], "site0"] == 1) & \
                       (meta.loc[partners[0,:], "site1"] == 1) & \
                       (meta.loc[partners[0,:], "site2"] == 1)
        partners = partners[0, partner_susceptible & (~partner_site)]


        # Iterate over all partnerships with potential for transmission
        for j in partners:


            # Pull out some indices for convenience
            trans_prob = trans_prob_fun(inf_parameters, vax_parameters, meta, i, j)


            # Determine if any transmissions have occured this iteration
            sites = np.array(meta.loc[i, ["site0", "site1", "site2"]])
            M = sites * np.transpose(trans_prob)
            U = np.random.random((3, 3))
            N = np.sum(U < M, axis=1) > 0
            print(M, U, N)
            new_inf = np.flatnonzero(N)


            # Make sure any new infections don't overlap with current infections
            infectee = meta.loc[j,:]
            sites = infectee[["site0", "site1", "site2"]] == 1
            exposures = infectee[["site0_t0", "site1_t0", "site2_t0"]] < float("inf")
            old_inf = np.where(sites.to_numpy() | exposures.to_numpy())
            new_inf = new_inf[~np.isin(new_inf, old_inf)]


            # Seed new infections
            if len(new_inf) > 0:


                # Update state of infectee
                meta.at[j, 'state'] = ('E' if infectee.state == 'S' else infectee.state)


                # Set infection parameters for the new cases
                for k in new_inf:


                    # Set duration of latent period (assumed to be the same for all sites)
                    end_latent = t + latent_period(inf_parameters, infectee)
                    meta.at[j, "site" + str(int(k)) + "_t0"] = end_latent


                    # Set site-specific infection parameters
                    if k == 0:

                        # Infection at rectum
                        meta.at[j, "site0_t1"] = end_latent + duration_mod['site0'](vax_parameters, meta, j) * duration_rectal(inf_parameters, infectee)
                        meta.at[j, 'site0_symptoms'] = symptoms_prob['site0'](inf_parameters, vax_parameters, meta, i, j)
                    elif k == 1:

                        # Infection at pharynx
                        meta.at[j, "site1_t1"] = end_latent + duration_mod['site1'](vax_parameters, meta, j) * duration_urethral(inf_parameters, infectee)
                        meta.at[j, 'site1_symptoms'] = symptoms_prob['site1'](inf_parameters, vax_parameters, meta, i, j)
                    else:

                        # Infection at urethra
                        meta.at[j, "site2_t1"] = end_latent + duration_mod['site2'](vax_parameters, meta, j) * duration_pharyngeal(inf_parameters, infectee)
                        meta.at[j, 'site2_symptoms'] = symptoms_prob['site2'](inf_parameters, vax_parameters, meta, i, j)


    # Return meta
    return meta


#%% FUN progress_state_of_infection()
# PROGRESS THE STATE OF INFECTION
#
#
# Simply checks the duration of each compartment and progresses the
# individual if the duration is up.
#
#
# INPUT
#   meta, t
#
# OUTPUT
#   meta
#
#
def progress_state_of_infection(meta, t):


    # Test for new rectal infections
    infectious = (meta["site0_t0"] < t) & (meta["site0"] == 0)
    meta.loc[infectious, "state"] = "I"
    meta.loc[infectious, "site0"] = 1


    # Test for new urethral infections
    infectious = (meta["site1_t0"] < t) & (meta["site1"] == 0)
    meta.loc[infectious, "state"] = "I"
    meta.loc[infectious, "site1"] = 1


    # Test for new pharyngeal infections
    infectious = (meta["site2_t0"] < t) & (meta["site2"] == 0)
    meta.loc[infectious, "state"] = "I"
    meta.loc[infectious, "site2"] = 1


    # Remove expired rectal infections
    recovery0 = meta["site0_t1"] <= t
    meta.at[recovery0, "site0"] = 0
    meta.at[recovery0, "site0_t0"] = float("inf")
    meta.at[recovery0, "site0_t1"] = float("inf")
    meta.at[recovery0, 'site0_symptoms'] = False


    # Remove expired urethral infections
    recovery1 = meta["site1_t1"] <= t
    meta.at[recovery1, "site1"] = 0
    meta.at[recovery1, "site1_t0"] = float("inf")
    meta.at[recovery1, "site1_t1"] = float("inf")
    meta.at[recovery1, 'site1_symptoms'] = False


    # Remove expired pharengynal infections
    recovery2 = meta["site2_t1"] <= t
    meta.at[recovery2, "site2"] = 0
    meta.at[recovery2, "site2_t0"] = float("inf")
    meta.at[recovery2, "site2_t1"] = float("inf")
    meta.at[recovery2, 'site2_symptoms'] = False


    # Check if anybody has achieved a natural recovery
    natural_recovery = ((recovery0 | recovery1) | recovery2) & (meta.site0==0) & (meta.site1==0) & (meta.site2==0)
    meta.at[natural_recovery, 'state'] = 'S'


    # Remove treatment-conferred immunity
    waned_immunity = meta["recovery_time"] < t
    meta.loc[waned_immunity, "state"] = "S"
    meta.loc[waned_immunity, "recovery_time"] = float("inf")


    return meta


#%% FUN seek_treatment()
# FUNCTION FOR TIME UNTIL TREATMENT
#
#
# Time until treatment
#    Gamma distributed with specified mean and variance.
#    Upon treatment, the indivdual's parter will also be treated.
#    Immunity is conferred for a specied period.
#
#
# INPUT
#    meta, t
#
#    Parameters of the distribution of time until an individual seeks treatment
#    treat_mean
#    treat_var
#
#    Parameters of the distribution of time for which an individual is immune
#    immune_mean
#    immune_var
#
#
# OUTPUT
#    meta
#
#
def seek_treatment(parameters, meta, partner_matrix, t):


    # Work out who is symptomatic
    symp0 = meta.site0_symptoms == True
    symp1 = meta.site1_symptoms == True
    symp2 = meta.site2_symptoms == True


    # Work out their duration of infectiousness
    dur0 = t - meta.loc[symp0, "site0_t0"]
    dur1 = t - meta.loc[symp1, "site1_t0"]
    dur2 = t - meta.loc[symp2, "site2_t0"]


    # Work out whose infectious period has exceeded their tolerance
    treat0 = sp.gamma.cdf(dur0, parameters['infection'].treatment_mean[0]/parameters['infection'].treatment_var[0], parameters['infection'].treatment_var[0]) >= meta.loc[symp0, "treatment_threshold"]
    treat1 = sp.gamma.cdf(dur1, parameters['infection'].treatment_mean[0]/parameters['infection'].treatment_var[0], parameters['infection'].treatment_var[0]) >= meta.loc[symp1, "treatment_threshold"]
    treat2 = sp.gamma.cdf(dur2, parameters['infection'].treatment_mean[0]/parameters['infection'].treatment_var[0], parameters['infection'].treatment_var[0]) >= meta.loc[symp2, "treatment_threshold"]


    # Pull out their identifiers
    treat0 = treat0.index[treat0]
    treat1 = treat1.index[treat1]
    treat2 = treat2.index[treat2]


    # Combine these into one big list
    treat = np.append(treat0, treat1)
    treat = np.append(treat, treat2)
    treat = np.unique(treat)


    # Have their current long-term partners get treated as well
    # part = np.asarray(np.where(partner_matrix[treat,:] == 1))
    part = meta.partner.iloc[treat]
    treat = np.append(treat, part[part>-1])


    # Make amendments to meta
    meta.loc[treat, "state"] = "T"
    meta.loc[treat, "recovery_time"] = t + duration_treatment_immunity(parameters, treat)
    meta.loc[treat, "site0"] = 0
    meta.loc[treat, "site1"] = 0
    meta.loc[treat, "site2"] = 0
    meta.loc[treat, "site0_t0"] = float("inf")
    meta.loc[treat, "site1_t0"] = float("inf")
    meta.loc[treat, "site2_t0"] = float("inf")
    meta.loc[treat, "site0_t1"] = float("inf")
    meta.loc[treat, "site1_t1"] = float("inf")
    meta.loc[treat, "site2_t1"] = float("inf")
    meta.loc[treat, 'site0_symptoms'] = False
    meta.loc[treat, 'site1_symptoms'] = False
    meta.loc[treat, 'site2_symptoms'] = False



    # Return duration
    return meta



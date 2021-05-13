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


    # Test for symptomatic of asymptomatic infection
    is_symptomatic = np.random.random() < inf_parameters['infection'].symptoms_rectal[infectee.gender]
    if is_symptomatic.all():


        # Symptomatic
        duration = np.random.gamma(inf_parameters['infection'].mean_rectal[infectee.gender] / \
                                   inf_parameters['infection'].var_rectal[infectee.gender], \
                                   inf_parameters['infection'].var_rectal[infectee.gender])


    else:


        # Asymptomatic
        duration = float("inf")


    # Return duration
    return duration


#%% FUN duration_urethral()
def duration_urethral(inf_parameters, infectee):


    # Test for symptomatic of asymptomatic infection
    ii = int(infectee.gender)
    is_symptomatic = np.random.random() < inf_parameters['infection'].symptoms_urethral.iloc[ii]
    if is_symptomatic.all():


        # Symptomatic
        duration = np.random.gamma(inf_parameters['infection'].mean_urethral[ii] / \
                                   inf_parameters['infection'].var_urethral[ii], \
                                   inf_parameters['infection'].var_urethral[ii])


    else:


        # Asymptomatic
        duration = float("inf")


    # Return duration
    return duration


#%% FUN duration_pharyngeal()
def duration_pharyngeal(inf_parameters, infectee):


    # Test for symptomatic or asymptomatic infection
    is_symptomatic = np.random.random() < inf_parameters['infection'].symptoms_pharyngeal[infectee.gender]
    if is_symptomatic.any():


        # Symptomatic
        duration = np.random.gamma(inf_parameters['infection'].mean_pharyngeal[infectee.gender] / \
                                   inf_parameters['infection'].var_pharyngeal[infectee.gender], \
                                   inf_parameters['infection'].var_pharyngeal[infectee.gender])


    else:


        # Asymptomatic
        duration = float("inf")


    # Return duration
    return duration


#%% FUN latent_period()
def latent_period(inf_parameters, infectee):


    # Just using a constant latent period for now
    out = inf_parameters['infection'].latent_period[infectee.gender]


    return out


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
def new_infections(inf_parameters, meta, partner_matrix, t):


    # Determine whether or not any new infections could possibly occur
    infectors = meta[(meta["state"] == "I") & (np.sum(partner_matrix, axis = 1) > 0)]


    # Iterate over all infectors
    for i in infectors.index:


        # Extract all partners of the infector
        partners = np.asarray(np.where(partner_matrix[i,:] == 1))


        # Remove partners who are either immune or already infected at all sites
        partner_susceptible = meta.loc[partners[0,:], "state"] != "R"
        partner_site = (meta.loc[partners[0,:], "site0"] == 1) & \
                       (meta.loc[partners[0,:], "site1"] == 1) & \
                       (meta.loc[partners[0,:], "site2"] == 1)
        partners = partners[0, partner_susceptible & (~partner_site)]


        # Iterate over all partnerships with potential for transmission
        for j in partners:


            # Pull out some indices for convenience
            infectee = meta.loc[j]
            g0 = int(meta.at[i, "gender"])
            g1 = int(infectee["gender"])
            risk = 1 + meta.at[i, "risk"] + infectee["risk"]


            # Compose the transition probability matrix
            trans_prob = \
                float(np.random.random(1) < risk * inf_parameters['p_anal'][g0, g1]) * inf_parameters['trans_anal'] + \
                float(np.random.random(1) < risk * inf_parameters['p_oral'][g0, g1]) * inf_parameters['trans_oral'] + \
                float(np.random.random(1) < risk * inf_parameters['p_kiss'][g0, g1]) * inf_parameters['trans_kiss'] + \
                float(np.random.random(1) < risk * inf_parameters['p_rim'][g0, g1]) * inf_parameters['trans_rim'] + \
                float(np.random.random(1) < risk * inf_parameters['p_sex'][g0, g1]) * inf_parameters['trans_sex']


            # Determine if any transmissions have occured this iteration
            sites = np.array(meta.loc[i, ["site0", "site1", "site2"]])
            new_inf = np.flatnonzero(np.sum(np.random.random((3, 3)) < sites * np.transpose(trans_prob), axis=1) > 0)


            # Make sure any new infections don't overlap with current infections
            sites = infectee[["site0", "site1", "site2"]] == 1
            exposures = infectee[["site0_t0", "site1_t0", "site2_t0"]] < float("inf")
            old_inf = np.where(sites.to_numpy() | exposures.to_numpy())
            new_inf = new_inf[~np.isin(new_inf, old_inf)]


            # Seed new infections
            if len(new_inf) > 0:


                # Update state of infectee
                if infectee["state"] == "S":
                    meta.at[j, "state"] = "E"


                # Set durations of infection
                for k in new_inf:


                    # Set duration of latent period
                    meta.at[j, "site" + str(int(k)) + "_t0"] = t + latent_period(inf_parameters, infectee)


                    # Set site-specific duration of infection
                    if k == 0:
                        meta.at[j, "site0_t1"] = t + duration_rectal(inf_parameters, infectee)
                    elif k == 1:
                        meta.at[j, "site1_t1"] = t + duration_urethral(inf_parameters, infectee)
                    else:
                        meta.at[j, "site2_t1"] = t + duration_pharyngeal(inf_parameters, infectee)


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
    recovery = meta["site0_t1"] <= t
    meta.at[recovery, "site0"] = 0
    meta.at[recovery, "site0_t0"] = float("inf")
    meta.at[recovery, "site0_t1"] = float("inf")


    # Remove expired urethral infections
    recovery = meta["site1_t1"] <= t
    meta.at[recovery, "site1"] = 0
    meta.at[recovery, "site1_t0"] = float("inf")
    meta.at[recovery, "site1_t1"] = float("inf")


    # Remove expired pharengynal infections
    recovery = meta["site2_t1"] <= t
    meta.at[recovery, "site2"] = 0
    meta.at[recovery, "site2_t0"] = float("inf")
    meta.at[recovery, "site2_t1"] = float("inf")


    # Make sure that everybody labelled I is still I
    # Otherwise, move them to S
    removal = (meta["site0"]==0) & (meta["site1"]==0) & (meta["site2"]==0) & (meta["state"]!="R")
    meta.at[removal, "state"] = "S"


    # Remove immunity
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
    symp0 = np.isfinite(meta["site0_t0"]) & np.isfinite(meta["site0_t1"])
    symp1 = np.isfinite(meta["site1_t0"]) & np.isfinite(meta["site1_t1"])
    symp2 = np.isfinite(meta["site2_t0"]) & np.isfinite(meta["site2_t1"])


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


    # Look up their current partners
    part = np.asarray(np.where(partner_matrix[treat,:] == 1))
    treat = np.append(treat, part[1,:]).tolist()


    # Make amendments to meta
    meta.loc[treat, "state"] = "R"
    meta.loc[treat, "recovery_time"] = t + np.random.gamma(parameters['infection'].immunity_mean[0]/parameters['infection'].immunity_var[0], parameters['infection'].immunity_var[0], len(treat))
    meta.loc[treat, "site0"] = 0
    meta.loc[treat, "site1"] = 0
    meta.loc[treat, "site2"] = 0
    meta.loc[treat, "site0_t0"] = float("inf")
    meta.loc[treat, "site1_t0"] = float("inf")
    meta.loc[treat, "site2_t0"] = float("inf")
    meta.loc[treat, "site0_t1"] = float("inf")
    meta.loc[treat, "site1_t1"] = float("inf")
    meta.loc[treat, "site2_t1"] = float("inf")


    # Return duration
    return meta



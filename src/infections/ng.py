# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 13:00:07 2020

Collection of functions for implementing infection dynamics in the remote
communities model.
"""


#%% IMPORT REQUIRED MODULES
import numpy as np


#%% SET REQUIRED VARIABLES


# Parameters for the duration of rectal infection
mean_rectal = 14 # 360
var_rectal = 35^2
symptomatic_rectal = 0.8


# parameters for the duration of urethral infection
mean_urethral = 7 # 185
var_urethral = 35^2
symptomatic_urethral = [0.45, 0.11] # [male, female]


#%%###########################################################################
##                   FUNCTIONS FOR INFECTION DURATION                       ##
##############################################################################
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
#    mean_rectal
#    var_rectal
#
#
# OUTPUT
#    duration
#
#


#########################
##  RECTAL INFECTIONS  ##
#########################
def duration_rectal(infectee):


    # Test for symptomatic of asymptomatic infection
    if np.random.random() < symptomatic_rectal:


        # Symptomatic
        duration = np.random.gamma(mean_rectal/var_rectal, var_rectal)


    else:


        # Asymptomatic
        duration = float("inf")


    # Return duration
    return duration


###########################
##  URETHRAL INFECTIONS  ##
###########################
def duration_urethral(infectee):


    # Test for symptomatic of asymptomatic infection
    if np.random.random() < symptomatic_urethral[int(infectee["gender"])]:


        # Symptomatic
        duration = np.random.gamma(mean_urethral/var_urethral, var_urethral)


    else:


        # Asymptomatic
        duration = float("inf")


    # Return duration
    return duration


#############################
##  PHARYNGEAL INFECTIONS  ##
#############################
def duration_pharyngeal(infectee):
    return float("inf")


#####################
##  LATENT PERIOD  ##
#####################
def latent_period():
    return 4


#%%###########################################################################
##                 FUNCTION FOR SEEDING NEW INFECTIONS                      ##
##############################################################################
# LOOK AT ALL PARTNERSHIPS AND SEED NEW INFECTIONS
#
#
# Decision tree:
#
#    1. Find all individuals in the population who have at least 1 partner
#        and are infections.
#
#    2. For a given person i, look at all their paartners j and check that:
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
def new_infections(meta, partner_matrix, t, p_anal, p_oral, p_kiss, p_rim, p_sex, trans_anal, trans_oral, trans_kiss, trans_rim, trans_sex):
    # Determine whether or not any new infections could possibly occur
    infectors = meta[(meta["state"] == "I") & (np.sum(partner_matrix, axis = 1) > 0)]


    # Iterate over all infectors
    for i in infectors.index:


        # Extract all partners of the infector
        partners = np.asarray(np.where(partner_matrix[i,:] == 1))


        # Remove partners who are either immune or already infected at all sites
        partner_state = meta.loc[partners[0,:], "state"] != "R"
        partner_site = (meta.loc[partners[0,:], "site0"] == 1) & \
                       (meta.loc[partners[0,:], "site1"] == 1) & \
                       (meta.loc[partners[0,:], "site2"] == 1)
        partners = partners[0, partner_state & (~partner_site)]


        # Iterate over all partnerships with potential for transmission
        for j in partners:


            # Pull out some indices for convenience
            infectee = meta.loc[j]
            g0 = int(meta.at[i, "gender"])
            g1 = int(infectee["gender"])
            risk = 1 + meta.at[i, "risk"] + infectee["risk"]


            # Compose the transition probability matrix
            trans_prob = \
                float(np.random.random(1) < risk * p_anal[g0, g1]) * trans_anal + \
                float(np.random.random(1) < risk * p_oral[g0, g1]) * trans_oral + \
                float(np.random.random(1) < risk * p_kiss[g0, g1]) * trans_kiss + \
                float(np.random.random(1) < risk * p_rim[g0, g1]) * trans_rim + \
                float(np.random.random(1) < risk * p_sex[g0, g1]) * trans_sex


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
                    meta.at[j, "site" + str(int(k)) + "_t0"] = t + latent_period()


                    # Set site-specific duration of infection
                    if k == 0:
                        meta.at[j, "site0_t1"] = t + duration_rectal(infectee)
                    elif k == 1:
                        meta.at[j, "site1_t1"] = t + duration_urethral(infectee)
                    else:
                        meta.at[j, "site2_t1"] = t + duration_pharyngeal(infectee)


    # Return meta
    return meta


#%%###########################################################################
##                   PROGRESS THE STATE OF INFECTION                        ##
##############################################################################
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
    # Ptherwise, move them to S
    removal = (meta["site0"]==0) & (meta["site1"]==0) & (meta["site2"]==0)
    meta.at[removal, "state"] = "S"


    # Remove immunity
    waned_immunity = meta["recovery_time"] < t
    meta.loc[waned_immunity, "state"] = "S"
    meta.loc[waned_immunity, "recovery_time"] = float("inf")


    return meta
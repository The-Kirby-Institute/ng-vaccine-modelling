# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 10:28:17 2020

@author: nicol
"""

#############
##  SETUP  ##
#############
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotnine as pn




##############################################################################
##                     FUNCTION FOR MAKING PARTNERSHIPS                     ##
##############################################################################
# FIND A SEXUAL PARTNER FOR PERSON i FROM THE POOL OF ELIGABLE SINGLES IN meta
#
#
# Decision tree is as follows:
#
#   1. Use the sexual orientation of the bachelor to narrow the population
#       down into the individuals who would they would be interested in
#       partnering with.
#
#   2. The population is put into three groups based on age:
#       16-19, 20-24 and 25-29.
#
#   3. Using data from the GOANNA study, the age-preferences of the bachelor
#       are identified based on their age group. This distribution is then
#       multiplied by the age group preferences of their gender.
#       ie.
#       P(partner age|bachelor age, bachelor gender) =
#           P(partner age|bachelor age) X P(partner age|bachelor gender)
#
#   4. A selection of partners is extracted from the pool of possible 
#       partners based on the age group distribution above.
#
#   5. A partner is then selected at random from that pool.       
#
#
# INPUT
#   meta = the population array
#   i = the index of the bachelor
#
# OUTPUT
#   j = the index of their new partner.
#
#   
def find_partner(meta, partner_matrix, bachelor_index):
    
    
    ##############################################################
    ##  DEFINE PROBABILITY MATRICES FOR AGE AND GENDER BIASING  ##
    ##############################################################
    
    
    # Probability matrix of age biasing of last sexual encounter
    # Data from Table 5-3 of the GOANNA study - characteristics of last sexual encounter
    # Read as: from (row) to (column)
    # State space: {<16, 16-19, 20-24, 25-29, >29}
    # Note that the <16 and >30 demographics are excluded as they aren't in the model
    # The rows only correspond to the 16-19, 20-24, 25-29 age groups
    bias_age = np.array(
            [[578, 130, 11],
            [127, 487, 61],
            [27, 243, 174]],
            dtype = "float")
    bias_age = bias_age/bias_age.sum(axis=1, keepdims = True)
    # bias_age = np.cumsum(bias_age, axis = 1)
    
    
    # Probability distribution of sex age bias for last sexual encounter
    # Data from Table 5-3 as above
    # State space {0 (male), 1 (female)}
    # Read as: from (row) to (column)
    bias_sex = np.array([[379, 313, 76],
                        [346, 546, 170]])
    bias_sex = bias_sex/bias_sex.sum(axis=1, keepdims = True)
    
    
    # Probability distribution of taking a high-risk partner by risk-group
    # Probabilties are made up
    # Columns: 0 (low-risk), 1(high-risk)
    # Row: the probability of taking a high-risk partner
    p_risky = np.array([0.05, 0.9])
    
    
    # Probability distribution of cheating by risk group
    # Probabilities are made up
    # Columns: 0 (low-risk), 1 (high risk)
    # Row: the probability of cheating on a long-term partner
    p_cheat = np.array([0.05, 0.75])
    
    
    ######################################################
    ##  NARROW DOWN POPULATION TO AVAILABLE CANDIDATES  ##
    ######################################################
    # Pick out the bachelor
    bachelor = meta.loc[bachelor_index,]
        
        
    # Pick out available partners
    if bachelor["orientation"] == 0:
        # Pick out partners for heterosexuals    
        # Could be a heterosexual or a bisexual but must be of the opposite gender
        partners = meta[(meta["orientation"] != 1) &\
                        (meta["gender"] != bachelor["gender"]) &\
                        (partner_matrix[bachelor_index,:]==0) &\
                        (meta.index != bachelor_index)]
        
        
    elif bachelor["orientation"] == 1:
        # Pick out partners for homosexuals
        # Could be a homosexual or a bisexual of the same gender
        partners = meta[(meta["orientation"] != 0) &\
                        (meta["gender"] == bachelor["gender"]) &\
                        (meta.index == np.where(partner_matrix[bachelor_index,:]==0)) &\
                        (meta.index != bachelor_index)]
        
        
    else:
        # Pick out partners for bisexuals
        # Could be anyone but a hetero of the same sex or a homo of the other sex
        partners = meta[~((meta["orientation"] == 0) & (meta["gender"] == bachelor["gender"])) &\
                        ~((meta["orientation"] == 1) & (meta["gender"] != bachelor["gender"])) &\
                        (meta.index == np.where(partner_matrix[bachelor_index,:] == 0)) &\
                        (meta.index != bachelor_index)]
    
    
    #############################################
    ##  DECIDE WHICH AGE GROUP TO PARTER WITH  ##
    #############################################
    if len(partners) > 0:
        
        
        # Pull out age biasing distribution
        partner_dist = bias_age[int(bachelor["age_group"]),] * bias_sex[int(bachelor["gender"])]
        
        
        # Check that there's a parter from each age group available
        to_ignore = partners.groupby("age_group")["age_group"].count().reset_index(name = "count")
        to_ignore = to_ignore[to_ignore["count"] == 0]
        
        
        # Make sure there are still some partners available
        if len(to_ignore) < 3:
            
            
            # Some age groups may still be empty - set frequency of such
            # groups to zero so it's impossible to end up choosing them
            for j in to_ignore["age_group"]:
                partner_dist[int(j)] = 0
        
        
            # Calculate CDF of age/gender distribution
            partner_dist = np.cumsum(partner_dist)
            partner_dist = partner_dist/max(partner_dist)
            
            
            # Decide which age-group to partner with
            partner_age_group = np.searchsorted(partner_dist, np.random.random())
            partners = partners[partners["age_group"] == partner_age_group]
            
            
            ###############################################
            ##  DECIDE WHICH RISK GROUP TO PARTNER WITH  ##
            ###############################################
            
            
            # Decide which risk-group to partner with
            if np.random.random(1) < p_risky[int(bachelor["risk"])]:
                
                # High-risk
                partners = partners[partners["risk"] == 1]
                
            else:
                
                # Low-risk
                partners = partners[partners["risk"] == 0]
            
            
            ###################################################
            ##  DECIDE WHICH PARTNER STATUS TO PARTNER WITH  ##
            ###################################################
            
            
            # Decide whether or not to cheat
            if np.random.random(1) < p_cheat[int(bachelor["risk"])]:
                
                # Cheating
                partners = partners[partners["partner"] != -1]
                
            else:
                # Not cheating
                partners = partners[partners["partner"] == -1]
            
            
            ######################
            ##  FINAL DECISION  ##
            ######################
            
            
            # Now just choose one at random
            if len(partners) > 0:
                partner = np.random.choice(partners.index, 1)
                partner = int(partner)
            else:
                partner = -1
        else:
            partner = -1
    else:
        partner = -1
        

    # Return the meta array but with the updated partner status
    return partner



##############################################################################
##             FUNCTION FOR DECIDING ON THE TYPE OF RELATIONSHIP            ##
##############################################################################
# DECIDE ON THE RELATIONSHIP (CASUAL vs LONG TERM) BETWEEN TWO INDIVIDUALS
#
#
# Decision tree is relatively simple:
#
#   1. Look to see if either i or j are in a long term relationship.
#
#   2.a If at least one of i and j are in a long term relationship, then
#         this is a short term relationship.
#
#   2.b Otherwise make a decision using data from the GOANNA study.
#
#
# INPUT
#   meta = the population array
#   i = the index of the person finding a partner
#   j = the index of their partner
#
# OUTPUT
#   relationship = {0 (long term), 1 (short term)}
#
def choose_relationship(meta, i, j):
    
    
    ######################################################################
    ##  DEFINE PROBABILITY MATRIX FOR AGE GROUP TO RELATIONSHIP STATUS  ##
    ######################################################################
    
    
    # Probability distribution of nature of sexual partnerships
    # Data from Table 5-3 as above
    # Read as: age group (row) and relationship (column)
    # Relationship state space: {0 (long term), 1 (short term)}
    bias_relationship = np.array([[526, 264],
                                  [490, 234],
                                  [449, 150]])
    bias_relationship = bias_relationship/bias_relationship.sum(axis=1, keepdims = True)
    
    
    # Aversion of high-risk group to long-term relationships
    # Made up
    risk_group = meta.at[i, "risk"] + meta.at[i, "risk"]
    aversion = [1, 0.02, 0.005]

    
    ##################################################
    ##  DECIDE ON THE NATURE OF THEIR RELATIONSHIP  ##
    ##################################################
    
    
    # Check that neither of the individuals are in a long term relationship
    if meta.at[i, "partner"] != -1 | meta.at[j, "partner"] != -1:
        
        
        # If already in a long term relationship - set this to be a short term
        relationship = 1
        
        
    # Otherwise make a decision at random based on the age group of i
    else:
        
        
        # Decide if relationship is long term or short term
        bias_relationship = bias_relationship[int(meta.at[i, "age_group"]), :]
        bias_relationship = np.cumsum(bias_relationship)
        bias_relationship[0] = aversion[int(risk_group)] * bias_relationship[0]
        
        
        # High-risk are less likely to get in a long-term relationship
        # if (meta.at[i, "risk"] == 1) | (meta.at[j, "risk"] == 1):
        #     bias_relationship[0] = aversion * bias_relationship[0]
        
        
        # Now decide on a relationship type at random
        relationship = int(np.searchsorted(bias_relationship, np.random.random(1)))
    
    
    # Return which type of relationship has been chosen
    return relationship







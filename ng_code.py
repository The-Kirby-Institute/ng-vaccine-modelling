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
def find_partner(meta, bachelor_index):
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
    #   meta - except a partnership has been formed for the bachelor.
    #
    #   This can be observed in the partner column, which contains the
    #   index of everybody's current partner. With a default value of -1
    #   indicating no partner.
    #
    #   For example, the end result will have the bachelor's index (i) as 
    #   somebody elses partner value and the bachelor will have their
    #   index as their partner value.
    #
    #   In particular, if j is the decided partner, then
    #       meta.loc[i, "partner"] = j
    #       meta.loc[j, "partner"] = i
    #   
    
    
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
    
    
    # Probability distribution of nature of sexual partnerships
    # Data from Table 5-3 as above
    # Read as: age group (row) and relationship (column)
    # Relationship state space: {0 (long term), 1 (short term)}
    bias_relationship = np.array([[526, 264],
                                  [490, 234],
                                  [449, 150]])
    bias_relationship = bias_relationship/bias_relationship.sum(axis=1, keepdims = True)
    
    
    ######################################################
    ##  NARROW DOWN POPULATION TO AVAILABLE CANDIDATES  ##
    ######################################################
    # Pick out the bachelor
    bachelor = meta.loc[bachelor_index,]
    
    
    # Make sure this individual is single
    if bachelor["partner"] == -1:
        
        
        # Pick out available partners
        if bachelor["orientation"] == 0:
            # Pick out partners for heterosexuals    
            # Could be a heterosexual or a bisexual but must be of the opposite gender
            partners = meta[(meta["orientation"] != 1) &\
                            (meta["gender"] != bachelor["gender"]) &\
                            (meta["partner"] == -1) &\
                            (meta.index != bachelor_index)]
            
            
        elif bachelor["orientation"] == 1:
            # Pick out partners for homosexuals
            # Could be a homosexual or a bisexual of the same gender
            partners = meta[(meta["orientation"] != 0) &\
                            (meta["gender"] == bachelor["gender"]) &\
                            (meta["partner"] == -1) &\
                            (meta.index != bachelor_index)]
            
            
        else:
            # Pick out partners for bisexuals
            # Could be anyone but a hetero of the same sex or a homo of the other sex
            partners = meta[~((meta["orientation"] == 0) & (meta["gender"] == bachelor["gender"])) &\
                            ~((meta["orientation"] == 1) & (meta["gender"] != bachelor["gender"])) &\
                            (meta["partner"] == -1) &\
                            (meta.index != bachelor_index)]
        
        
        # Can use this to check the break down of the available pool
        # Check on results - i think they are okay
        # ggplot(partners, aes(x="orientation", fill="gender")) + geom_bar()
        
        
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
                ##  DECIDE WHICH INDIVIDUAL TO PARTNER WITH  ##
                ###############################################
                
                
                # Just choose one at random
                partner = np.random.choice(partners.index, 1)
                
                
                # Update meta
                meta = meta.copy(deep=True)
                meta.at[bachelor_index, "partner"] = partner[0]
                meta.at[partner[0], "partner"] = bachelor_index
                
                
                # Just to make sure
                # print([bachelor_index, meta.at[partner[0], "partner"], \
                #        partner[0], meta.at[bachelor_index, "partner"], len(partner)])
                
                
                ##################################################
                ##  DECIDE ON THE NATURE OF THEIR RELATIONSHIP  ##
                ##################################################
                
                
                # Decide if relationship is long terms or short term
                bias_relationship = np.cumsum(bias_relationship[int(bachelor["age_group"]), :])
                relationship = np.searchsorted(bias_relationship, np.random.random(1))
                
                
                # Put in into meta
                meta.at[bachelor_index, "relationship"] = relationship
                meta.at[partner[0], "relationship"] = relationship
    
    
    # Return the meta array but with the updated partner status
    return meta










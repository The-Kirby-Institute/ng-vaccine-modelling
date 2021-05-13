# -*- coding: utf-8 -*-
"""
         Collection of functions for the remote communities model

INDEX
    find_partner: decides who a given person will partner with
    choose_relationship: decides if a given relationship will be long or short


"""

#%% SETUP Load Libraries
import numpy as np
import pandas as pd


#%% SETUP Read in Data


# Setup distribution for the age-group to age-group preferences
#
#
# Probability matrix of age biasing of last sexual encounter
# Data from Table 5-3 of the GOANNA study - characteristics of last sexual encounter
# Read as: from (row) to (column)
# State space: {16-19, 20-24, 25-29, >29}
# Note that the <16 demographics are excluded as they aren't in the model
# The rows only correspond to the 16-19, 20-24, 25-29 age groups
# bias_age = np.array([[578, 130, 11],
#                      [127, 487, 61],
#                      [27, 243, 174],
#                      [27, 243, 174]],
#         dtype = "float")
#
#
# Update for latest GOANNA survey (Table 5.5)
# bias_age = np.array([[221, 71, 7, 7],
#                      [50, 208, 105, 105],
#                      [9, 58, 198, 198],
#                      [9, 58, 198, 198]],
#         dtype = "float")
# bias_age = bias_age/bias_age.sum(axis=1, keepdims = True)
# bias_age = np.cumsum(bias_age, axis = 1)
#
#
# Read in distribution as csv
bias_age = pd.read_csv('data/age_partnership_distribution.csv')


# Setup distribution for the sex to age-group preferences
#
#
# Probability distribution of sex age bias for last sexual encounter
# Data from Table 5-3 as above
# State space {0 (male), 1 (female)}
# Read as: from (row) to (column)
# bias_sex = np.array([[379, 313, 76, 76],
#                     [346, 546, 170, 170]])
#
#
# Update for latest GOANNA Survey (Table 5.4)
# bias_sex = np.array([[136, 132, 98, 98],
#                      [155, 229, 254, 254]])
# bias_sex = bias_sex/bias_sex.sum(axis=1, keepdims = True)
#
#
# This has been turned off


# Probabilities of partnering with another high-risk individual
#
#
# Probability distribution of taking a high-risk partner by risk-group
# Probabilties are made up
# Columns: 0 (low-risk), 1(high-risk)
# Row: the probability of taking a high-risk partner
# p_risky = np.array([0.05, 0.9])
#
#
p_risky = pd.read_csv('data/probability_high_risk_partner.csv')


# Probabilities of cheating
#
#
# Probability distribution of cheating by risk group
# Probabilities are made up
# Columns: 0 (low-risk), 1 (high risk)
# Row: the probability of cheating on a long-term partner
# p_cheat = np.array([0.05, 0.5])
#
#
p_cheat = pd.read_csv('data/probability_cheat.csv')


# Probabilities of entering a long-term relationship by age group
#
#
# Probability distribution of nature of sexual partnerships
# Data from Table 5-3 as above
# Read as: age group (row) and relationship (column)
# Relationship state space: {0 (long term), 1 (short term)}
# bias_relationship = np.array([[526, 264],
#                               [490, 234],
#                               [449, 150]])
#
#
# Updated for new GOANNA survey (Table 5.5)
# bias_relationship = np.array([[129, 174],
#                               [173, 187],
#                               [157, 109],
#                               [157, 109]])
# bias_relationship = bias_relationship/bias_relationship.sum(axis=1, keepdims = True)
#
#
bias_relationship = pd.read_csv('data/probability_relationship.csv')


# Scaling of the probability of a long term relationship
#
#
# The probability of a long-term relationship by relationship risk-group
# The relationship risk-group defined as follows
#    0 = 0 x high-risk | 2 x low-risk
#    1 = 1 x high-risk | 1 x low-risk
#    2 = 2 x high-risk | 0 x low-risk
# Column: relationship risk-group
# aversion = [1, 0.4, 0.05]
#
#
aversion = pd.read_csv('data/scaling_long_term_by_risk_group.csv')


# Partnership formation rates
#
#
# Probability of forming a new partnership
# Adjusted to agree with the GOANNA survey data
# Row: risk level, column: age-group
#
#
# p_new_partner = np.array([(2/2) * (1/365) * np.array([1, 1, 0.9, 0.9]),
#                           (50/2) * (1/365) * np.array([1.1, 1.1, 1, 1])])
#
#
partner_rates = pd.read_csv('data/partnership_rates.csv')
p_new_partner = pd.read_csv('data/partnership_rates_scaling.csv')
p_new_partner = (1/365) * p_new_partner
p_new_partner.loc[0, :] = partner_rates.low[0] * p_new_partner.loc[0, :]
p_new_partner.loc[1, :] = partner_rates.high[0] * p_new_partner.loc[1, :]


# Partnership duration parameters
#
#
# Parameters of sample distribution for long-term relationships
# Note that this is a Gamma distribution with seperate parameters for
# each relationship risk-group
# Row: parameter, column: relationship risk-group (see above)
# duration_params = {"long": np.array([[365/100, 2*30/10, 2*30/10, 2*30/10],
#                                      [100, 10, 10, 10]]),
#                    "short": 14}
#
#
partner_durations = pd.read_csv('data/partnership_durations.csv')
duration_params = {'long': np.array([4 * [partner_durations.long_mean[0]/partner_durations.long_var[0]],
                                     4 * [partner_durations.long_var[0]]]),
                   'short': partner_durations.short[0]}


#%% FUN update_partnerships()
#
#
# Function to update all partnership dynamics in the model
#
#
def update_partnerships(meta, partner_matrix, partner_expire, t):


    # Update partnership network
    meta, partner_matrix, partner_expire, _, _, _, _ = new_partnership(meta, partner_matrix, partner_expire, t)


    # Remove expired partnerships
    meta, partner_matrix, partner_expire = old_partnerships(meta, partner_matrix, partner_expire, t)


    return meta, partner_matrix, partner_expire


#%% FUN find_partner()
#
# FUNCTION FOR MAKING PARTNERSHIPS
#
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
#       16-19, 20-24, 25-29 and > 29.
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
                        (partner_matrix[bachelor_index,:]==0) &\
                        (meta.index != bachelor_index)]


    else:
        # Pick out partners for bisexuals
        # Could be anyone but a hetero of the same sex or a homo of the other sex
        partners = meta[~((meta["orientation"] == 0) & (meta["gender"] == bachelor["gender"])) &\
                        ~((meta["orientation"] == 1) & (meta["gender"] != bachelor["gender"])) &\
                        (partner_matrix[bachelor_index,:]==0) &\
                        (meta.index != bachelor_index)]


    #############################################
    ##  DECIDE WHICH AGE GROUP TO PARTER WITH  ##
    #############################################
    if len(partners) > 0:


        # Pull out age biasing distribution
        partner_dist = bias_age.iloc[int(bachelor["age_group"]),] #* bias_sex[int(bachelor["gender"])]


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
            if np.random.random(1) < p_risky.iloc[0, int(bachelor["risk"])]:

                # High-risk
                partners = partners[partners["risk"] == 1]

            else:

                # Low-risk
                partners = partners[partners["risk"] == 0]


            ###################################################
            ##  DECIDE WHICH PARTNER STATUS TO PARTNER WITH  ##
            ###################################################


            # Decide whether or not to cheat
            if np.random.random(1) < p_cheat.iloc[0, int(bachelor["risk"])]:

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



#%% FUN choose_relationship()
#
# FUNCTION FOR DECIDING ON THE TYPE OF RELATIONSHIP
#
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


    ##################################################
    ##  DECIDE ON THE NATURE OF THEIR RELATIONSHIP  ##
    ##################################################


    # Check that neither of the individuals are in a long term relationship
    if meta.at[i, "partner"] != -1:


        # If already in a long term relationship - set this to be a short term
        relationship = 1


    elif meta.at[j, "partner"] != -1:


        # If already in a long term relationship - set this to be a short term
        relationship = 1


    # Otherwise make a decision at random based on the age group of i
    else:


        # Decide if relationship is long term or short term
        risk_group = meta.at[i, "risk"] + meta.at[j, "risk"]
        p_relationship = bias_relationship.iloc[int(meta.at[i, "age_group"]), :]
        p_relationship = np.cumsum(p_relationship)
        p_relationship[0] = aversion.iloc[0, int(risk_group)] * p_relationship[0]


        # Now decide on a relationship type at random
        relationship = int(np.searchsorted(p_relationship, np.random.random(1)))


    # print(i, j, relationship)
    # Return which type of relationship has been chosen
    return relationship


#%% FUN prob_partnership()
#
# FUNCTION FOR DECIDING THE PROBABILITY OF FORMING A RELATIONSHIP
#
# THE PER-DAY PROBABILITY OF AN INDIVIDUAL FORMING ANY KIND OF RELATIONSHIP
#
#
# These probabilities are based on a comparison between the resulting partnership
# aquisition rates and those sampled in the GOANNA survey.
#
# Some notes:
#
#   1. The probability of a partnership is given by
#
#          (expected number of partnerships per year) x scaling(age, risk) x cheat(risk)
#
#       In this equation, the expected number of partners is different for
#       the high-risk and the low-risk groups. The the scaling for the low-risk
#       group has been based on the GOANNA numbers and the number for the
#       high-risk group has been tuned.
#
#       The scaling function adjusts the partnership aquisition rates for
#       discrepencies between age groups. For example, it was determined
#       that for the middle age group low-risk partnerships are relatively
#       infrequent while high-risk partnerships are more frequent.
#
#       The cheating function adjusts the partnership aquisition rate to
#       account for cheating behaviour. In particular, how likely is each
#       risk group to cheat on a long-term partner. Note that concurrent
#       short-term partnerships is not considered cheating.
#
#
# INPUT
#   meta = the population array
#   i = the index of the person under consideration
#
# OUTPUT
#   the probability of this individual entering a new partnership
def prob_partnership(meta, i):


    # Probability of making a new partnership
    p_partner_it = ( int(meta.at[i, "partner"] == -1) \
                    + int(meta.at[i, "partner"] != -1) * p_cheat.iloc[0, int(meta.at[i, "risk"])] ) \
                    * p_new_partner.iloc[int(meta.at[i, "risk"]), int(meta.at[i, "age_group"])]


    # Return the partnership formation probability
    return p_partner_it


#%% FUN relationship_duration()
#
# FUNCTION FOR SAMPLING RELATIONSHIP DURATION
#
# SAMPLE THE DURATION OF A PARTNERSHIP
#
#
# Short term relationships are sampled from an exponential distribution with
# a mean of 5 days.
#
# Long term relationships are sampled from a Gamma distribution with a seperate
# set of parameters for each relationhip risk-group.
#
#
# INPUT
#   meta, i, j
#   is_short = {0=long term relationship, 1=short term relationship}
#
# OUTPUT
#   the duration of the relationship
def relationship_duration(meta, i, j, is_short):


    # Sample a duration
    if is_short == 0:
        risk_group = meta.at[i, "risk"] + meta.at[j, "risk"]
        duration = np.random.gamma(duration_params["long"][0, int(risk_group)],
                                   duration_params["long"][1, int(risk_group)])
        #duration = 1000
    else:
        duration = np.random.exponential(duration_params["short"])
        #duration = 1


    # Return duration
    return duration



#%% FUN new_partnership()
#
# FUNCTION FOR MAKING NEW PARTNERSHIPS
#
# CREATE A NEW RELATIONSHIP FOR A GIVEN PERSON
#
#
# 1. Sample prob_partnership() to decide whether or not to make a new relationship
#
# 2. Run find_partner() to decide who the partner will be
#
# 3. Run choose_relationship() to decide if it will be a long or short-term relationship
#
# 4. Sample a duration from relationship_duration()
#
# 5. Update meta, partner_matrix, partner_expire accordingly.
#      Note that entering a long-term relationship causes an end to all
#      current short-term relationships
#
#
# INPUT
#   meta, partner_matrix, partner_expire, i, t
#
# OUTPUT
#   meta, partner_matrix, partner_expire
def new_partnership(meta, partner_matrix, partner_expire, t):


    # Initilise a couple of summary statistics of duration for if you want them
    d0t = []
    d1t = []
    d2t = []
    d3t = []


    # Iterate over all people
    for i in range(0, len(meta)):


        # Determine if this individual will look for a new partner on this iteration
        if np.random.random(1) < prob_partnership(meta, i):


            # Find a new partner
            j = find_partner(meta, partner_matrix, i)


            # Check that a partner was indeed found
            if j != -1:


                # Decide on their relationship type
                is_short = choose_relationship(meta, i, j)


                # Sample a duration
                duration = relationship_duration(meta, i, j, is_short)


                # Updates for long-term relationships
                if is_short == 0:


                    # Update partnership status
                    meta.at[i, "partner"] = j
                    meta.at[j, "partner"] = i


                    # End all other relationships
                    partner_matrix[i,] = 0
                    partner_matrix[j,] = 0
                    partner_expire[i,] = float("inf")
                    partner_expire[j,] = float("inf")


                # Update partnership array
                partner_matrix[i,j] = 1
                partner_matrix[j,i] = 1


                # Update partner counter
                # meta.at[i, "counter"] = meta.at[i, "counter"] + 1
                # meta.at[j, "counter"] = meta.at[j, "counter"] + 1


                # Update partnership duration matrix
                # print(i, j, is_short, duration)
                partner_expire[i, j] = t + duration
                partner_expire[j, i] = t + duration


                # # Update summary statistics, if you want them
                # if meta.at[i, "age_group"] == 0:
                #     d0t.append(duration)
                # elif meta.at[i, "age_group"] == 1:
                #     d1t.append(duration)
                # elif meta.at[i, "age_group"] == 2:
                #     d2t.append(duration)
                # else:
                #     d3t.append(duration)


    # Results
    return meta, partner_matrix, partner_expire, d0t, d1t, d2t, d3t



#%% FUN old_partnerships()
#
# FUNCTION FOR REMOVING OLD PARTNERSHIPS
#
# REMOVE EXPIRED RELATIONSHIPS FROM THE POPULATION
#
#
# Check the partner_expire array to see if any relationships have expired.
# Remove all expired relationships from the array and the partner_matrix array.
# Check meta to see if any of the expired relationships are long-term
# and update meta accordingly.
#
# INPUT
#   meta, partner_matrix, partner_expire, i
#
# OUTPUT
#   meta, partner_matrix, partner_expire
def old_partnerships(meta, partner_matrix, partner_expire, t):


    # Identify elements of partner_expire whose time has expired
    [ii, jj] = np.where(partner_expire < t)


    # Iterate over meta to check if these relationships are long or short term
    for i in range(0, len(ii)):
        if meta.at[ii[i], "partner"] == jj[i]:
            # print("ENDING IT:", ii[i], jj[i], meta.at[ii[i], "partner"], meta.at[jj[i], "partner"], partner_expire[ii[i], jj[i]])
            meta.at[ii[i], "partner"] = -1
            meta.at[jj[i], "partner"] = -1


    # Reset these elements in the partnership matrices
    partner_matrix[ii, jj] = 0
    partner_expire[ii, jj] = float("inf")


    # Return output
    return meta, partner_matrix, partner_expire



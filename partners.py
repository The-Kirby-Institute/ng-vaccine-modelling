# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 11:27:30 2020

@author: nicol

Script for setting up how partnerships are made.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotnine as pn
import ng_code as ng


#%% Setup demographic data


# Set up demographic data
# Note 0 = male and 1 = female in gender column
n = 10000
meta = pd.DataFrame({"gender": np.round(np.random.random(n)),
                     "age": 16 + (29-16)*np.random.random(n)})


# Store gender as a categorical variable
meta["gender"] = meta["gender"].astype("category")


# Categorise by age group
age_group = [None] * n
for i in range(0,n):
    if meta["age"][i] <= 19:
        age_group[i] = int(0)
    elif meta["age"][i] <= 24:
        age_group[i] = int(1)
    else:
        age_group[i] = int(2)
        

# Store age group as factor
meta["age_group"] = age_group
meta["age_group"] = meta["age_group"].astype("category")


# Check on age distributions
groupings = meta.groupby(["gender", "age_group"])["age"].count().reset_index(name="count")
fig = (\
    pn.ggplot(groupings, pn.aes(x="age_group", y="count", group="gender", fill="factor(gender)")) +\
    pn.geom_col(position = "dodge") \
    )
# print(fig)


#%% Determine sexual orientation


# Probability matrix of sexual orientation by gender and age group
# Data from Table 3-3 of the GOANNA study - demographic characteristics by gender and age group
# Note that this data is only given by either gender or age group
# rows = age group and columns = orientation
# Orientation: 0=heterosexual, 1=homosexual, 2=bisexual
orientation_by_age = np.array([[1156/1231, 30/1231, 45/1231],
                               [792/881, 55/881, 34/881],
                               [641/714, 42/714, 31/714]])
orientation_by_age = np.cumsum(orientation_by_age, axis = 1)


# Work out sexual orientations
meta["orientation"] = np.random.random(n)
for i in range(0, 3):
    
    
    # Extract orientation data
    x = meta["orientation"][meta["age_group"] == i]
    
    
    # Determine where each random number falls in the distribution
    x.loc[x <= orientation_by_age[0, 0]] = 0
    x.loc[x >= orientation_by_age[0, 1]] = 2
    x.loc[~np.isin(x, [0, 2])] = 1
    
    
    # Put back into the data frame
    meta.loc[x.index, "orientation"] = x


# Change orientation to categorical variable
meta["orientation"] = meta["orientation"].astype("category")


# Check on age distributions
groupings = meta.groupby(["gender", "age_group", "orientation"])["age"].count().reset_index(name="count")
fig = (\
    pn.ggplot(groupings, pn.aes(x="age_group", y="count", fill="orientation")) +\
    pn.geom_col(position = "stack") +\
    pn.facet_wrap("gender")
    )
# print(fig)


#%% Test partnership biasing function


# # Make a partner column
# # Value is the index of their partner
# # Default to -1 to indicate no partner
# meta["partner"] = -1


# # Make a relationship column
# # Values 0=long term 1=short term
# # Default to -1 for no relationship
# meta["relationship"] = -1


# # Run algorithm for a bunch of people
# for i in range(0, 500):
    
    
#     # Only proceed if this one isn't already partnered
#     if meta.loc[i, "partner"] == -1:
        
        
#         # Find a partner for them
#         meta = ng.find_partner(meta, i)


#%%

t_reset = 400
n_days = t_reset + 365
xt = np.zeros((n_days, 3))
g0t = np.zeros((n_days, 4))
g1t = np.zeros((n_days, 4))
g2t = np.zeros((n_days, 4))

meta["partner"] = -1
meta["relationship"] = -1
meta["partner_expire"] = float("inf")


# Put a dummy column in meta to keep track of how many partners everyone is having
meta["partners"] = 0


# Probability distribution of sexual experience
# Data from Table 5-1
# Read as: age group (row) and number of sexual partners (column)
# Number of partners state space: {0 (none), 1, (one), 2 (two-four), 3 (>=five)}
partner_prob_raw = np.array([[78, 346, 367, 76],
                             [55, 366, 292, 64],
                             [58, 363, 210, 27]])
partner_prob_raw = partner_prob_raw/partner_prob_raw.sum(axis=1, keepdims = True)
partner_prob = 3 * (1/365) * (1-partner_prob_raw)


#
n_people = 1000
for ii in range(0, n_days):
    
    # Iterate over all people
    for jj in range(0, n_people):
        
        # Probability of making a new partnership
        if np.random.random(1) < partner_prob[int(meta.loc[jj, "age_group"]), 0]:
            if meta.loc[jj, "partner"] == -1:
                
                # Implement partnership
                meta = ng.find_partner(meta, jj)
                
                # Check that a partner was indeed found
                if meta.loc[jj, "partner"] != -1:
                    
                    # Update the partner counter
                    meta.loc[jj, "partners"] = meta.loc[jj, "partners"] + 1
                    meta.loc[meta.loc[jj,"partner"], "partners"] = meta.loc[meta.loc[jj,"partner"], "partners"] + 1
                    
                    # Make up a duration
                    if meta.loc[jj, "relationship"] == 0:
                        duration = np.random.exponential(6*30)
                        meta.loc[jj, "partner_expire"] = ii + duration
                        meta.loc[meta.loc[jj, "partner"], "partner_expire"] = ii + duration
                    else:
                        duration = np.random.exponential(30)
                        meta.loc[jj, "partner_expire"] = ii + duration
                        meta.loc[meta.loc[jj, "partner"], "partner_expire"] = ii + duration
    
    # Identify expired relationships
    expired = meta["partner_expire"] <= ii
    meta.loc[expired, "partner"] = -1
    meta.loc[expired, "relationship"] = -1
    meta.loc[expired, "partner_expire"] = float("inf")
    
    # Update xt - partnership status
    xt[ii, 0] = sum((meta["partner"][range(0,n_people)] != -1) & (meta["relationship"][range(0,n_people)] == 0))
    xt[ii, 1] = sum((meta["partner"][range(0,n_people)] != -1) & (meta["relationship"][range(0,n_people)] == 1))
    xt[ii, 2] = sum((meta["partner"][range(0,n_people)] == -1))
    
    # Update partnership groups for age group 0
    g0t[ii, 0] = sum((meta["age_group"] == 0) & (meta["partners"][range(0,n_people)] == 0))
    g0t[ii, 1] = sum((meta["age_group"] == 0) & (meta["partners"][range(0,n_people)] == 1))
    g0t[ii, 2] = sum((meta["age_group"] == 0) & (meta["partners"][range(0,n_people)] > 1) & \
                     (meta["partners"][range(0,n_people)] < 5))
    g0t[ii, 3] = sum((meta["age_group"] == 0) & (meta["partners"][range(0,n_people)] > 4))
    
    # Update partnership groups for age group 0
    g1t[ii, 0] = sum((meta["age_group"] == 1) & (meta["partners"][range(0,n_people)] == 0))
    g1t[ii, 1] = sum((meta["age_group"] == 1) & (meta["partners"][range(0,n_people)] == 1))
    g1t[ii, 2] = sum((meta["age_group"] == 1) & (meta["partners"][range(0,n_people)] > 1) & \
                     (meta["partners"][range(0,n_people)] < 5))
    g1t[ii, 3] = sum((meta["age_group"] == 1) & (meta["partners"][range(0,n_people)] > 4))
    
    # Update partnership groups for age group 0
    g2t[ii, 0] = sum((meta["age_group"] == 2) & (meta["partners"][range(0,n_people)] == 0))
    g2t[ii, 1] = sum((meta["age_group"] == 2) & (meta["partners"][range(0,n_people)] == 1))
    g2t[ii, 2] = sum((meta["age_group"] == 2) & (meta["partners"][range(0,n_people)] > 1) & \
                     (meta["partners"][range(0,n_people)] < 5))
    g2t[ii, 3] = sum((meta["age_group"] == 2) & (meta["partners"][range(0,n_people)] > 4))
    
    # At the turn of the 1000th time step, start counting
    if ii == t_reset:
        meta["partners"] = 0
        meta.loc[meta["partner"] != -1, "partners"] = 1
    
    
    
    
        

# Plot long vs short term partnerships over time
fig, ax = plt.subplots(4)
ax[0].plot(range(0, n_days), xt[:,0], label = "long term")
ax[0].plot(range(0, n_days), xt[:,1], label = "short term")
ax[0].plot(range(0, n_days), xt[:,2], label = "single")
ax[0].set_ylim([0, np.max(xt)])
ax[0].legend()

# Plot the number of people in each partnership group over time
ax[1].plot(range(0, n_days), g0t[:,0], label = "0", color = "blue")
ax[1].plot(range(0, n_days), g0t[:,1], label = "1", color = "red")
ax[1].plot(range(0, n_days), g0t[:,2], label = "2-4", color = "green")
ax[1].plot(range(0, n_days), g0t[:,3], label = ">4", color = "purple")
weight = sum(g0t[0,:])
ax[1].axhline(weight*partner_prob_raw[0,0], color = "blue", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,1], color = "red", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,2], color= "green", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,3], color = "purple", linestyle = "--")
#ax[1].set_xlim([1000, 1365])
ax[1].legend()

# Plot the number of people in each partnership group over time
ax[2].plot(range(0, n_days), g1t[:,0], label = "0", color = "blue")
ax[2].plot(range(0, n_days), g1t[:,1], label = "1", color = "red")
ax[2].plot(range(0, n_days), g1t[:,2], label = "2-4", color = "green")
ax[2].plot(range(0, n_days), g1t[:,3], label = ">4", color = "purple")
weight = sum(g1t[0,:])
ax[2].axhline(weight*partner_prob_raw[1,0], color = "blue", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,1], color = "red", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,2], color= "green", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,3], color = "purple", linestyle = "--")
#ax[2].set_xlim([1000, 1365])
ax[2].legend()

# Plot the number of people in each partnership group over time
ax[3].plot(range(0, n_days), g2t[:,0], label = "0", color = "blue")
ax[3].plot(range(0, n_days), g2t[:,1], label = "1", color = "red")
ax[3].plot(range(0, n_days), g2t[:,2], label = "2-4", color = "green")
ax[3].plot(range(0, n_days), g2t[:,3], label = ">4", color = "purple")
weight = sum(g2t[0,:])
ax[3].axhline(weight*partner_prob_raw[2,0], color = "blue", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,1], color = "red", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,2], color= "green", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,3], color = "purple", linestyle = "--")
#ax[3].set_xlim([1000, 1365])
ax[3].legend()
    
        

# Make a plot
# fig, ax = plt.subplots(3)
# ax[0].plot(T, xt["S"], label = "S")
# ax[0].plot(T, xt["I"], label = "I")
# ax[0].plot(T, xt["R"], label = "R")
# ax[0].set_title("Compartment Status")
# ax[0].legend()

# ax[1].plot(T, xt["single"], label = "Single")
# ax[1].plot(T, xt["partnered"], label = "Partnered")
# ax[1].set_title("Partnership Status")
# ax[1].legend()

# ax[2].plot(T, xt["site0"], label = "Rectal")
# ax[2].plot(T, xt["site1"], label = "Urogenital")
# ax[2].plot(T, xt["site2"], label = "Pharyngeal")
# ax[2].set_title("Prevalence by Anatomical Site")
# ax[2].legend()
                










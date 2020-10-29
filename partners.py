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
n = 1000
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
print(fig)


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
print(fig)


#%% Set Risk groups


# Probability distribution of sexual experience
# Data from Table 5-1
# Read as: age group (row) and number of sexual partners (column)
# Number of partners state space: {0 (none), 1, (one), 2 (two-four), 3 (>=five)}
partner_prob_raw = np.array([[78, 346, 367, 76],
                             [55, 366, 292, 64],
                             [58, 363, 210, 27]])
partner_prob_raw = partner_prob_raw/partner_prob_raw.sum(axis=1, keepdims = True)


# Risk
# 0=low and 1=high
meta["risk"] = np.random.random(n)
meta.loc[(meta["age_group"] == 0) & (meta["risk"] < partner_prob_raw[0,3]), "risk"] = 1
meta.loc[(meta["age_group"] == 1) & (meta["risk"] < partner_prob_raw[1,3]), "risk"] = 1
meta.loc[(meta["age_group"] == 2) & (meta["risk"] < partner_prob_raw[2,3]), "risk"] = 1
meta.loc[meta["risk"] != 1, "risk"] = 0


#%% Test partnership biasing function


# Make a big array for setting partnership conncetions
partner_matrix = np.zeros((n,n))


# Make a partner column
# Value is the index of their partner
# Default to -1 to indicate no partner
meta["partner"] = -1


# Run algorithm for a bunch of people
if False:
    for k in range(0, 200):
        for i in range(0, n):
            
            
            # Find a partner
            j = ng.find_partner(meta, partner_matrix, i)
            
            
            if j != -1:
                
                
                # Decide on their relationship
                is_short = ng.choose_relationship(meta, i, j)
                
                
                # Update population array
                partner_matrix[i,j] = 1
                partner_matrix[j,i] = 1
                
                
                # Update partners array
                if is_short == 0:
                    meta.at[i, "partner"] = j
                    meta.at[j, "partner"] = i
    
    plt.imshow(partner_matrix)
    

#%% Test Partnership aquisition rates


# Default partnership durations to Inf
partner_expire = float("inf") * np.ones((n, n))


# Set simulation length
t_reset = 300


# Set time to start counting from
n_days = t_reset + 365


# Number of partners last year
meta["counter"] = 0
xt = np.zeros((n_days, 4))
g0t = np.zeros((n_days, 4))
g1t = np.zeros((n_days, 4))
g2t = np.zeros((n_days, 4))


# Duration of partnerships
d0ht = []
d0lt = []
d1ht = []
d1lt = []
d2ht = []
d2lt = []


# In each partnership
p0ht = np.zeros((n_days, 5))
p0lt = np.zeros((n_days, 5))
p1ht = np.zeros((n_days, 5))
p1lt = np.zeros((n_days, 5))
p2ht = np.zeros((n_days, 5))
p2lt = np.zeros((n_days, 5))


# Probability of forming a new partnership
# Calibrated
# Row: risk level, column: age-group
scaling = np.array([0.9, 0.4, 1.4])
p_new_partner = np.array([(2/2) * (1/365) * scaling,
                          (200/2) * (1/365) * np.array([1, 1.1, 1])])
p_cheat = np.array([0.05, 0.9])

dur_par = np.array([[365/100, 3*30/10, 3*30/10],
                    [100, 10, 10]])


#
n_people = min(n, 2000)
for t in range(0, n_days):
    print(t)
    
    
    # Iterate over all people
    for i in range(0, n_people):
        
        
        # Probability of making a new partnership
        p_partner_it = ( int(meta.at[i, "partner"] == -1) \
                         + int(meta.at[i, "partner"] != -1) * p_cheat[int(meta.at[i, "risk"])] ) \
                        * p_new_partner[int(meta.at[i, "risk"]), int(meta.at[i, "age_group"])]
            
            
        if np.random.random(1) < p_partner_it:
            
            
            # Find a new partner
            j = ng.find_partner(meta, partner_matrix, i)
            
            
            # Check that a partner was indeed found
            if j != -1:
                
                
                # Decide on their relationship
                is_short = ng.choose_relationship(meta, i, j)
                
                
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
                meta.at[i, "counter"] = meta.at[i, "counter"] + 1
                meta.at[j, "counter"] = meta.at[j, "counter"] + 1
                
                
                # Make up a duration
                if is_short == 0:
                    # duration = np.random.exponential(12*30)
                    # duration = np.random.normal(365, 100)
                    # duration = np.random.triangular(6*30, 365, 10*365)
                    risk_group = meta.at[i, "risk"] + meta.at[i, "risk"]
                    duration = np.random.gamma(dur_par[0, int(risk_group)], dur_par[1, int(risk_group)])
                else:
                    duration = np.random.exponential(5)
                    
                
                # Update partnership duration matrix
                partner_expire[i, j] = t + duration
                partner_expire[j, i] = t + duration
                
                
                # Store duration as summary statistic
                duration = min(duration, n_days)
                if (meta.at[i, "age_group"] == 0) & (meta.at[i, "risk"] == 0):
                    d0lt.append(duration)
                elif (meta.at[i, "age_group"] == 0) & (meta.at[i, "risk"] == 1):
                    d0ht.append(duration)
                elif (meta.at[i, "age_group"] == 1) & (meta.at[i, "risk"] == 0):
                    d1lt.append(duration)
                elif (meta.at[i, "age_group"] == 1) & (meta.at[i, "risk"] == 1):
                    d1ht.append(duration)
                elif (meta.at[i, "age_group"] == 2) & (meta.at[i, "risk"] == 0):
                    d2lt.append(duration)
                elif (meta.at[i, "age_group"] == 2) & (meta.at[i, "risk"] == 1):
                    d2ht.append(duration)
    
    
    # Identify and remove expired relationships
    [ii, jj] = np.where(partner_expire < t)
    partner_matrix[ii, jj] = 0
    partner_expire[ii, jj] = float("inf")
    for i in range(0, len(ii)):
        if meta.at[ii[i], "partner"] == jj[i]:
            meta.at[ii[i], "partner"] = -1
            meta.at[jj[i], "partner"] = -1
    
    
    # Track the number of partners over time
    xt[t, 0] = sum(np.sum(partner_matrix, axis = 1) == 0)
    xt[t, 1] = sum(meta["partner"] != -1)
    xt[t, 2] = sum(np.sum(partner_matrix, axis = 1) > 0) - xt[t, 1]
    xt[t, 3] = np.median(partner_expire[partner_expire < float("inf")]) - t
    
    
    # Update partnership groups for age group 0
    g0t[t, 0] = sum((meta["age_group"] == 0) & (meta["counter"][range(0,n_people)] == 0))
    g0t[t, 1] = sum((meta["age_group"] == 0) & (meta["counter"][range(0,n_people)] == 1))
    g0t[t, 2] = sum((meta["age_group"] == 0) & (meta["counter"][range(0,n_people)] > 1) & \
                      (meta["counter"][range(0,n_people)] < 5))
    g0t[t, 3] = sum((meta["age_group"] == 0) & (meta["counter"][range(0,n_people)] > 4))
    
    # Update partnership groups for age group 0
    g1t[t, 0] = sum((meta["age_group"] == 1) & (meta["counter"][range(0,n_people)] == 0))
    g1t[t, 1] = sum((meta["age_group"] == 1) & (meta["counter"][range(0,n_people)] == 1))
    g1t[t, 2] = sum((meta["age_group"] == 1) & (meta["counter"][range(0,n_people)] > 1) & \
                      (meta["counter"][range(0,n_people)] < 5))
    g1t[t, 3] = sum((meta["age_group"] == 1) & (meta["counter"][range(0,n_people)] > 4))
    
    # Update partnership groups for age group 0
    g2t[t, 0] = sum((meta["age_group"] == 2) & (meta["counter"][range(0,n_people)] == 0))
    g2t[t, 1] = sum((meta["age_group"] == 2) & (meta["counter"][range(0,n_people)] == 1))
    g2t[t, 2] = sum((meta["age_group"] == 2) & (meta["counter"][range(0,n_people)] > 1) & \
                      (meta["counter"][range(0,n_people)] < 5))
    g2t[t, 3] = sum((meta["age_group"] == 2) & (meta["counter"][range(0,n_people)] > 4))
    
    
    # Update the number of people in each partnership type
    p = np.sum(partner_matrix, axis = 1)
    p0ht[t, 0] = sum((meta["age_group"] == 0) & (meta["risk"] == 1) & (p == 0))
    p0ht[t, 1] = sum((meta["age_group"] == 0) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p == 1))
    p0ht[t, 2] = sum((meta["age_group"] == 0) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p > 1))
    p0ht[t, 3] = sum((meta["age_group"] == 0) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p == 1))
    p0ht[t, 4] = sum((meta["age_group"] == 0) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p > 1))
    
    p0lt[t, 0] = sum((meta["age_group"] == 0) & (meta["risk"] == 0) & (p == 0))
    p0lt[t, 1] = sum((meta["age_group"] == 0) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p == 1))
    p0lt[t, 2] = sum((meta["age_group"] == 0) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p > 1))
    p0lt[t, 3] = sum((meta["age_group"] == 0) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p == 1))
    p0lt[t, 4] = sum((meta["age_group"] == 0) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p > 1))
    
    p1ht[t, 0] = sum((meta["age_group"] == 1) & (meta["risk"] == 1) & (p == 0))
    p1ht[t, 1] = sum((meta["age_group"] == 1) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p == 1))
    p1ht[t, 2] = sum((meta["age_group"] == 1) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p > 1))
    p1ht[t, 3] = sum((meta["age_group"] == 1) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p == 1))
    p1ht[t, 4] = sum((meta["age_group"] == 1) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p > 1))
    
    p1lt[t, 0] = sum((meta["age_group"] == 1) & (meta["risk"] == 0) & (p == 0))
    p1lt[t, 1] = sum((meta["age_group"] == 1) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p == 1))
    p1lt[t, 2] = sum((meta["age_group"] == 1) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p > 1))
    p1lt[t, 3] = sum((meta["age_group"] == 1) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p == 1))
    p1lt[t, 4] = sum((meta["age_group"] == 1) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p > 1))
    
    p2ht[t, 0] = sum((meta["age_group"] == 2) & (meta["risk"] == 1) & (p == 0))
    p2ht[t, 1] = sum((meta["age_group"] == 2) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p == 1))
    p2ht[t, 2] = sum((meta["age_group"] == 2) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p > 1))
    p2ht[t, 3] = sum((meta["age_group"] == 2) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p == 1))
    p2ht[t, 4] = sum((meta["age_group"] == 2) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p > 1))
    
    p2lt[t, 0] = sum((meta["age_group"] == 2) & (meta["risk"] == 0) & (p == 0))
    p2lt[t, 1] = sum((meta["age_group"] == 2) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p == 1))
    p2lt[t, 2] = sum((meta["age_group"] == 2) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p > 1))
    p2lt[t, 3] = sum((meta["age_group"] == 2) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p == 1))
    p2lt[t, 4] = sum((meta["age_group"] == 2) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p > 1))
    
    
    # Reset partner counters at time t_reset
    if t == t_reset:
        meta.counter.at[:] = np.sum(partner_matrix, axis=1)





# Plot of the partnership matrix
plt.imshow(partner_matrix)



#%%
# Plot long vs short term partnerships over time
fig, ax = plt.subplots(4)
ax[0].plot(range(0, n_days), xt[:,0], label = "single")
ax[0].plot(range(0, n_days), xt[:,1], label = "long term")
ax[0].plot(range(0, n_days), xt[:,2], label = "short term")
ax[0].plot(range(0, n_days), xt[:,3], label = "time left")
ax[0].set_ylim([0, n])
ax[0].legend(loc = "upper right")


# Plot the number of people in each partnership group over time
ax[1].plot(range(0, n_days), g0t[:,0], label = "0", color = "blue")
ax[1].plot(range(0, n_days), g0t[:,1], label = "1", color = "red")
ax[1].plot(range(0, n_days), g0t[:,2], label = "2-4", color = "green")
ax[1].plot(range(0, n_days), g0t[:,3], label = "5 more", color = "purple")
weight = sum(g0t[0,:])
ax[1].axhline(weight*partner_prob_raw[0,0], color = "blue", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,1], color = "red", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,2], color= "green", linestyle = "--")
ax[1].axhline(weight*partner_prob_raw[0,3], color = "purple", linestyle = "--")
ax[1].set_xlim([t_reset, n_days])
ax[1].legend(loc = "upper right")
ax[0].set_title("Comparison of 12-month partner count to GOANNA data")


# Plot the number of people in each partnership group over time
ax[2].plot(range(0, n_days), g1t[:,0], label = "0", color = "blue")
ax[2].plot(range(0, n_days), g1t[:,1], label = "1", color = "red")
ax[2].plot(range(0, n_days), g1t[:,2], label = "2-4", color = "green")
ax[2].plot(range(0, n_days), g1t[:,3], label = "5 more", color = "purple")
weight = sum(g1t[0,:])
ax[2].axhline(weight*partner_prob_raw[1,0], color = "blue", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,1], color = "red", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,2], color= "green", linestyle = "--")
ax[2].axhline(weight*partner_prob_raw[1,3], color = "purple", linestyle = "--")
ax[2].set_xlim([t_reset, n_days])


# Plot the number of people in each partnership group over time
ax[3].plot(range(0, n_days), g2t[:,0], label = "0", color = "blue")
ax[3].plot(range(0, n_days), g2t[:,1], label = "1", color = "red")
ax[3].plot(range(0, n_days), g2t[:,2], label = "2-4", color = "green")
ax[3].plot(range(0, n_days), g2t[:,3], label = "5 more", color = "purple")
weight = sum(g2t[0,:])
ax[3].axhline(weight*partner_prob_raw[2,0], color = "blue", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,1], color = "red", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,2], color= "green", linestyle = "--")
ax[3].axhline(weight*partner_prob_raw[2,3], color = "purple", linestyle = "--")
ax[3].set_xlim([t_reset, n_days])



#%%
# Partner durations
fig, ax = plt.subplots(3)

ax[0].hist(d0lt, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "low-risk", density = True)
ax[0].hist(d0ht, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "high-risk", density = True)
ax[0].legend()

ax[1].hist(d1lt, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "low-risk", density = True)
ax[1].hist(d1ht, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "high-risk", density = True)

ax[2].hist(d2lt, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "low-risk", density = True)
ax[2].hist(d2ht, alpha = 0.6, bins = int(n_days/5), range = (0, n_days), label = "high-risk", density = True)



#%% Number of people in each relationship type
t = range(0, n_days)
fig, ax = plt.subplots(3, 2)
n_g = sum((meta.age_group == 0) & (meta.risk == 1))
ax[0, 0].bar(t, (p0ht[:,0] + p0ht[:,1] + p0ht[:,2] + p0ht[:,3] + p0ht[:,4])/n_g, color = "navy", width = 1)
ax[0, 0].bar(t, (p0ht[:,1] + p0ht[:,2] + p0ht[:,3] + p0ht[:,4])/n_g, color = "darkred", width = 1)
ax[0, 0].bar(t, (p0ht[:,1] + p0ht[:,2] + p0ht[:,3])/n_g, color = "red", width = 1)
ax[0, 0].bar(t, (p0ht[:,1] + p0ht[:,2])/n_g, color = "darkgreen", width = 1)
ax[0, 0].bar(t, p0ht[:,1]/n_g, color = "green", width = 1)
ax[0, 0].set_title("High-risk")
ax[0, 0].set_ylabel("Age 16-19")
ax[0, 0].set_xlim([0, n_days])
ax[0, 0].set_ylim([0, 1])


n_g = sum((meta.age_group == 0) & (meta.risk == 0))
ax[0, 1].bar(t, (p0lt[:,0] + p0lt[:,1] + p0lt[:,2] + p0lt[:,3] + p0lt[:,4])/n_g, color = "navy", width = 1)
ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2] + p0lt[:,3] + p0lt[:,4])/n_g, color = "darkred", width = 1)
ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2] + p0lt[:,3])/n_g, color = "red", width = 1)
ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2])/n_g, color = "darkgreen", width = 1)
ax[0, 1].bar(t, p0lt[:,1]/n_g, color = "green", width = 1)
ax[0, 1].set_title("Low-risk")
ax[0, 1].set_xlim([0, n_days])
ax[0, 1].set_ylim([0, 1])


n_g = sum((meta.age_group == 1) & (meta.risk == 1))
ax[1, 0].bar(t, (p1ht[:,0] + p1ht[:,1] + p1ht[:,2] + p1ht[:,3] + p1ht[:,4])/n_g, color = "navy", width = 1)
ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2] + p1ht[:,3] + p1ht[:,4])/n_g, color = "darkred", width = 1)
ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2] + p1ht[:,3])/n_g, color = "red", width = 1)
ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2])/n_g, color = "darkgreen", width = 1)
ax[1, 0].bar(t, p1ht[:,1]/n_g, color = "green", width = 1)
ax[1, 0].set_ylabel("Age 20-24")
ax[1, 0].set_xlim([0, n_days])
ax[1, 0].set_ylim([0, 1])

n_g = sum((meta.age_group == 1) & (meta.risk == 0))
ax[1, 1].bar(t, (p1lt[:,0] + p1lt[:,1] + p1lt[:,2] + p1lt[:,3] + p1lt[:,4])/n_g, color = "navy", width = 1)
ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2] + p1lt[:,3] + p1lt[:,4])/n_g, color = "darkred", width = 1)
ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2] + p1lt[:,3])/n_g, color = "red", width = 1)
ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2])/n_g, color = "darkgreen", width = 1)
ax[1, 1].bar(t, p1lt[:,1]/n_g, color = "green", width = 1)
ax[1, 1].set_xlim([0, n_days])
ax[1, 1].set_ylim([0, 1])


n_g = sum((meta.age_group == 2) & (meta.risk == 1))
ax[2, 0].bar(t, (p2ht[:,0] + p2ht[:,1] + p2ht[:,2] + p2ht[:,3] + p2ht[:,4])/n_g, label = "Single", color = "navy", width = 1)
ax[2, 0].bar(t, (p2ht[:,1] + p2ht[:,2] + p2ht[:,3] + p2ht[:,4])/n_g, label = "Short-term concurrent", color = "darkred", width = 1)
ax[2, 0].bar(t, (p2ht[:,1] + p2ht[:,2] + p2ht[:,3])/n_g, label = "Short-term", color = "red", width = 1)
ax[2, 0].bar(t, (p2ht[:,1] + p2ht[:,2])/n_g, label = "Long-term concurrent", color = "darkgreen", width = 1)
ax[2, 0].bar(t, p2ht[:,1]/n_g, label = "Long-term", color = "green", width = 1)
ax[2, 0].legend(loc = "lower left", bbox_to_anchor=(0.18,-0.05), bbox_transform=fig.transFigure, ncol=3)
ax[2, 0].set_xlim([0, n_days])
ax[2, 0].set_ylabel("Age 25-29")
ax[2, 0].set_xlabel("Time (days)")
ax[2, 0].set_ylim([0, 1])

n_g = sum((meta.age_group == 2) & (meta.risk == 0))
ax[2, 1].bar(t, (p2lt[:,0] + p2lt[:,1] + p2lt[:,2] + p2lt[:,3] + p2lt[:,4])/n_g, color = "navy", width = 1)
ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2] + p2lt[:,3] + p2lt[:,4])/n_g, color = "darkred", width = 1)
ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2] + p2lt[:,3])/n_g, color = "red", width = 1)
ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2])/n_g, color = "darkgreen", width = 1)
ax[2, 1].bar(t, p2lt[:,1]/n_g, color = "green", width = 1)
ax[2, 1].set_xlim([0, n_days])
ax[2, 1].set_ylim([0, 1])
ax[2, 1].set_xlabel("Time (days)")

fig.savefig("graphs/relationship_distribution.pdf")






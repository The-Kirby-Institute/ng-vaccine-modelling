# -*- coding: utf-8 -*-
"""
Some functions for producing summary stats on the partnership model
"""


import numpy as np


#%% Summary statistics on the duration of relationships
def update_duration_stats(duration, meta, i, d0lt, d0ht, d1lt, d1ht, d2lt, d2ht):
    # duration = min(duration, n_days)
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
    return d0lt, d0ht, d1lt, d1ht, d2lt, d2ht


#%% Summary statistics on the cumulative number of partners per year
def update_cumulative_partners(meta, partner_matrix, partner_expire, t, n_people, xt, g0t, g1t, g2t):
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
    
    return xt, g0t, g1t, g2t


#%% Summary statistics on the number of people in each partnership type
def update_partnership_types(meta, partner_matrix, t, p0ht, p0lt, p1ht, p1lt, p2ht, p2lt):
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
    return p0ht, p0lt, p1ht, p1lt, p2ht, p2lt
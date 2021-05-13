# -*- coding: utf-8 -*-
"""
Some functions for producing summary stats on the partnership model
"""


import numpy as np
import matplotlib.pyplot as plt


#%% Summary statistics on the duration of relationships
# def update_duration_stats(duration, meta, i, d0lt, d0ht, d1lt, d1ht, d2lt, d2ht):
#     # duration = min(duration, n_days)
#     if (meta.at[i, "age_group"] == 0) & (meta.at[i, "risk"] == 0):
#         d0lt.append(duration)
#     elif (meta.at[i, "age_group"] == 0) & (meta.at[i, "risk"] == 1):
#         d0ht.append(duration)
#     elif (meta.at[i, "age_group"] == 1) & (meta.at[i, "risk"] == 0):
#         d1lt.append(duration)
#     elif (meta.at[i, "age_group"] == 1) & (meta.at[i, "risk"] == 1):
#         d1ht.append(duration)
#     elif (meta.at[i, "age_group"] == 2) & (meta.at[i, "risk"] == 0):
#         d2lt.append(duration)
#     elif (meta.at[i, "age_group"] == 2) & (meta.at[i, "risk"] == 1):
#         d2ht.append(duration)
#     return d0lt, d0ht, d1lt, d1ht, d2lt, d2ht


#%% Initilise arrays for tracking partnership numbers
def initilise_partner_number_tracking(n_days):
    # Tracking the number of people in each partnership type
    p0ht = np.zeros((n_days, 5))
    p0lt = np.zeros((n_days, 5))
    p1ht = np.zeros((n_days, 5))
    p1lt = np.zeros((n_days, 5))
    p2ht = np.zeros((n_days, 5))
    p2lt = np.zeros((n_days, 5))
    p3ht = np.zeros((n_days, 5))
    p3lt = np.zeros((n_days, 5))
    
    
    # Tracking the cumulative number of partners
    xt = np.zeros((n_days, 4))
    g0t = np.zeros((n_days, 4))
    g1t = np.zeros((n_days, 4))
    g2t = np.zeros((n_days, 4))
    g3t = np.zeros((n_days, 4))
    
    
    # Return
    return p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt, xt, g0t, g1t, g2t, g3t


#%% Summary statistics on the cumulative number of partners per year
def update_cumulative_partners(meta, partner_matrix, partner_expire, t, n_people, xt, g0t, g1t, g2t, g3t):
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


    # Update partnership groups for age group 0
    g3t[t, 0] = sum((meta["age_group"] == 3) & (meta["counter"][range(0,n_people)] == 0))
    g3t[t, 1] = sum((meta["age_group"] == 3) & (meta["counter"][range(0,n_people)] == 1))
    g3t[t, 2] = sum((meta["age_group"] == 3) & (meta["counter"][range(0,n_people)] > 1) & \
                      (meta["counter"][range(0,n_people)] < 5))
    g3t[t, 3] = sum((meta["age_group"] == 3) & (meta["counter"][range(0,n_people)] > 4))

    return xt, g0t, g1t, g2t, g3t


#%% Summary statistics on the number of people in each partnership type
def update_partnership_types(meta, partner_matrix, t, p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt):
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

    p3ht[t, 0] = sum((meta["age_group"] == 3) & (meta["risk"] == 1) & (p == 0))
    p3ht[t, 1] = sum((meta["age_group"] == 3) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p == 1))
    p3ht[t, 2] = sum((meta["age_group"] == 3) & (meta["risk"] == 1) & (meta["partner"] != -1) & (p > 1))
    p3ht[t, 3] = sum((meta["age_group"] == 3) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p == 1))
    p3ht[t, 4] = sum((meta["age_group"] == 3) & (meta["risk"] == 1) & (meta["partner"] == -1) & (p > 1))

    p3lt[t, 0] = sum((meta["age_group"] == 3) & (meta["risk"] == 0) & (p == 0))
    p3lt[t, 1] = sum((meta["age_group"] == 3) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p == 1))
    p3lt[t, 2] = sum((meta["age_group"] == 3) & (meta["risk"] == 0) & (meta["partner"] != -1) & (p > 1))
    p3lt[t, 3] = sum((meta["age_group"] == 3) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p == 1))
    p3lt[t, 4] = sum((meta["age_group"] == 3) & (meta["risk"] == 0) & (meta["partner"] == -1) & (p > 1))
    return p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt


#%% FUN graph_partnership_numbers()
def graph_partnership_numbers(meta, n_days, p0ht, p0lt, p1ht, p1lt, p2ht, p2lt, p3ht, p3lt, save_dir):
    
    
    # Setup graph
    t = range(0, n_days)
    fig, ax = plt.subplots(4, 2)


    # Graph of partnershipd in high risk 16-20
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


    # Graph of partnershipd in low risk 16-20
    n_g = sum((meta.age_group == 0) & (meta.risk == 0))
    ax[0, 1].bar(t, (p0lt[:,0] + p0lt[:,1] + p0lt[:,2] + p0lt[:,3] + p0lt[:,4])/n_g, color = "navy", width = 1)
    ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2] + p0lt[:,3] + p0lt[:,4])/n_g, color = "darkred", width = 1)
    ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2] + p0lt[:,3])/n_g, color = "red", width = 1)
    ax[0, 1].bar(t, (p0lt[:,1] + p0lt[:,2])/n_g, color = "darkgreen", width = 1)
    ax[0, 1].bar(t, p0lt[:,1]/n_g, color = "green", width = 1)
    ax[0, 1].set_title("Low-risk")
    ax[0, 1].set_xlim([0, n_days])
    ax[0, 1].set_ylim([0, 1])


    # Graph of partnershipd in high risk 21-24
    n_g = sum((meta.age_group == 1) & (meta.risk == 1))
    ax[1, 0].bar(t, (p1ht[:,0] + p1ht[:,1] + p1ht[:,2] + p1ht[:,3] + p1ht[:,4])/n_g, color = "navy", width = 1)
    ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2] + p1ht[:,3] + p1ht[:,4])/n_g, color = "darkred", width = 1)
    ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2] + p1ht[:,3])/n_g, color = "red", width = 1)
    ax[1, 0].bar(t, (p1ht[:,1] + p1ht[:,2])/n_g, color = "darkgreen", width = 1)
    ax[1, 0].bar(t, p1ht[:,1]/n_g, color = "green", width = 1)
    ax[1, 0].set_ylabel("Age 20-24")
    ax[1, 0].set_xlim([0, n_days])
    ax[1, 0].set_ylim([0, 1])


    # Graph of partnershipd in low risk 21-24
    n_g = sum((meta.age_group == 1) & (meta.risk == 0))
    ax[1, 1].bar(t, (p1lt[:,0] + p1lt[:,1] + p1lt[:,2] + p1lt[:,3] + p1lt[:,4])/n_g, color = "navy", width = 1)
    ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2] + p1lt[:,3] + p1lt[:,4])/n_g, color = "darkred", width = 1)
    ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2] + p1lt[:,3])/n_g, color = "red", width = 1)
    ax[1, 1].bar(t, (p1lt[:,1] + p1lt[:,2])/n_g, color = "darkgreen", width = 1)
    ax[1, 1].bar(t, p1lt[:,1]/n_g, color = "green", width = 1)
    ax[1, 1].set_xlim([0, n_days])
    ax[1, 1].set_ylim([0, 1])


    # Graph of partnershipd in high risk 25-29
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


    # Graph of partnershipd in low risk 25-29
    n_g = sum((meta.age_group == 2) & (meta.risk == 0))
    ax[2, 1].bar(t, (p2lt[:,0] + p2lt[:,1] + p2lt[:,2] + p2lt[:,3] + p2lt[:,4])/n_g, color = "navy", width = 1)
    ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2] + p2lt[:,3] + p2lt[:,4])/n_g, color = "darkred", width = 1)
    ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2] + p2lt[:,3])/n_g, color = "red", width = 1)
    ax[2, 1].bar(t, (p2lt[:,1] + p2lt[:,2])/n_g, color = "darkgreen", width = 1)
    ax[2, 1].bar(t, p2lt[:,1]/n_g, color = "green", width = 1)
    ax[2, 1].set_xlim([0, n_days])
    ax[2, 1].set_ylim([0, 1])
    ax[2, 1].set_xlabel("Time (days)")


    # Graph of partnershipd in high risk 30 or older
    n_g = sum((meta.age_group == 3) & (meta.risk == 1))
    ax[3, 0].bar(t, (p3ht[:,0] + p3ht[:,1] + p3ht[:,2] + p3ht[:,3] + p3ht[:,4])/n_g, label = "Single", color = "navy", width = 1)
    ax[3, 0].bar(t, (p3ht[:,1] + p3ht[:,2] + p3ht[:,3] + p3ht[:,4])/n_g, label = "Short-term concurrent", color = "darkred", width = 1)
    ax[3, 0].bar(t, (p3ht[:,1] + p3ht[:,2] + p3ht[:,3])/n_g, label = "Short-term", color = "red", width = 1)
    ax[3, 0].bar(t, (p3ht[:,1] + p3ht[:,2])/n_g, label = "Long-term concurrent", color = "darkgreen", width = 1)
    ax[3, 0].bar(t, p3ht[:,1]/n_g, label = "Long-term", color = "green", width = 1)
    ax[3, 0].legend(loc = "lower left", bbox_to_anchor=(0.18,-0.05), bbox_transform=fig.transFigure, ncol=3)
    ax[3, 0].set_xlim([0, n_days])
    ax[3, 0].set_ylabel("Age Over 29")
    ax[3, 0].set_xlabel("Time (days)")
    ax[3, 0].set_ylim([0, 1])


    # Graph of partnershipd in low risk 30 or older
    n_g = sum((meta.age_group == 3) & (meta.risk == 0))
    ax[3, 1].bar(t, (p3lt[:,0] + p3lt[:,1] + p3lt[:,2] + p3lt[:,3] + p3lt[:,4])/n_g, color = "navy", width = 1)
    ax[3, 1].bar(t, (p3lt[:,1] + p3lt[:,2] + p3lt[:,3] + p3lt[:,4])/n_g, color = "darkred", width = 1)
    ax[3, 1].bar(t, (p3lt[:,1] + p3lt[:,2] + p3lt[:,3])/n_g, color = "red", width = 1)
    ax[3, 1].bar(t, (p3lt[:,1] + p3lt[:,2])/n_g, color = "darkgreen", width = 1)
    ax[3, 1].bar(t, p3lt[:,1]/n_g, color = "green", width = 1)
    ax[3, 1].set_xlim([0, n_days])
    ax[3, 1].set_ylim([0, 1])
    ax[3, 1].set_xlabel("Time (days)")


    # Save graph
    plt.savefig(save_dir + "_timeseries.pdf")
    plt.close()
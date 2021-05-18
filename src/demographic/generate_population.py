# -*- coding: utf-8 -*-
"""
CODE FOR DOING ALL THE DEMOGRAPHIC STUFF

Created on Mon Mar 15 11:04:41 2021

@author: nicol
"""


#%%  Setup Libraries


# Load libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# Read in parameters
sim_parameters = pd.read_csv("data/param.csv")
scenario_global = sim_parameters.scenario[0]


#%% FUN setup_data()
def setup_data(scenario = scenario_global, run_mode = 'serial'):


    # What doing
    ( print('Parsing demographic attributes for scenario ' + str(scenario) + '.\n') if run_mode == 'serial' else [] )


    # Load distribution of community size
    size = pd.read_csv("data/scenarios.csv")
    size = size.loc[size["scenario_num"] == scenario,]
    n = size.scenario_use.iloc[0]


    # Load distribution of sex
    sex_dist = pd.read_csv("data/sex_distributions.csv")
    sex_dist = sex_dist.loc[sex_dist["scenario"] == scenario,]


    # Load distribution of age
    age_dist = pd.read_csv("data/age_distributions.csv")
    age_dist = age_dist.loc[age_dist["scenario"] == scenario,]


    # Convert sex from M/F to 1/0
    age_dist.loc[age_dist.sex == 'M', 'sex'] = 1
    age_dist.loc[age_dist.sex == 'F', 'sex'] = 0


    # Modify age distribution to agree with the age bounds 16 and 35
    age_dist = age_dist.loc[age_dist.age_lower >= 15,:]
    age_dist = age_dist.loc[age_dist.age_lower <= 35,:]
    age_dist.loc[age_dist.age_lower == 15, 'ave'] = (4/5) * age_dist.loc[age_dist.age_lower == 15, 'ave']
    age_dist.loc[age_dist.age_lower == 35, 'ave'] = (1/5) * age_dist.loc[age_dist.age_lower == 35, 'ave']


    # Renormalise age distribution
    age_dist.loc[age_dist.sex == 1, 'ave'] = (1/np.sum(age_dist.loc[age_dist.sex == 1, 'ave'])) * age_dist.loc[age_dist.sex == 1, 'ave']
    age_dist.loc[age_dist.sex == 0, 'ave'] = (1/np.sum(age_dist.loc[age_dist.sex == 0, 'ave'])) * age_dist.loc[age_dist.sex == 0, 'ave']


    # Modify the quoted upper and lower bounds
    age_dist.loc[age_dist.age_lower == 15, 'age_lower'] = 16
    age_dist.loc[:, 'age_upper'] = age_dist.loc[:, 'age_upper'] + 1
    age_dist.loc[age_dist.age_upper == 40, 'age_upper'] = 36


    # Compute the CDF for the age distribution
    age_dist.loc[:, 'cdf'] = np.cumsum(age_dist.ave)
    age_dist.loc[age_dist.sex == 1, 'cdf'] = age_dist.loc[age_dist.sex == 1, 'cdf'] - 1


    # Load distribution of sexual orientation
    orientation_dist = pd.read_csv("data/orientation_distribution.csv")


    # Load distribution of number of sexual partners
    # partners_dist = pd.read_csv("data/partners_distribution_DELETE_THIS.csv")
    partners_dist = pd.read_csv("data/calibration_partnership_rates.csv")


    # Store all population data in a big dictionary
    pop_parameters = {'scenario': scenario,
                      'size': size,
                      'n': n,
                      'sex_dist': sex_dist,
                      'age_dist': age_dist,
                      'orientation_dist': orientation_dist,
                      'partners_dist': partners_dist}


    # Return the data
    return pop_parameters


#%% FUN generate_population()
def generate_population(pop_parameters, n_generate = 'initilise', prop_infected = sim_parameters.init_prob_exposed[0]):


    # Setup demographic data
    # size = pop_parameters['size']
    sex_dist = pop_parameters['sex_dist']
    age_dist = pop_parameters['age_dist']
    orientation_dist = pop_parameters['orientation_dist']
    partners_dist = pop_parameters['partners_dist']


    # Switch to just generating one new individual if this is an importation event
    n = pop_parameters['n'] if n_generate == 'initilise' else int(n_generate)


    #%% Initilise meta data.frame


    # Initilise data.frame containing attributes of the population
    meta = pd.DataFrame(columns = ["gender",               # Binary 0/1 are they male
                                   "age",                  # Age of the individual
                                   "age_group",            # Age group (16-19, 20-24, 25-29, 30-36)
                                   "orientation",          # Sexual orientation
                                   "risk",                 # Infection risk level
                                   "partner",              # The indivdual's long-term partner
                                   "counter",              # Counter of how many partners they've had
                                   "state",                # Their current infection state (S,I,R)
                                   "site0",                # Binary 0/1 are they infected at anatomical site 0
                                   "site1",                # Binary 0/1 are they infected at anatomical site 1
                                   "site2",                # Binary 0/1 are they infected at anatomical site 2
                                   "site0_t0",             # The simulation time that they became infected at site 0
                                   "site1_t0",             # The simulation time that they became infected at site 1
                                   "site2_t0",             # The simulation time that they became infected at site 0
                                   "site0_t1",             # The simulation time that they recover at site 0
                                   "site1_t1",             # The simulation time that they recover at site 1
                                   "site2_t1",             # The simulation time that they recover at site 2
                                   "treatment_threshold",  # Threshold in [0,1] indicating when they'll get treatment
                                   "recovery_time"])       # Simulation time that they get treatment


    # Set variable types
    meta.gender.astype("int64")
    meta.age.astype("float64")
    meta.age_group.astype("int64")
    meta.orientation.astype("int64")
    meta.risk.astype("int64")
    meta.partner.astype("int64")
    meta.counter.astype("int64")
    meta.state.astype("category")
    meta.site0.astype("int64")
    meta.site1.astype("int64")
    meta.site2.astype("int64")
    meta.site0_t0.astype("float64")
    meta.site1_t0.astype("float64")
    meta.site2_t0.astype("float64")
    meta.site0_t1.astype("float64")
    meta.site1_t1.astype("float64")
    meta.site2_t1.astype("float64")
    meta.treatment_threshold.astype("float64")
    meta.recovery_time.astype("float64")


    # Set default values for the counter columns used for diagnostics
    meta.partner = n * [-1]
    meta.counter = n * [0]


    #%% Set age and gender attributes


    # Gender
    meta.loc[:,'gender'] = np.random.random(n)
    meta.loc[meta.gender < sex_dist.pMale.iloc[0], 'gender'] = 1
    meta.loc[meta.gender < 1, 'gender'] = 0


    # Simulate random numbers for age
    meta.loc[:, 'age'] = np.random.random(n)


    # Convert random numbers to age
    for i in range(0, n):


        # Work out which age group they're in
        group = np.min(np.where((age_dist.sex == meta.gender[i]) & (age_dist.cdf > meta.age[i])))


        # Now choose their age
        meta.loc[i, 'age'] = age_dist.age_lower.iloc[group] + (age_dist.age_upper.iloc[group] - age_dist.age_lower.iloc[group]) * np.random.random(1)


        # Set their age group
        meta.loc[i, 'age_group'] = int((age_dist.age_upper.iloc[group] - 19)/5)


    # Just check to make sure that there's somebody in the last age group
    # when generating a full sized dataset
    if n_generate == 'initilise':
        n_oldest = sum(meta.age_group == 4)
        if n_oldest == 0:


            # If not, pick somebody at random and put them into that age group
            i = round(n * np.random.random(1)[0])
            meta.loc[i, 'age'] = 35.5
            meta.loc[i, 'age_group'] = 4


    # Lump the 4th age group (35-39) in with the 3rd age group (30-34) anyway
    meta.loc[meta.age_group == 4, 'age_group'] = 3


    #%% Set sexual orientation


    # Simulate random numbers for orientation
    meta.loc[:, 'orientation'] = np.random.random(n)


    # Set orientation
    for i in range(0, n):


        # Work out their orientation
        meta.loc[i, 'orientation'] = np.min(np.where(orientation_dist.loc[meta.age_group.iloc[i], ['hetero', 'homo', 'bi']].to_numpy() > meta.orientation[i]))


    #%% Set infection-risk


    # Simulate some random numbers
    meta.loc[:, 'risk'] = np.random.random(n)


    # Set orientation
    for i in range(0, n):


        # Work out their orientation
        # meta.loc[i, 'risk'] = int(meta.risk[i] < partners_dist.loc[meta.age_group.iloc[i], ['more']].to_numpy())
        meta.loc[i, 'risk'] = int(meta.risk[i] < partners_dist.iloc[3, meta.age_group.iloc[i]])



    #%% Initilise infections


    # Set default values
    meta.state = n * ["S"]
    meta.site0 = n * [0]
    meta.site1 = n * [0]
    meta.site2 = n * [0]
    meta.site0_t0 = n * [float("inf")]
    meta.site1_t0 = n * [float("inf")]
    meta.site2_t0 = n * [float("inf")]
    meta.site0_t1 = n * [float("inf")]
    meta.site1_t1 = n * [float("inf")]
    meta.site2_t1 = n * [float("inf")]
    meta.treatment_threshold = np.random.random(n)
    meta.recovery_time = n * [float("inf")]


    # Seed some infections
    for i in range(0, n):


        # Set infection rate to 90% of the population
        if np.random.random() < prop_infected:


            # Set as exposed
            meta.at[i, "state"] = "E"


            # Choose one or more site to infect
            u = np.cumsum(np.random.random(3))
            u = np.min(np.where(u/u[2] > np.random.random()))
            meta.at[i, "site" + str(u) + "_t0"] = sim_parameters.partner_burn_in[0] + sim_parameters.init_duration_exposed[0] * np.random.random(1)


    # End it
    return meta



#%% FUN initilise_partner_matrix()
def initilise_partner_matrix(pop_parameters):
    out = np.zeros((pop_parameters['n'], pop_parameters['n']))
    return out


#%% FUN initilise_partner_durations()
def initilise_partner_duration(pop_parameters):
    out =  float("inf") * np.ones((pop_parameters['n'], pop_parameters['n']))
    return out


#%% FUN graph_population()
def graph_population(pop_parameters, meta, save_dir):


    # Setup demographic data
    n = pop_parameters['n']
    sex_dist = pop_parameters['sex_dist']
    age_dist = pop_parameters['age_dist']
    orientation_dist = pop_parameters['orientation_dist']
    partners_dist = pop_parameters['partners_dist']


    #%% Sex


    # Sex distribution
    simulated = [np.sum( (meta.gender == 1) ), np.sum( (meta.gender == 0) )]
    target = [n * sex_dist.pMale.iloc[0], n * (1 - sex_dist.pMale.iloc[0])]
    labels = ['Males', 'Females']
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x-width/2, simulated, width, label = "Simulated")
    ax.bar(x+width/2, target, width, label = "Target")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.set_ylabel('Number of Individuals')
    ax.set_title('Sex Distribution: Simulated vs. Target')
    ax.legend()
    plt.savefig(save_dir + '_sex.png', bbox_inches='tight')
    plt.close()
    #plt.show()


    #%% Sexual orientation by age group


    # Setup the simulated data
    meta.loc[meta.age > 35, 'age_group'] = 4
    counted = meta.pivot_table(index='age_group', columns='orientation', fill_value=0, aggfunc='count')['age'].unstack()
    hetero = counted[0]
    homo = counted[1]
    bi = counted[2]
    labels = ['[16, 20)', '[20, 25)', '[25, 30)', '[30, 35)', '[35, 36)']
    x = np.arange(len(labels))

    # Setup the target data
    target_dist = orientation_dist.append(orientation_dist.loc[3,:], ignore_index=True)
    target_dist.age_group.iloc[4] = 4
    target_dist.bi = target_dist.bi - target_dist.homo
    target_dist.homo = target_dist.homo - target_dist.hetero
    target_dist.loc[0,:] = n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[5] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[0]) * target_dist.loc[0,:]
    target_dist.loc[1,:] = n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[6] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[1]) * target_dist.loc[1,:]
    target_dist.loc[2,:] = n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[7] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[2]) * target_dist.loc[2,:]
    target_dist.loc[3,:] = n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[8] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[3]) * target_dist.loc[3,:]
    target_dist.loc[4,:] = n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[9] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[4]) * target_dist.loc[4,:]


    # Make figure
    fig, ax = plt.subplots()
    ax.bar(x-width/2, bi, width, label = 'Simulated', color = 'tab:green')
    ax.bar(x-width/2, homo, width, bottom = bi, label = 'Simulated', color = 'tab:orange')
    ax.bar(x-width/2, hetero, width, bottom = bi + homo, label = 'Simulated', color = 'tab:blue')
    ax.bar(x+width/2, target_dist.bi, width, label = 'Target', color = 'tab:green', alpha = 0.6)
    ax.bar(x+width/2, target_dist.homo, width, bottom = target_dist.bi, label = 'Target', color = 'tab:orange', alpha = 0.6)
    ax.bar(x+width/2, target_dist.hetero, width, bottom = target_dist.bi + target_dist.homo, label = 'Target', color = 'tab:blue', alpha = 0.6)

    ax.set_xlabel('Age Group')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Number of Individuals')
    # ax.set_title('Distribution of Age by Sexual Orientation: Simulated (left) vs Target (right)')
    ax.legend(handles = [mpatches.Patch(color='tab:blue', label = "Heterosexual"),
                         mpatches.Patch(color='tab:orange', label = "Homosexual"),
                         mpatches.Patch(color='tab:green', label = "Bisexual")])
    plt.savefig(save_dir + '_age_and_orientation.png', bbox_inches='tight')
    plt.close()
    #plt.show()


    #%% Risk level by age group

    counted = meta.pivot_table(index='age_group', columns='risk', fill_value=0, aggfunc='count')['age'].unstack()
    low = counted[0]
    high = counted[1]


    # Setup the simulated data
    #low = meta.loc[meta.risk == 0, :]. groupby('age_group')['age_group'].count()
    #high = meta.loc[meta.risk == 1, :]. groupby('age_group')['age_group'].count()
    labels = ['[16, 20)', '[20, 25)', '[25, 30)', '[30, 35)', '[35, 36)']
    x = np.arange(len(labels))


    # Setup for working out the partners_dist target
    risk = partners_dist.iloc[3, :]


    # Setup the target data
    target_dist = partners_dist.append(partners_dist.loc[3,:], ignore_index=True)
    target_high = [n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[5] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[0]) * risk[0],
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[6] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[1]) * risk[1],
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[7] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[2]) * risk[2],
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[8] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[3]) * risk[3],
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[9] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[4]) * risk[3]]
    target_low =  [n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[5] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[0]) * (1-risk[0]),
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[6] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[1]) * (1-risk[1]),
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[7] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[2]) * (1-risk[2]),
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[8] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[3]) * (1-risk[3]),
                   n * (sex_dist.pMale.iloc[0] * age_dist.ave.iloc[9] + (1-sex_dist.pMale.iloc[0]) * age_dist.ave.iloc[4]) * (1-risk[3])]


    # Make figure
    fig, ax = plt.subplots()
    ax.bar(x-width/2, high, width, label = 'Simulated', color = 'tab:orange')
    ax.bar(x-width/2, low, width, bottom = high, label = 'Simulated', color = 'tab:blue')
    ax.bar(x+width/2, target_high, width, label = 'Target', color = 'tab:orange', alpha = 0.6)
    ax.bar(x+width/2, target_low, width, bottom = target_high, label = 'Target', color = 'tab:blue', alpha = 0.6)

    ax.set_xlabel('Age Group')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Number of Individuals')
    # ax.set_title('Distribution of Age by Sexual Orientation: Simulated (left) vs Target (right)')
    ax.legend(handles = [mpatches.Patch(color='tab:blue', label = "Low Infection-risk"),
                         mpatches.Patch(color='tab:orange', label = "High Infection-risk")])
    plt.savefig(save_dir + '_age_and_risk.png', bbox_inches='tight')
    plt.close()
    #plt.show()













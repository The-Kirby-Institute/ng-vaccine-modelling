library(tidyverse)
library(stringr)
library(reticulate)
library(viridis)
library(epiR)
np = import('numpy')


########################################
##  READ IN RESULTS FROM SIMULATIONS  ##
########################################


# Read in all parameter sets
data = 
  read.csv('simulations/parameters.csv') %>%
  as_tibble()


# Read in the target prevalence
target = 
  read.csv('data/calibration_prevalence.csv') %>%
  as_tibble()


# Initilise columns for computing prevalence
data = 
  data %>%
  mutate(set = 0:999,
         prev_tot = NA,
         prev_m = NA,
         prev_f = NA,
         prev_m0 = NA,
         prev_m1 = NA,
         prev_m2 = NA,
         prev_m3 = NA,
         prev_f0 = NA,
         prev_f1 = NA,
         prev_f2 = NA,
         prev_f3 = NA)


# Read in data and determine the equilibrium point
scenario = 1
for (i in 0:999){
  print(i)
  
  
  # Load prevalence data
  file_name = str_c('simulations/prevalence/scenario_', scenario, '/data', i, '.npy')
  if ( file.exists(file_name) ){
    prev = np$load(file_name) %>% as_tibble()
    names(prev) = c('tot', 'm', 'f', 'm0', 'm1', 'm2', 'm3', 'm4', 'f0', 'f1', 'f2', 'f3', 'f4')
    
    
    # Compute the average prevalence
    prev = prev[2000:nrow(prev),]
    data$prev_tot[i+1] = mean(prev$tot)
    data$prev_m[i+1] = mean(prev$m)
    data$prev_f[i+1] = mean(prev$f)
    data$prev_m0[i+1] = mean(prev$m0)
    data$prev_m1[i+1] = mean(prev$m1)
    data$prev_m2[i+1] = mean(prev$m2)
    data$prev_m3[i+1] = mean(prev$m3)
    data$prev_f0[i+1] = mean(prev$f0)
    data$prev_f1[i+1] = mean(prev$f1)
    data$prev_f2[i+1] = mean(prev$f2)
    data$prev_f3[i+1] = mean(prev$f3)
  }
}


# Summary of overall prevalence
data %>%
  ggplot(aes(x=prev_tot)) +
  geom_histogram(bins = 20)


############################
##  SENSITIVITY ANALYSIS  ##
############################


# Compute correlation with different variables
x = data %>% filter(!is.na(prev_tot)) %>% select(-starts_with('prev'), -starts_with('mean'), -set)
y = data %>% filter(!is.na(prev_tot)) %>% select(starts_with('prev'))
out = tibble(var = names(x), 
             cor_tot = NA,
             cor_m = NA,
             cor_f = NA,
             cor_m0 = NA,
             cor_m1 = NA,
             cor_m2 = NA,
             cor_m3 = NA,
             cor_f0 = NA,
             cor_f1 = NA,
             cor_f2 = NA,
             cor_f3 = NA)
compute_cor = function(x, y){
  out = epi.prcc(tibble(x, y))
  return(out$est)
}
for ( i in 1:ncol(x) ){
  if( !all(is.na(x[,i])) ){
    x[,i] = x[,i] - mean(data.matrix(x[,i]), na.rm = T)
    x[,i] = x[,i]/sqrt(var(data.matrix(x[,i]), na.rm = T))
    out$cor_tot[i] = compute_cor(x[,i], y[,1])
    out$cor_m[i] = compute_cor(x[,i], y[,2])
    out$cor_f[i] = compute_cor(x[,i], y[,3])
    out$cor_m0[i] = compute_cor(x[,i], y[,4])
    out$cor_m1[i] = compute_cor(x[,i], y[,5])
    out$cor_m2[i] = compute_cor(x[,i], y[,6])
    out$cor_m3[i] = compute_cor(x[,i], y[,7])
    out$cor_f0[i] = compute_cor(x[,i], y[,8])
    out$cor_f1[i] = compute_cor(x[,i], y[,9])
    out$cor_f2[i] = compute_cor(x[,i], y[,10])
    out$cor_f3[i] = compute_cor(x[,i], y[,11])
  }
}


# Plot the correlation for each prevalence type
out %>%
  mutate(var = case_when(var == 'pup' ~ 'trans_prob_ural_phar',
                         var == 'ppp' ~ 'trans_prob_phar_phar',
                         var == 'pru' ~ 'trans_prob_rect_ural',
                         var == 'ppu' ~ 'trans_prob_phar_ural',
                         var == 'pur' ~ 'trans_prob_ural_rect',
                         var == 'prp' ~ 'trans_prob_rect_phar',
                         var == 'ppr' ~ 'trans_prob_phar_rect',
                         var == 'puu' ~ 'trans_prob_ural_ural',
                         var == 'p_anal_MM' ~ 'prob_anal_M2M',
                         var == 'p_sex_MM' ~ 'prob_sex_M2M',
                         var == 'p_rim' ~ 'prob_rim',
                         var == 'p_kiss' ~ 'prob_kiss',
                         var == 'p_oral_MM' ~ 'prob_oral_M2M',
                         var == 'p_oral_MF' ~ 'prob_oral_M2F',
                         var == 'p_oral_FM' ~ 'prob_oral_F2M',
                         var == 'p_oral_FF' ~ 'prob_oral_F2F',
                         var == 'p_sex_MF' ~ 'prob_sex_M2F',
                         var == 'p_anal_MF' ~ 'prob_anal_M2F',
                         var == 'p_sex_FF' ~ 'prob_sex_F2F',
                         T ~ var),
         var = reorder(var, cor_tot)) %>%
  gather(type, val, -var) %>%
  mutate(type = ordered(type, 
                        levels=c('cor_tot', 'cor_m', 'cor_f', 'cor_m0', 'cor_m1', 'cor_m2', 'cor_m3', 'cor_f0', 'cor_f1', 'cor_f2', 'cor_f3'),
                        labels=c('Overall', 'Males', 'Females', 'Male 16-19', 'Male 20-24', 'Male 25-29', 'Male 30-35', 'Female 16-19', 'Female 20-24', 'Female 25-29', 'Female 30-35')),
         val = case_when(val > 0.2 ~ 0.2,
                         val > 0.1 ~ 0.1,
                         val > 0 ~ 0,
                         val > -0.1 ~ -0.1,
                         val > -0.2 ~ -0.2,
                         val > -0.3 ~ -0.3,
                         val > -0.4 ~ -0.4,
                         val > -0.5 ~ -0.5,
                         val > -0.6 ~ -0.6,
                         val > -0.7 ~ -0.7)) %>%
  filter(!is.na(val)) %>%
  ggplot(aes(x=type, y=var, fill=as.factor(val))) +
  geom_tile() +
  scale_fill_viridis_d() +
  labs(y = 'Parameters being calibrated',
       x = 'Prevalence Category',
       title = 'Partial-rank Correlation Coefficient Between Prevalence Parameters',
       fill = 'Correlation') +
  theme(axis.text.x = element_text(angle = -30, hjust = 0.1))


################################
##  FIND THE BEST PARAMETERS  ##
################################


# Compute how good each parameter set is
data = 
  data %>%
  mutate(mean_ss = (1/11)*((prev_tot - target$tot)^2 +
                          (prev_m - target$m)^2 +
                          (prev_f - target$f)^2 +
                          (prev_m0 - target$m0)^2 +
                          (prev_m1 - target$m1)^2 +
                          (prev_m2 - target$m2)^2 +
                          (prev_m3 - target$m3)^2 +
                          (prev_f0 - target$f0)^2 +
                          (prev_f1 - target$f1)^2 +
                          (prev_f2 - target$f2)^2 +
                          (prev_f3 - target$f3)^2))


# Make a graph
data %>%
  filter(!is.na(mean_ss)) %>%
  ggplot(aes(x=mean_ss)) +
  geom_histogram(bins = 40) +
  labs(x = 'Mean Residual Sum of Squares Across Prevalence Categories',
       y = 'Count',
       title = 'Distribution of the Goodness of Fit for all Simulations')


# Pull out the best 50
calibrated = 
  data %>%
  arrange(mean_ss) %>%
  slice_head(n = 50)
write.csv(calibrated, str_c('simulations/calibrated_scenario_', scenario, '.csv'), row.names = F)


###################################################
##  DISTRIBUTION OF THE BEST PREVALENCE RESULTS  ##
###################################################
# Look at the distribution of prevalence for the top 50


# Preallocate
prev_overall = array(0, c(1651, 50))
prev_m = array(0, c(1651, 50))
prev_f = array(0, c(1651, 50))


# Read in data and determine the equilibrium point
scenario = 1
for (j in 1:50){
  i = calibrated$set[j]
  print(j)
  
  
  # Load prevalence data
  file_name = str_c('simulations/prevalence/scenario_', scenario, '/data', i, '.npy')
  if ( file.exists(file_name) ){
    prev = np$load(file_name) %>% as_tibble()
    names(prev) = c('tot', 'm', 'f', 'm0', 'm1', 'm2', 'm3', 'm4', 'f0', 'f1', 'f2', 'f3', 'f4')
    prev = prev[2000:nrow(prev),]

    
    # Compute the average prevalence
    prev_overall[,j] = prev$tot
    prev_m[,j] = prev$m
    prev_f[,j] = prev$f
  }
}


# Plot Overall
row_mean = rowMeans(prev_overall)
prev_overall %>%
  as_tibble() %>%
  mutate(t = 1:nrow(prev_overall),
         row_mean = row_mean) %>%
  gather(sim, val, -t, -row_mean) %>%
  mutate(sim = as.factor(str_extract(sim, '[0-9]+'))) %>%
  ggplot(aes(x=t)) +
  geom_line(aes(y=val, group=sim), alpha = 0.1) +
  geom_line(aes(y=row_mean), colour = 'red') +
  geom_hline(aes(yintercept = target$tot), lty = 'dashed') +
  scale_x_continuous(expand = c(0, 0)) +
  labs(x = 'Days from 2000th time step',
       y = 'Prevalence',
       title = 'Comparison Rolling Mean of Overall Simulated Prevalence to Overall STRIVE Prevalence')


# Plot Male
row_mean = rowMeans(prev_m)
prev_m %>%
  as_tibble() %>%
  mutate(t = 1:nrow(prev_m),
         row_mean = row_mean) %>%
  gather(sim, val, -t, -row_mean) %>%
  mutate(sim = as.factor(str_extract(sim, '[0-9]+'))) %>%
  ggplot(aes(x=t)) +
  geom_line(aes(y=val, group=sim), alpha = 0.1) +
  geom_line(aes(y=row_mean), colour = 'red') +
  geom_hline(aes(yintercept = target$m), lty = 'dashed') +
  scale_x_continuous(expand = c(0, 0)) +
  labs(x = 'Days from 2000th time step',
       y = 'Prevalence',
       title = 'Comparison Rolling Mean of Male Simulated Prevalence to Male STRIVE Prevalence')


# Plot Female
row_mean = rowMeans(prev_f)
col_mean = mean(colMeans(prev_f))
prev_f %>%
  as_tibble() %>%
  mutate(t = 1:nrow(prev_f),
         row_mean = row_mean) %>%
  gather(sim, val, -t, -row_mean) %>%
  mutate(sim = as.factor(str_extract(sim, '[0-9]+'))) %>%
  ggplot(aes(x=t)) +
  geom_line(aes(y=val, group=sim), alpha = 0.1) +
  geom_line(aes(y=row_mean), colour = 'red') +
  geom_hline(aes(yintercept = target$f), lty = 'dashed') +
  scale_x_continuous(expand = c(0, 0)) +
  labs(x = 'Days from 2000th time step',
       y = 'Prevalence',
       title = 'Comparison Rolling Mean of Female Simulated Prevalence to Female STRIVE Prevalence')


##############################################
##  PLOT THE DISTRIBUTION OF THE BEST FITS  ##
##############################################


# Compute how good each parameter set is
data %>%
  filter(!is.na(prev_tot)) %>%
  mutate(prev_tot = prev_tot - target$tot,
         prev_m = prev_m - target$m,
         prev_f = prev_f - target$f,
         prev_m0 = prev_m0 - target$m0,
         prev_m1 = prev_m1 - target$m1,
         prev_m2 = prev_m2 - target$m2,
         prev_m3 = prev_m3 - target$m3,
         prev_f0 = prev_f0 - target$f0,
         prev_f1 = prev_f1 - target$f1,
         prev_f2 = prev_f2 - target$f2,
         prev_f3 = prev_f3 - target$f3,
         chosen = case_when(set %in% calibrated$set ~ T, T ~ F)) %>%
  select(chosen, starts_with('prev')) %>%
  gather(case, val, -chosen) %>%
  mutate(cases = as.factor(case),
         case = ordered(case, 
                        levels=c('prev_tot', 'prev_m', 'prev_f', 'prev_m0', 'prev_m1', 'prev_m2', 'prev_m3', 'prev_f0', 'prev_f1', 'prev_f2', 'prev_f3'),
                        labels=c('Overall', 'Males', 'Females', 'Male 16-19', 'Male 20-24', 'Male 25-29', 'Male 30-35', 'Female 16-19', 'Female 20-24', 'Female 25-29', 'Female 30-35'))) %>%
  ggplot(aes(fill = chosen, x = val)) +
  geom_vline(aes(xintercept = 0), lty = 'dashed') +
  geom_density(alpha = 0.6) + 
  facet_wrap(~case) +
  labs(x = 'Distribution of Difference Between Simulated and STRIVE Prevalence',
       y = 'Density',
       title = 'Analysis of Systematic Bias Within Prevalence Categories',
       fill = 'Is in top 50: ') +
  theme(legend.position = 'bottom')



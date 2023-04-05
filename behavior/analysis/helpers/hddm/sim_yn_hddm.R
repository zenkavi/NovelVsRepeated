#!/usr/bin/env Rscript

library(here)
library(optparse)
library(tidyverse)
library(RWiener)
set.seed(38992)

#######################
# Usage
#######################

# Rscript --vanilla sim_yn_hddm.R --cond HT --day 2 --subnum 601 --n_samples 10
# Rscript --vanilla sim_yn_hddm.R --cond RE --day 6 --subnum 619

#######################
# Parse input arguments
#######################
option_list = list(
  make_option("--cond", type="character"),
  make_option("--day", type="character"),
  make_option("--subnum", type="character"),
  make_option("--n_samples", default = 1000)
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

cur_sub = as.numeric(opt$subnum)
cur_cond = opt$cond
cur_day = as.numeric(opt$day)
n_samples = as.numeric(opt$n_samples)

#########################
# Read in stimuli and estimated parameter posteriors
#########################

helpers_path = here()

data_yn = read.csv(paste0(helpers_path, '/inputs/data_choiceYN.csv'))

data_yn_clean = data_yn %>%
  filter(session != -99) %>%
  select(-inizialTime, -inizialTimeResp, -endTime, -endTimeResp) %>%
  mutate(type = ifelse(type == 1, "HT", "RE"))

rm(data_yn)

fn = file.path(here(), "inputs",'yn_hddm_mcmc_draws.csv')

all_results_df = read.csv(fn)

#########################
# Define helper functions
#########################

sim_trial = function(trial_vdiff, sampled_sigma, sampled_d, sampled_ndt, sampled_bias){

  # Multiplying boundary separation and drift rate my sigma to account for that parameter
  trial_drift = sampled_sigma * (sampled_d * trial_vdiff)

  # brms::rwiener response levels: upper == 1; lower == 0
  # cur_pred = brms::rwiener(1, 2*sampled_sigma, sampled_ndt, sampled_bias, trial_drift)
  # RWiener::rwiener response levels: upper == 1; lower == 2

  if(abs(trial_drift) < 10){
    cur_pred = RWiener::rwiener(1, 2*sampled_sigma, sampled_ndt, sampled_bias, trial_drift)
  } else {
    print("d too large. Sampling RT.")
    pq = sampled_ndt + abs(rnorm(1, mean = 0, sd = 0.01))
    pr = ifelse(trial_drift>10, factor("upper", levels = c("upper", "lower")), factor("lower", levels = c("upper", "lower")))
    cur_pred = data.frame(q = pq, resp = pr)
  }


  return(cur_pred)

}

sim_subj_cond_day_once = function(cur_stims, sampled_sigma, sampled_d, sampled_ndt, sampled_bias){

  pred_data = cur_stims
  pred_data$sampled_sigma = sampled_sigma
  pred_data$sampled_d = sampled_d
  pred_data$sampled_ndt = sampled_ndt
  pred_data$sampled_bias = sampled_bias
  pred_data$pred_rt = NA
  pred_data$pred_yesChosen = NA

  for(i in 1:nrow(cur_stims)){

    trial_vdiff = cur_stims$possiblePayoff[i] - cur_stims$reference[i]
    cur_pred = sim_trial(trial_vdiff, sampled_sigma, sampled_d, sampled_ndt, sampled_bias)

    pred_data$pred_rt[i] = cur_pred$q
    pred_data$pred_yesChosen[i] = cur_pred$resp

  }

  return(pred_data)
}

sim_subj_cond_day_nsamples = function(n_samples, cur_sub, cur_type, cur_day){

  cur_cond_pars = all_results_df %>%
    filter(subnum == cur_sub & day == cur_day & type == cur_type)

  if(nrow(cur_cond_pars)/30000 != 4){
    print("Parameters not filtered correctly. Aborting...")
  } else {

    cur_stims = data_yn_clean %>%
      filter(subnum == cur_sub & day == cur_day & type == cur_type) %>%
      select(subnum, day, type, possiblePayoff, reference, yesChosen, rt)

    i = 0
    while(i < n_samples){

      sampled_pars = cur_cond_pars %>%
        group_by(par_name, type, day) %>%
        sample_n(1)

      print(sampled_pars)

      sampled_sigma = as.numeric(sampled_pars[sampled_pars$par_name == "sigma", 'estimate'])
      sampled_d = as.numeric(sampled_pars[sampled_pars$par_name == "d", 'estimate'])
      sampled_ndt = as.numeric(sampled_pars[sampled_pars$par_name == "ndt", 'estimate'])
      sampled_bias = as.numeric(sampled_pars[sampled_pars$par_name == "bias", 'estimate'])

      cur_pred = sim_subj_cond_day_once(cur_stims, sampled_sigma, sampled_d, sampled_ndt, sampled_bias)
      cur_pred$sample = i+1

      if(i == 0){
        pred_data = cur_pred
      } else{
        pred_data = rbind(pred_data, cur_pred)
      }

      # if (i %% 25 == 0){
      print(paste0("Iteration number ", i+1, " complete"))
      # }

      i = i+1
    }

    return(pred_data)
  }


}


#########################
# Simulate data using the true stimuli plugging in parameters sampled from the posteriors
#########################

pred_data = sim_subj_cond_day_nsamples(n_samples, cur_sub, cur_cond, cur_day)

#########################
# Save output
#########################

fn = file.path(here(), "inputs", paste0('yn_sim_hddm_sub-', cur_sub,'_', cur_cond, '_day-', cur_day, '.csv'))
write.csv(pred_data, fn, row.names = F)

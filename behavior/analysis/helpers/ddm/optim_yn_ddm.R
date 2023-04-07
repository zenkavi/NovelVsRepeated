#!/usr/bin/env Rscript

library(here)
library(optparse)
library(tidyverse)

# Note this will be run in docker container so /ddModels must be mounted
helpers_path = paste0(here(),'/analysis/helpers')
source(paste0(helpers_path,'fit_task.R'))


#######################
# Parse input arguments
#######################
option_list = list(
  make_option("--data", type="character", default='test_data/test_trial_conditions'),
  make_option("--start_vals", type="character"),
  make_option("--model", type="character", default = "yn_ddm"),
  make_option("--max_iter", type="integer", default = as.integer(500)),
  make_option("--par_names", type="character", default = c("d", "sigma", "nonDecisionTime", "bias", "barrierDecay")),
  make_option("--out_path", type="character", default = 'sim0')
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

#######################
# Initialize parameters from input arguments
#######################
data_suffix = opt$data

if(grepl('/', data_suffix)){
  tmp_split = strsplit(data_suffix, '/')
  p2 = tmp_split[[1]][2]
  if(grepl('_', tmp_split[[1]][1])){
  p1 = strsplit(tmp_split[[1]][1], '_')[[1]][3]
  data_suffix = paste0(p1, '_', p2)
  } else{
    data_suffix = p2
  }
}

#  WHERE SHOULD DATA BE PULLED FROM
data = read.csv(paste0(helpers_path, 'cluster_scripts/', opt$data, '.csv'))

# Convert to numeric so optim can work with it
start_vals = as.numeric(strsplit(opt$start_vals, ",")[[1]])

model = opt$model
source(paste0(helpers_path, model,'.R'))
sim_trial_list = list()
fit_trial_list = list()
sim_trial_list[[model]] = sim_trial
fit_trial_list[[model]] = fit_trial

max_iter = opt$max_iter

par_names = opt$par_names
# If using string input convert to vector
if(length(par_names) == 1){
  if(grepl(',', par_names)){
    par_names = gsub(" ", "", par_names) #remove spaces
    par_names = strsplit(par_names, ',')[[1]]
  }
}

# Must end with /
out_path = paste0(helpers_path, 'cluster_scripts/optim_out/',opt$out_path)

}

#######################
# Run optim
#######################

optim_out = optim_save(par = start_vals, get_task_nll, data_= data, par_names_ = par_names, model_name_ = model, fix_pars_ = fix_pars, control = list(maxit=max_iter))

optim_out$par = data.frame(vals = optim_out$par)
optim_out$par$par_names = par_names
optim_out$par = optim_out$par %>% spread(par_names, vals)
optim_out$par$loglik = optim_out$iterations_df$Result[nrow(optim_out$iterations_df)]

#######################
# Save output
#######################
suffix = paste(format(Sys.time(), "%F-%H-%M-%S"), round(runif(1, max=1000)), sep="_")
suffix = paste0(model ,'_', data_suffix, '_', suffix, '.csv')

dir.create(out_path, showWarnings = FALSE)

write.csv(optim_out$par, paste0(out_path, '/optim_par_', suffix), row.names=FALSE)

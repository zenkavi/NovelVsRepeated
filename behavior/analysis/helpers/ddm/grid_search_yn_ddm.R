#!/usr/bin/env Rscript

library(optparse)
library(tidyverse)

# Note this will be run in docker container so make sure paths are mounted and defined in the env
input_path = Sys.getenv("INPUT_PATH")
code_path = Sys.getenv("CODE_PATH")
output_path = Sys.getenv("OUT_PATH")

source(file.path(code_path,'fit_yn_ddm.R'))

#######################
# Parse input arguments
#######################
option_list = list(
  make_option("--data", type="character", default='data_choiceYN.csv'),
  make_option("--subnum", type="integer"),
  make_option("--day", type="integer"),
  make_option("--type", type="character"),
  make_option("--model", type="character", default = "yn_ddm"),
  make_option("--grid", type="character", default='ddm_grid.csv'),
  make_option("--out_path", type="character", default = output_path)
)

opt_parser = OptionParser(option_list = option_list)
opt = parse_args(opt_parser)

#######################
# Initialize parameters from input arguments
#######################

#  WHERE SHOULD DATA BE PULLED FROM?
data = read.csv(file.path(input_path , opt$data))

cur_sub = as.numeric(opt$subnum)
cur_day = as.numeric(opt$day)
cur_type = opt$type

normMax = 1
normMin = -1

data = data %>%
  mutate(type = ifelse(type == 1, "HT", "RE")) %>%
  filter((subnum == cur_sub) & (day == cur_day) & (type == cur_type)) %>%
  filter(reference != -99) %>%
  filter(rt > .3 & rt < 5) %>%
  mutate(rawVDiff = possiblePayoff - reference,
         normVDiff =  (normMax - normMin) / (max(rawVDiff) - min(rawVDiff)) * (rawVDiff - max(rawVDiff)) + (normMax) )


model = opt$model
source(file.path(code_path, paste0(model, '.R')))
fit_trial_list = list()
fit_trial_list[[model]] = fit_trial


ddm_grid = read.csv(file.path(input_path, opt$grid))

par_names = names(ddm_grid)

# Must end with /
out_path = opt$out_path
# Make sure path exists
dir.create(out_path, showWarnings = FALSE)

#######################
# Run grid search
#######################

print(paste0("Starting grid search for sub-", cur_sub, ", day ", cur_day, ", type ", cur_type))
for(i in 1:nrow(ddm_grid)){

  print(paste0("Row num = ", i))

  par = as.numeric(ddm_grid[i,])
  gs_out = get_task_nll(par_ = par, data_= data, par_names_ = par_names, model_name_ = model)

  cur_out = tibble(key = par_names, value = par)
  cur_out = cur_out %>% spread(key, value)
  cur_out$nll = gs_out
  cur_out$subnum = cur_sub
  cur_out$day = cur_day
  cur_out$type = cur_type
  cur_out$model = model

  if(i == 1){
    out = cur_out
  } else{
    out = rbind(out, cur_out)
  }

  #######################
  # Save output (save for each start)
  #######################

  fn = paste0("grid_search_YN_DDM_FIT_sub-", cur_sub, "_", cur_type, "_day_", cur_day, ".csv")
  write.csv(out, file.path(out_path, fn), row.names = F)
}

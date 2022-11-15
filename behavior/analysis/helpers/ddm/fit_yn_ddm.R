#!/usr/bin/env Rscript

library(here)
library(optparse)
library(runjags)
library(tidyverse)
set.seed(38992)

#######################
# Usage
#######################

# Rscript --vanilla fit_yn_ddm.R --type HT --day 3
# Rscript --vanilla fit_yn_ddm.R --type HT --day 7
# Rscript --vanilla fit_yn_ddm.R --type HT --day 3

#######################
# Parse input arguments
#######################
option_list = list(
  make_option("--type", type="character"),
  make_option("--day", type="character")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

if(opt$type == "HT"){
  stim_type = 1
} else if (opt$type == "RE") {
  stim_type = 0
} else {
  stim_type = c(0,1)
}

if(opt$day == "all"){
  day_num = c(3, 7, 11)
} else{
  day_num = as.numeric(opt$day)
}

data <- read.csv(paste0(here(), '/inputs/data_choiceYN.csv'))
model_fn <- file.path(here(), "analysis/helpers/ddm/ddmHT_modelWIENER.txt")
out_path <- file.path(here(), "inputs")

stim_type_str = ifelse(length(stim_type) > 1, "both_types", ifelse(stim_type == 1, "HT", "RE"))
day_num_str = ifelse(length(day_num) > 1, "all_sessions", paste0("day_", day_num))
fn = paste0('YN_HDDM_FIT_', stim_type_str, '_', day_num_str)

#
# # # some data variables: # # #
#
# yesChosen -> 1 for yes, 0 for no
# possiblePayoff -> value of seem option
# rt -> reaction time in seconds
# trialNum -> trial number
# subnum -> subject number

### prepare data
# subject numbers
subjs <- unique(data$subnum)

# RT is positive if yes/stim chosen, negative if no/reference chosen
# data = data %>%
#   # scaling option values for subject specifically before filtering subjects by training type
#   group_by(subnum) %>%
#   mutate(possiblePayoffleft_std = possiblePayoffleft - mean(possiblePayoffleft),
#          possiblePayoffright_std = possiblePayoffright - mean(possiblePayoffright)) %>%
#   filter((typeLeft %in% stim_type) & (day %in% day_num)) %>% # Filter only relevant stimuli
#   group_by(subnum, day, trialNum, leftFix) %>%
#   summarise(.groups = 'keep',
#             fixDuration = sum(fixDuration),
#             rt = unique(rt),
#             leftval = unique(possiblePayoffleft_std),
#             rightval = unique(possiblePayoffright_std),
#             choice = unique(leftChosen)) %>%
#   mutate(leftFix = ifelse(leftFix == 1, "fixleft", "fixright")) %>%
#   spread(leftFix, fixDuration) %>%
#   mutate(fixleft = ifelse(is.na(fixleft), 0, fixleft),
#          fixright = ifelse(is.na(fixright), 0, fixright),
#          totfix = fixleft + fixright,
#          rtPN = ifelse(choice == 1, rt, (-1)*rt))

data = data %>%
  filter(reference != -99) %>%
  group_by(subnum) %>%
  mutate(possiblePayoff_std = possiblePayoff - mean(possiblePayoff)) %>%
  filter(day %in% day_num) %>%
  mutate(rtPN = ifelse(yesChosen == 1, rt, (-1)*rt))


#non decision time = rt - total fixation time
#data$ndt<- data$rt - data$totfix
# you can decide whether to fit the ndt or give it as input to the model

# NB BEFORE FITTING THE MODEL MAKE SURE YOU HAVE NO NAN or NA IN YOUR DATA

#--------------------------------#--------------------------------

idxP = as.numeric(ordered(data$subnum)) #makes a sequentially numbered subj index

v_stim = data$possiblePayoff_std
v_ref = data$reference

# proportion of fixations to the left option (nb. fixright = 1-gazeL)
# gazeL = data$fixleft/data$totfix

# rt to fit
y= data$rtPN

# number of trials
N = length(y)

# number of subjects
ns = length(unique(idxP))


#--------------------------------------------
# fit the model

# data
# dat <- dump.format(list(N=N, y=y, idxP=idxP, v_left=v_left,v_right=v_right, gazeL=gazeL, ns=ns))
dat <- dump.format(list(N=N, y=y, idxP=idxP, v_stim=v_stim, v_ref=v_ref, ns=ns))

# create random values for the inital values of noise mean and variance
alpha.mu1 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.mu2 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.mu3 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.si1 = as.vector(matrix(runif(1)*10, 1,1))
alpha.si2 = as.vector(matrix(runif(1)*10, 1,1))
alpha.si3 = as.vector(matrix(runif(1)*10, 1,1))


inits1 <- dump.format(list( alpha.mu=alpha.mu1, alpha.pr=alpha.si1,
                            ndt.mu=0.1, ndt.pr=0.5,  b.mu=0.2, b.pr=0.05, bias.mu=0.5, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Super-Duper", .RNG.seed=99999 ))

inits2 <- dump.format(list( alpha.mu=alpha.mu2, alpha.pr=alpha.si2,
                            ndt.mu=0.2, ndt.pr=0.5,  b.mu=1, b.pr=0.05, bias.mu=0.6, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Wichmann-Hill", .RNG.seed=1234))

inits3 <- dump.format(list( alpha.mu=alpha.mu3, alpha.pr=alpha.si3,
                            ndt.mu=0.15, ndt.pr=0.5,  b.mu=1.3, b.pr=0.05, bias.mu=0.4, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Mersenne-Twister", .RNG.seed=6666 ))

# parameters to monitor
monitor = c(
  "b.mu", "ndt.mu", "alpha.mu","bias.mu", "b.p",  "ndt.pr", "theta.p","alpha.p","bias","deviance" )

# run the fitting
results <- run.jags(model=model_fn, monitor=monitor, data=dat, n.chains=3, inits=c(inits1,inits2, inits3), plots = TRUE, method="parallel", module="wiener", burnin=50000, sample=10000, thin=10)


suuum<-summary(results)

save(results, file=file.path(out_path, paste0("results_", fn,".RData")) )
write.csv(suuum, file=file.path(out_path, paste0("summary_", fn ,".csv")) )


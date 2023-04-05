#!/usr/bin/env Rscript

library(here)
library(optparse)
library(runjags)
library(tidyverse)
set.seed(38752)

#######################
# Usage
#######################

# Rscript --vanilla fit_bc_haddm.R --type HT --day 3
# Rscript --vanilla fit_bc_haddm.R --type HT --day 7
# Rscript --vanilla fit_bc_haddm.R --type HT --day 3

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
} else {
  stim_type = 0
}

day_num = as.numeric(opt$day)


stim_type_str = opt$type
day_num_str = paste0("day_", day_num)
fn = paste0('BC_HaDDM_FIT_', stim_type_str, '_', day_num_str)

data <- read.csv(paste0(here(), '/inputs/data_fixBC.csv'))
model_fn <- file.path(here(), "analysis/helpers/haddm/bc_haddm_jags.txt")
out_path <- file.path(here(), "inputs")

#
# # # some data variables: # # #
#
# leftChosen -> 1 for left, 0 for right
# possiblePayoffleft -> value of left option
# possiblePayoffright -> value of right option
# rt -> reaction time in seconds
# fixNum -> fixation number
# fixDuration -> fixation duration in ms
# leftFix -> 1 for fixation on left option, 0 for fixation on right option
# trialNum -> trial number
# subnum -> subject number

### prepare data
# subject numbers
subjs <- unique(data$subnum)

# calculate total fixation duration, total fixation time to the left option and total fixation time to the right option
# RT is positive if left food item choosen, negative if right food item chosen
data = data %>%
  # scaling option values for subject specifically before filtering subjects by training type
  filter(rt < 5) %>% # discard very long RT trials
  group_by(subnum) %>%
  mutate(possiblePayoffleft_std = possiblePayoffleft - mean(possiblePayoffleft),
         possiblePayoffright_std = possiblePayoffright - mean(possiblePayoffright)) %>%
  filter((typeLeft %in% stim_type) & (day %in% day_num)) %>% # Filter only relevant stimuli
  group_by(subnum, day, trialNum, leftFix) %>%
  summarise(.groups = 'keep',
            fixDuration = sum(fixDuration),
            rt = unique(rt),
            leftval = unique(possiblePayoffleft_std),
            rightval = unique(possiblePayoffright_std),
            choice = unique(leftChosen)) %>%
  mutate(leftFix = ifelse(leftFix == 1, "fixleft", "fixright")) %>%
  spread(leftFix, fixDuration) %>%
  mutate(fixleft = ifelse(is.na(fixleft), 0, fixleft),
         fixright = ifelse(is.na(fixright), 0, fixright),
         totfix = fixleft + fixright,
         rtPN = ifelse(choice == 1, rt, (-1)*rt))


#non decision time = rt - total fixation time
#data$ndt<- data$rt - data$totfix
# you can decide whether to fit the ndt or give it as input to the model

# NB BEFORE FITTING THE MODEL MAKE SURE YOU HAVE NO NAN or NA IN YOUR DATA

#--------------------------------#--------------------------------

idxP = as.numeric(ordered(data$subnum)) #makes a sequentially numbered subj index

v_left = data$leftval
v_right = data$rightval

# proportion of fixations to the left option (nb. fixright = 1-gazeL)
gazeL = data$fixleft/data$totfix

# rt to fit
y= data$rtPN

# number of trials
N = length(y)

# number of subjects
ns = length(unique(idxP))


#--------------------------------------------
# fit the model

# data
dat <- dump.format(list(N=N, y=y, idxP=idxP, v_left=v_left,v_right=v_right, gazeL=gazeL, ns=ns))

# create random values for the inital values of noise mean and variance
alpha.mu1 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.mu2 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.mu3 = as.vector(matrix(1.3 + rnorm(1)*0.2,1,1))
alpha.si1 = as.vector(matrix(runif(1)*10, 1,1))
alpha.si2 = as.vector(matrix(runif(1)*10, 1,1))
alpha.si3 = as.vector(matrix(runif(1)*10, 1,1))


inits1 <- dump.format(list( alpha.mu=alpha.mu1, alpha.pr=alpha.si1,  thetaGaze.mu=0.6, thetaGaze.kappa=1,
                            ndt.mu=0.1, ndt.pr=0.5,  b.mu=0.2, b.pr=0.05, bias.mu=0.5, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Super-Duper", .RNG.seed=99999 ))

inits2 <- dump.format(list( alpha.mu=alpha.mu2, alpha.pr=alpha.si2,  thetaGaze.mu=0.5, thetaGaze.kappa=1,
                            ndt.mu=0.2, ndt.pr=0.5,  b.mu=1, b.pr=0.05, bias.mu=0.6, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Wichmann-Hill", .RNG.seed=1234))

inits3 <- dump.format(list( alpha.mu=alpha.mu3, alpha.pr=alpha.si3,  thetaGaze.mu=0.2, thetaGaze.kappa=1,
                            ndt.mu=0.15, ndt.pr=0.5,  b.mu=1.3, b.pr=0.05, bias.mu=0.4, bias.kappa=1,
                            y_pred=y, .RNG.name="base::Mersenne-Twister", .RNG.seed=6666 ))

# parameters to monitor
monitor = c(
  "b.mu", "ndt.mu", "alpha.mu","bias.mu", "thetaGaze.mu","thetaGaze", "b.p","thetaGaze.kappa",  "ndt.pr", "theta.p","alpha.p","bias","deviance" )

# run the fitting
results <- run.jags(model=model_fn, monitor=monitor, data=dat, n.chains=3, inits=c(inits1,inits2, inits3), plots = TRUE, method="parallel", module="wiener", burnin=50000, sample=10000, thin=10)


suuum<-summary(results)

save(results, file=file.path(out_path, paste0("results_", fn,".RData")) )
write.csv(suuum, file=file.path(out_path, paste0("summary_", fn ,".csv")) )

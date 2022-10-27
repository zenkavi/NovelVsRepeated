library(eyelinker)
library(tidyverse)
library(here)

raw_data_path = paste0(here(), '/inputs/raw_eyetracking')

helpers_path = paste0(here(),'/analysis/helpers/')
source(paste0(helpers_path, '01_clean_behavioral_data.R'))
rm(data_yn_clean)

data_bc_fmri = data_bc_clean %>%
  filter(fmri==1)
rm(data_bc_clean)

subnums = c("601", "609", "611", "619", "621", "629")
days = c("3", "7", "11")

data_fix_bc = data.frame()

for(i in 1:length(subnums)){
  for(j in 1:length(days)){
    cur_sub = subnums[i]
    cur_day = days[j]
    cur_fn = paste0(raw_data_path, '/Subj_', cur_sub, '/day_', cur_day, '/Es_5.asc')

    if(!file.exists(cur_fn)){
      print(paste0("Eyetracking data does not exist for Subj_", cur_sub, ' day_', cur_day))
      next
    }

    cur_choice_dat = data_bc_fmri %>%
      filter(as.character(subnum) == cur_sub & as.character(day) == cur_day) %>%
      mutate(trialNum = 1:n())

    cur_eye_dat = read.asc(cur_fn, samples = F)
    half_screen_width = cur_eye_dat$info$screen.x/2

    cur_fix = cur_eye_dat$fix

    cur_fix_clean = cur_fix %>%
      mutate(subnum = as.numeric(cur_sub),
             day = as.numeric(cur_day),
             trialNum = block - 1) %>%
      group_by(trialNum) %>%
      mutate(fixDuration = dur,
             leftFix = ifelse(axp < half_screen_width, 1, 0), #check if this is too lenient
             fixNum = 1:n(),
             firstFix = ifelse(fixNum == 1, 1, 0),
             lastFix = ifelse(fixNum == max(fixNum), 1, 0),
             middleFix = ifelse(firstFix == 0 & lastFix == 0, 1, 0),
             numTotalFix = max(fixNum)) %>%
      select(-block, -stime, -etime, -dur, -axp, -ayp, -aps, -eye) %>%
      left_join(cur_choice_dat, by=c("subnum", "day", "trialNum"))

    data_fix_bc = rbind(data_fix_bc, cur_fix_clean)
  }
}

write.csv(data_fix_bc, paste0(here(), '/inputs/data_fixBC.csv'), row.names = F)



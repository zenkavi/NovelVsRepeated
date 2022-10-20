library(tidyverse)
library(here)

helpers_path = here()

data_yn = read.csv(paste0(helpers_path, '/inputs/data_choiceYN.csv'))

data_yn_clean = data_yn %>%
  filter(session != -99) %>%
  select(-inizialTime, -inizialTimeResp, -endTime, -endTimeResp)

data_bc = read.csv(paste0(helpers_path, '/inputs/data_choiceBC.csv'))

data_bc_clean = data_bc %>%
  select(-stimLettNumLeft, -stimLettNumRight) %>%
  rename(stimNumLeft = stimNumLef) %>%
  select(-inizialTime, -inizialTimeResp, -endTime, -endTimeResp)

rm(data_yn, data_bc)

print("Done loading data.")

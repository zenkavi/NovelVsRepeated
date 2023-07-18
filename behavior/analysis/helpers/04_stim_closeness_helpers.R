library(tidyverse)


# Function to get stimnums and attribute levels for HT stims for a given subject

get_sub_ht_stims = function(cur_sub, data = data_yn_clean){

  out = data %>%
    filter(subnum == cur_sub & type == 1) %>%
    select(type, stimNum, shape, filling, orientation) %>%
    distinct() %>%
    arrange(stimNum)

  return(out)
}


# Function to get stimnums and attribute levels for stims close to a given HT stim num for a given subject
get_sub_cht_stims_for_one_ht = function(cur_sub, ht_stim, data = data_yn_clean, w_shape = TRUE){

  # For each of the HT stims define CHT stims as:
  # same filling, same orientation, different shape (5 stims)
  # same shape, same orientation. filling level +/- 1 (2 stims)
  # same shape, filling, orientation level +/1 (2 stims)
  # Exclude if any CHT is also an HT stim

  sub_ht_stim = data %>%
    filter(subnum == cur_sub & type == 1 & stimNum == ht_stim) %>%
    select(type, stimNum, shape, filling, orientation) %>%
    distinct()

  shape_level = sub_ht_stim$shape[1]
  orientation_level = sub_ht_stim$orientation[1]
  filling_level = sub_ht_stim$filling[1]

  # List all levels of all attributes
  shape_levels = sort(unique(data$shape))
  orientation_levels = sort(unique(data$orientation))
  filling_levels = sort(unique(data$filling))

  # Get close shape levels
  if(w_shape){
    close_shape_levels = shape_levels[shape_levels != shape_level]
    out = tibble(shape = close_shape_levels, filling = filling_level, orientation = orientation_level)
  } else {
    out = tibble()
  }

  # Get close orientation levels
  orientation_level_index = which(orientation_levels == orientation_level)

  if(orientation_level_index == 1){  # if o = 0, get o = 15, o = 150
    close_orientation_levels = c(orientation_levels[2], orientation_levels[length(orientation_levels)])
  } else if (orientation_level_index == length(orientation_levels)){ #if o = 150, get o = 135, o = 0
    close_orientation_levels = c(orientation_levels[1], orientation_levels[length(orientation_levels) - 1])
  } else{
    close_orientation_levels = orientation_levels[c(orientation_level_index-1, orientation_level_index+1)]
  }

  out = rbind(out, tibble(shape = shape_level, filling = filling_level, orientation = close_orientation_levels))


  # Get close filling levels
  filling_level_index = which(filling_levels == filling_level)

  if(filling_level_index == 1){
    close_filling_levels = filling_levels[2]
  } else if(filling_level_index == length(filling_levels)){
    close_filling_levels = filling_levels[filling_level_index - 1]
  } else {
    close_filling_levels = filling_levels[c(filling_level_index - 1, filling_level_index + 1)]
  }

  out = rbind(out, tibble(shape = shape_level, filling = close_filling_levels, orientation = orientation_level))

  # Get stimNums for the CHT
  out = data %>%
    filter(subnum == cur_sub) %>%
    select(stimNum, type, shape, filling, orientation) %>%
    right_join(out, by = c("shape", "filling", "orientation")) %>%
    arrange(stimNum) %>%

    # Check if any of the CHT are also HT
    filter(type != 1) %>%
    distinct()

  return(out)
}

# Wrapper to get all close to HT stims for a given subject
get_sub_cht_stims_for_all_ht = function(cur_sub, data = data_yn_clean, w_shape = TRUE){

  sub_ht_stims = get_sub_ht_stims(cur_sub, data = data)

  out = tibble()

  for(cur_ht_stim in sub_ht_stims$stimNum){
    out = rbind(out, get_sub_cht_stims_for_one_ht(cur_sub, cur_ht_stim, data = data, w_shape = w_shape))
  }

  return(out)

}

## Assign CHT labels to dataset
get_cht_labels_for_all_subs = function(data = data_yn_clean, w_shape = TRUE){

  out = tibble()

  for(cur_sub in unique(data$subnum)){
    sub_cht_stimnums = get_sub_cht_stims_for_all_ht(cur_sub, data = data, w_shape = w_shape)

    sub_cht_stimnums = sub_cht_stimnums$stimNum

    cur_out = data_yn_clean %>%
      filter(subnum == cur_sub) %>%
      mutate(type_chr = ifelse(stimNum %in% sub_cht_stimnums, "CHT", type_chr))

    out = rbind(out, cur_out)
  }

  return(out)
}



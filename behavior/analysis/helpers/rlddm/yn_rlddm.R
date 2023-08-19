sim_task = function(stims, ht_values, attr_values, d, sigma, alpha, theta, oe_noise, re_noise, nonDecisionTime, bias = 0, barrierDecay = 0, barrier = 1, timeStep = 10, maxIter = 1000, return_values = TRUE){ # nolint

  # Since value updating needs to happen sequentially (i.e. cannot be parallelized) writing this function as a task simulator instead of a trial simulator

  # stims : trial information containing attribute levels and possible payoff
  # values: list with values for each attribute
  # d : drift rate
  # sigma: sd of the normal distribution from which RDVs are sampled in each timestep
  # alpha: learning rate for ht stims
  # theta: generalization rate for re stims
  # re_noise: noise for the normal distribution from which the RE stim value is drawn
  # oe_noise: noise for the normal distribution from which the RE stim value is drawn
  # timeStep: in ms
  # nonDecisionTime: in ms
  # maxIter: num max samples. if a barrier isn't hit by this sampling of evidence no decision is made.
  # If time step is 10ms and maxIter is 1000 this would be a 10sec timeout maximum

  out = tibble()
  val_shape = attr_values$val_shape
  val_orientation = attr_values$val_orientation
  val_filling = attr_values$val_filling
  ht_vals = ht_values

  # val_shape = rep(0, 6) # indexed for [1, 2, 3, 4, 5, 6]
  # val_orientation = rep(0, 11) # indexed for [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150]
  # val_filling = rep(0, 9) # indexed for [-.85, -.6, -.4, -.2, 0, .2, .4, .6, .85]

  # nonDecIters = nonDecisionTime / timeStep
  initialBarrier = barrier
  # barrier = rep(initialBarrier, maxIter)

  for(stim_row in 1:nrow(stims)){

    barrier = rep(initialBarrier, maxIter)

    nonDecIters = nonDecisionTime / timeStep
    trial_sigma = sigma

    # Initialize variables that will be populated
    # bias is operationalized differently than the HDDM, where it ranges 0 to 1 and no bias is .5
    # Here no bias is 0 and the range is -1 to 1
    RDV = bias
    time = 1
    elapsedNDT = 0
    choice = 0
    RT = NA
    tooSlow = 0

    # Extract stimulus information
    cur_type = stims$type[stim_row]
    # trial_sigma = ifelse(cur_type == 1, trial_sigma * oe_noise, trial_sigma) # this is weird

    cur_shape = stims$shape[stim_row]
    cur_orientation = stims$orientation[stim_row]
    cur_filling = stims$filling[stim_row]
    cur_stimNum = as.character(stims$stimNum[stim_row])

    shape_index = cur_shape
    orientation_index = (cur_orientation/15) + 1
    filling_index = round(cur_filling/.2) + 5

    cur_shape_val = val_shape[shape_index]
    cur_orientation_val = val_orientation[orientation_index]
    cur_filling_val = val_filling[filling_index]

    # Should all attributes be updated by the full observed amount?
    observed_val = stims$possiblePayoff[stim_row]

    cur_day = NA
    if("day" %in% names(stims)){
      if(length(unique(stims$day)) > 1){
        cur_day = stims$day[stim_row]
      }
    }

    if(cur_type == 1){
      
      # Add barrier decay option only for HT stims
      for(t in seq(2, maxIter, 1)){
        barrier[t] = initialBarrier / (1 + (barrierDecay * t))
        }

      if(! (cur_stimNum %in% names(ht_vals)) ){
        ht_vals[[cur_stimNum]] = 0
      }
      cur_stim_val = ht_vals[[cur_stimNum]]
    } else {
      cur_stim_val  = (cur_shape_val + cur_orientation_val + cur_filling_val)/3
    }


    # The values of the barriers can change over time
    # for(t in seq(2, maxIter, 1)){
    #   barrier[t] = initialBarrier / (1 + (barrierDecay * t))
    # }

    # Average drift rate is sampled from the distributions with different noie levels depending on stimulus type
    cur_stim_val = ifelse(cur_type == 1,  rnorm(1, mean = cur_stim_val, sd = oe_noise), rnorm(1, mean = cur_stim_val, sd = re_noise))

    cur_ref_val = stims$reference[stim_row]
    mu_mean = d * (cur_stim_val - cur_ref_val)

    while (time<maxIter) {

      # If the RDV hit one of the barriers, the trial is over.
      if (RDV >= barrier[time] | RDV <= -barrier[time]){

        # Convert ms back to secs
        RT = (time * timeStep)/1000

        # Specify which choice is made
        if (RDV >= barrier[time]){
          choice = "yes"

        } else if (RDV <= -barrier[time]){
          choice = "no"
        }
        break
      }

      if (elapsedNDT < nonDecIters){
        mu = 0
        elapsedNDT = elapsedNDT + 1
      } else{
        mu = mu_mean
      }

      # Sample the change in RDV from the distribution.
      # Noise isn't in the sampling of evidence to decision. It's in the representation of value
      # sigma = ifelse(cur_type == 1, oe_noise, re_noise)

      # RDV = RDV + rnorm(1, mu, sigma)
      RDV = RDV + rnorm(1, mu, trial_sigma)

      # Increment sampling iteration
      time = time + 1
    }

    # If a choice hasn't been made by the time limit
    if(is.na(RT)){

      # Choose whatever you have most evidence for
      if (RDV >= 0){
        choice = "yes"
      } else if (RDV <= 0){
        choice = "no"
      }

      # Sample a random RT from a log normal distribution with a mean of 7.5 secs
      tooSlow = 1
      RT = rlnorm(1, mean = 2, sd = 0.1)
    }

    # Update value representations
    # This doesn't depend on which choice is made because feedback is provided regardless
    # No embedded assumption on how value "leaks" across consecutive levels (which might be the case for the attributes with continuos levels)
    if(cur_type == 1){
      ht_vals[cur_stimNum] = cur_stim_val + alpha * (observed_val - cur_stim_val)
    }

    val_shape[shape_index] = cur_shape_val + theta * (observed_val - cur_shape_val)
    val_orientation[orientation_index] = cur_orientation_val + theta * (observed_val - cur_orientation_val)
    val_filling[filling_index] = cur_filling_val + theta * (observed_val - cur_filling_val)

    # Make sure the RT is always at least as large as the nonDecisionTime
    # (Even if a boundary is hit only by noise before ndt)
    tooFast = as.numeric( (RT*1000) < nonDecisionTime )
    RT = ifelse( (RT*1000) < nonDecisionTime, nonDecisionTime/1000, RT)

    #Organize output
    pred_trial = tibble(shape = round(cur_shape), orientation = round(cur_orientation), filling = round(cur_filling, 2),
                        shape_val = round(cur_shape_val, 3), orientation_val = round(cur_orientation_val, 3), filling_val = round(cur_filling_val, 3),
                        stim_ev = cur_stim_val, type = cur_type, possiblePayoff = stims$possiblePayoff[stim_row], reference = stims$reference[stim_row], day = cur_day,
                        trial_drift = mu_mean,
                        choice = choice, reactionTime = RT,
                        tooSlow = tooSlow, tooFast = tooFast,
                        d = d, sigma = sigma, alpha = alpha,
                        barrierDecay = barrierDecay, barrier = barrier[time], nonDecisionTime = nonDecisionTime, bias = bias,
                        timeStep = timeStep, maxIter = maxIter,
                        val_shape = list(val_shape), val_orientation = list(val_orientation), val_filling = list(val_filling))

    out = rbind(out, pred_trial)


  }

  if(return_values){
    return(list(out = out, values = list(ht_vals = ht_vals, val_shape = val_shape, val_orientation = val_orientation, val_filling = val_filling)))
  } else {
    return(out)
  }
}

sim_task = function(stims, d, sigma, alpha, theta, nonDecisionTime, bias, barrierDecay, barrier = 1, timeStep = 10, maxIter = 1000, debug = FALSE, return_values = TRUE){

  # Since value updating needs to happen sequentially (i.e. cannot be parallelized) writing this function as a task simulator instead of a trial simulator

  # stims : trial information containing attribute levels and possible payoff
  # d : drift rate
  # sigma: sd of the normal distribution from which RDVs are sampled in each timestep
  # theta: percentage of updated value that leaks to consecutive levels of orientation and filling [0, 1]
  # timeStep: in ms
  # nonDecisionTime: in ms
  # maxIter: num max samples. if a barrier isn't hit by this sampling of evidence no decision is made.
  # If time step is 10ms and maxIter is 1000 this would be a 10sec timeout maximum

  out = tibble()
  val_shape = rep(0, 6) # indexed for [1, 2, 3, 4, 5, 6]
  val_orientation = rep(0, 11) # indexed for [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150]
  val_filling = rep(0, 9) # indexed for [-.85, -.6, -.4, -.2, 0, .2, .4, .6, .85]

  nonDecIters = nonDecisionTime / timeStep
  initialBarrier = barrier
  barrier = rep(initialBarrier, maxIter)

  for(stim_row in 1:nrow(stims)){

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
    cur_shape = stims$shape[stim_row]
    cur_orientation = stims$orientation[stim_row]
    cur_filling = stims$filling[stim_row]

    shape_index = cur_shape
    orientation_index = (cur_orientation/15) + 1
    filling_index = round(cur_filling/.2) + 5

    cur_shape_val = val_shape[shape_index]
    cur_orientation_val = val_orientation[orientation_index]
    cur_filling_val = val_filling[filling_index]

    observed_val = stims$possiblePayoff[stim_row]
    cur_type = stims$type[stim_row]


    # The values of the barriers can change over time
    for(t in seq(2, maxIter, 1)){
      barrier[t] = initialBarrier / (1 + (barrierDecay * t))
    }

    mu_mean = d * ((cur_shape_val + cur_orientation_val + cur_filling_val)/3)

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
      RDV = RDV + rnorm(1, mu, sigma)

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
    val_shape[shape_index] = cur_shape_val + alpha * (observed_val - cur_shape_val)

    val_orientation[orientation_index] = cur_orientation_val + alpha * (observed_val - cur_orientation_val)
    orientation_steps_away = 1:length(val_orientation) - orientation_index
    val_orientation = (orientation_steps_away * theta * val_orientation[orientation_index]) + val_orientation[orientation_index]

    if(filling_index != 5){
      val_filling[filling_index] = cur_filling_val + alpha * (observed_val - cur_filling_val)
      filling_steps_away = 1:length(val_filling) - filling_index

      if(filling_index < 5){
        filling_steps_away = (-1) * filling_steps_away
        tmp_val_filling = (filling_steps_away * theta * val_filling[filling_index]) + val_filling[filling_index]
        val_filling[1:4] = tmp_val_filling[1:4]
        val_filling[6:9] = (-1) * tmp_val_filling[4:1]
      } else {
        tmp_val_filling = (filling_steps_away * theta * val_filling[filling_index]) + val_filling[filling_index]
        val_filling[6:9] = tmp_val_filling[6:9]
        val_filling[1:4] = (-1) * tmp_val_filling[9:6]
      }
      val_filling[5] = 0
    }

    if(debug){
      cat(paste0("***Trial ", stim_row, "***\n"))
      cat(paste0("Stim details: Shape = ", cur_shape, ", Orientation = ", cur_orientation, ", Filling = ", cur_filling, "\n"))
      cat(paste0("Stim EV = ", round(mu_mean, 2), ", Payoff = ", observed_val, "\n"))
      cat("***Post-choice values: ***\n")
      cat("Shape = \n")
      cat(as.character(round(val_shape, 2)))
      cat("\n")
      cat("Orientation = \n")
      cat(as.character(round(val_orientation, 2)))
      cat("\n")
      cat("Filling = \n")
      cat(as.character(round(val_filling, 2)))

      cat("\n###################\n")
      cat("\n")
    }

    # Make sure the RT is always at least as large as the nonDecisionTime
    # (Even if a boundary is hit only by noise before ndt)
    tooFast = as.numeric( (RT*1000) < nonDecisionTime )
    RT = ifelse( (RT*1000) < nonDecisionTime, nonDecisionTime/1000, RT)

    #Organize output
    pred_trial = tibble(shape = round(cur_shape), orientation = round(cur_orientation), filling = round(cur_filling, 2),
                        shape_val = round(cur_shape_val, 3), orientation_val = round(cur_orientation_val, 3), filling_val = round(cur_filling_val, 3),
                        stim_ev = mu_mean, type = cur_type,
                        choice = choice, reactionTime = RT,
                        tooSlow = tooSlow, tooFast = tooFast,
                        d = d, sigma = sigma, alpha = alpha, theta = theta,
                        barrierDecay = barrierDecay, barrier = barrier[time], nonDecisionTime = nonDecisionTime, bias = bias,
                        timeStep = timeStep, maxIter = maxIter)

    out = rbind(out, pred_trial)
  }

  if(return_values){
    return(list(out = out, values = list(val_shape = val_shape, val_orientation = val_orientation, val_filling = val_filling)))
  } else {
    return(out)
  }
}

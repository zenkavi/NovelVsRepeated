sim_trial = function(d, sigma, nonDecisionTime=0, bias=0, barrierDecay=0, barrier=1, timeStep=10, maxIter=400, debug=FALSE,...){

  # d : drift rate
  # sigma: sd of the normal distribution
  # timeStep: in ms
  # nonDecisionTime: in ms
  # maxIter: num max samples. if a barrier isn't hit by this sampling of evidence no decision is made.
  # If time step is 10ms and maxIter is 1000 this would be a 10sec timeout maximum

  if (debug){
    debug_df = data.frame(time = 0, mu = NA, RDV = 0, barrier = barrier)
  }

  RDV = bias # this is operationalized differently than the HDDM, where it ranges 0 to 1 and no bias is .5
  # Here no bias is 0 and the range is -1 to 1
  time = 1
  elapsedNDT = 0
  choice = 0
  RT = NA

  timeOut = 0

  kwargs = list(...)

  ValStim=kwargs$ValStim
  ValRef=kwargs$ValRef

  nonDecIters = nonDecisionTime / timeStep

  initialBarrier = barrier
  barrier = rep(initialBarrier, maxIter)

  # The values of the barriers can change over time
  for(t in seq(2, maxIter, 1)){
    barrier[t] = initialBarrier / (1 + (barrierDecay * t))
  }

  mu_mean = d * (ValStim - ValRef)

  while (time<maxIter){

    # If the RDV hit one of the barriers, the trial is over.
    if (RDV >= barrier[time] | RDV <= -barrier[time]){

      # Convert ms back to secs
      RT = (time * timeStep)/1000

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

    if (debug){
      debug_row = data.frame(time = time, mu = round(mu, 3), RDV = round(RDV, 3), barrier = round(barrier[time], 3))
      debug_df = rbind(debug_df, debug_row)
    }

    # Increment sampling iteration
    time = time + 1
  }

  #If a choice hasn't been made by the time limit
  if(is.na(RT)){
    # Choose whatever you have most evidence for
    if (RDV >= 0){
      choice = "left"
    } else if (RDV <= 0){
      choice = "right"
    }
    if(debug){
      print("Max iterations reached.")
    }
    timeOut = 1
    RT=rlnorm(1, mean = 1.25, sd = 0.1)
  }

  #Organize output
  out = data.frame(ValStim = ValStim, ValRef = ValRef, choice=choice, reactionTime = RT, timeOut = timeOut, d = d, sigma = sigma, barrierDecay = barrierDecay, barrier=barrier[time], nonDecisionTime=nonDecisionTime, bias=bias, timeStep=timeStep, maxIter=maxIter)

  if(debug){
    return(list(out=out, debug_df = debug_df))
  } else {
    return(out)
  }
}

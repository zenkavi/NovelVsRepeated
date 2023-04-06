Previously:

`ddm_model.R` - contains `sim_trial` and `fit_trial` functions for a given model

`fit_task.R` - calls `fit_trial` function from a list of ddm model names in its `fit_task` function

`ddm_Roptim.R` - `optim_save` calls `get_task_nll` defined in `fit_task.R`

GRID SEARCH OR OPTIM?

If grid search: d, sigma, starting point bias, barrier decay, ndt (fix?)
If you try 10 values for each fixing one of these that's 10000 likelihoods to compute for each subject, day, stimulus type

If optim you can start from random points e.g. 500 times and see where the algorithm ends up

To build (in reverse order):
`run_optim_yn_ddm.sh`
`run_optim_yn_ddm.batch`
`optim_yn_ddm.R` ~ `ddm_Roptim.R` [don't need to use visualMLE `optim_save`]
`sim_yn_ddm.R` ~ `sim_task.R`
`fit_yn_ddm.R` ~ `fit_task.R`
`yn_ddm.R` ~ `ddm_model.R`

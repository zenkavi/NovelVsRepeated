# Save to /inputs

d = seq(0.01, .1, .01)
sigma = seq(.5, 2, .25)
ndt = seq(200, 400, 100)
bias = seq(-.1, .1, .1)
barrierDecay = c(0, .001, .01, .02)

ddm_grid = expand.grid(d, sigma, ndt, bias, barrierDecay)
names(ddm_grid) = c("d", "sigma", "nonDecisionTime", "bias", "barrierDecay")

write.csv(ddm_grid, paste0(here(), '/inputs/','ddm_grid.csv'),row.names=FALSE)


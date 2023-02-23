#!/bin/bash

#SBATCH -J yn-sim-hddm-sub-{SUBNUM}-{COND}-day-{DAY}_%j
#SBATCH -c 2

# Outputs ----------------------------------
#SBATCH -o /shared/.out/yn-sim-hddm-sub-{SUBNUM}-{COND}-day-{DAY}_%j.out
#SBATCH -e /shared/.err/yn-sim-hddm-sub-{SUBNUM}-{COND}-day-{DAY}_%j.err
# ------------------------------------------

export DATA_PATH=/shared/behavior

docker run --rm -v $DATA_PATH:/behavior -w /behavior zenkavi/rjagswiener:0.0.3 Rscript --vanilla /behavior/analysis/helpers/ddm/sim_yn_ddm.R --cond {COND} --day {DAY} --subnum {SUBNUM}

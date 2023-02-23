set -e

while getopts s:d: flag
do
    case "${flag}" in
        s) stim=${OPTARG};;
        d) day=${OPTARG};;
    esac
done

sed -e "s/{STIM}/$stim/g" -e "s/{DAY}/$day/g" run_fit_bc_hddm_rjags.batch | sbatch

# sh run_fit_bc_hddm_rjags.sh -s RE -d 4

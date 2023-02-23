set -e

while getopts s:d: flag
do
    case "${flag}" in
        s) stim=${OPTARG};;
        d) day=${OPTARG};;
    esac
done

sed -e "s/{STIM}/$stim/g" -e "s/{DAY}/$day/g" run_fit_bc_haddm_rjags.batch | sbatch

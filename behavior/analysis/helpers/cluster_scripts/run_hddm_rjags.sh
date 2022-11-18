set -e

while getopts s:d: flag
do
    case "${flag}" in
        s) stim=${OPTARG};;
        d) day=${OPTARG};;
    esac
done

sed -e "s/{STIM}/$stim/g" -e "s/{DAY}/$day/g" run_hddm_rjags.batch | sbatch

# ./run_ddm_Roptim.sh -s HT -d 4

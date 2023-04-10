set -e

while getopts s:d:c: flag
do
    case "${flag}" in
        c) cond=${OPTARG};;
        d) day=${OPTARG};;
        s) subnum=${OPTARG};;
    esac
done

sed -e "s/{COND}/$cond/g" -e "s/{DAY}/$day/g" -e "s/{SUBNUM}/$subnum/g" run_sim_yn_hddm.batch | sbatch

# sh run_fit_yn_hddm_rjags.sh -s 601 -c RE -d 4

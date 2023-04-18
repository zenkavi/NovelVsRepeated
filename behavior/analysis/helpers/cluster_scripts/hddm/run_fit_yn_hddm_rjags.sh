set -e

while getopts t:d: flag
do
    case "${flag}" in
        t) type=${OPTARG};;
        d) day=${OPTARG};;
    esac
done

sed -e "s/{TYPE}/$type/g" -e "s/{DAY}/$day/g" run_fit_yn_hddm_rjags.batch | sbatch

# sh run_fit_yn_hddm_rjags.sh -t RE -d 4

set -e

while getopts s:t: flag
do
    case "${flag}" in
        s) sub=${OPTARG};;
        t) type=${OPTARG};;
    esac
done

sed -e "s/{TYPE}/$type/g" -e "s/{SUB}/$sub/g" run_fit_yn_hddm_sub_rjags.batch | sbatch

# sh run_fit_yn_hddm_sub_rjags.sh -t RE -s 619

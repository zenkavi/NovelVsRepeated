set -e

model=yn_ddm

while getopts s:d:t: flag
do
    case "${flag}" in
        s) subnum=${OPTARG};;
        d) day=${OPTARG};;
        t) type=${OPTARG};;
    esac
done

sed -e "s/{MODEL}/$model/g" -e "s/{SUBNUM}/$subnum/g" -e "s/{DAYNUM}/$day/g" -e "s/{TYPE}/$type/g" run_grid_search_yn_ddm.batch | sbatch

# sh run_grid_search_yn_ddm.sh -s 601 -t RE -d 4

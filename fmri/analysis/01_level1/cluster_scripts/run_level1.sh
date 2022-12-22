set -e

while getopts m:t:s: flag
do
    case "${flag}" in
        m) modelnum=${OPTARG};;
        t) task=${OPTARG};;
        s) session=${OPTARG};;
    esac
done

for subnum in 601 609 611 619 621 629
  do
      sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SUBNUM}/$subnum/g" -e "s/{TASK}/$task/g" -e "s/{SESSION}/$session/g" run_level1.batch | sbatch
    done

# sh run_level1.sh -m model1 -t binaryChoice -s 2
# Should I change from model numbers to regressor names? Or maybe something in between where all models have a base set of regressors and the model nums refer to a small number of regressors differing between models?

# ./run_ddm_Roptim.sh -m threeIntegrators_sepProbDistortion -d sub_data_distV/sub01_data -s sub_sv_threeInts01.csv -o fitThreeInts -p dLott,dFrac,dArb,sigmaLott,sigmaFrac

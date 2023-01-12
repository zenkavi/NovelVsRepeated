set -e

while getopts m:t:s:o: flag
do
    case "${flag}" in
        m) modelnum=${OPTARG};;
        t) task=${OPTARG};;
        s) session=${OPTARG};;
        o) space=${OPTARG};;
    esac
done

for subnum in 601 609 611 619 621 629
  do
      sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SUBNUM}/$subnum/g" -e "s/{TASK}/$task/g" -e "s/{SESSION}/$session/g" -e "s/{SPACE}/$space/g" run_level1.batch | sbatch
    done

# 6 jobs each for each of the commands below
# sh run_level1.sh -m model1 -t binaryChoice -s 1 -o MNI152NLin2009cAsym:res-2
# sh run_level1.sh -m model1 -t binaryChoice -s 2 -o MNI152NLin2009cAsym:res-2
# sh run_level1.sh -m model1 -t binaryChoice -s 3 -o MNI152NLin2009cAsym:res-2
# sh run_level1.sh -m model1 -t yesNo -s 1 -o MNI152NLin2009cAsym:res-2
# sh run_level1.sh -m model1 -t yesNo -s 2 -o MNI152NLin2009cAsym:res-2
# sh run_level1.sh -m model1 -t yesNo -s 3 -o MNI152NLin2009cAsym:res-2

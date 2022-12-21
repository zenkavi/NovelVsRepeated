set -e
for modelnum in model1
do
  for subnum in 601 609 611 619 621 629
  do
    sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SUBNUM}/$subnum/g" run_level1.batch | sbatch
  done
done

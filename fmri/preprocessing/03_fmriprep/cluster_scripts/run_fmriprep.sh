set -e
for subnum in 601 609 611 619 621 629
do
sed -e "s/{SUBNUM}/$subnum/g" run_fmriprep.batch | sbatch
done

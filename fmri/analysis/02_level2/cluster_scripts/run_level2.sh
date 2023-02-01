set -e
for modelnum in model1
do
  for sign in pos neg
  do
    for regname in valHT_par valRE_par stimHT_ev stimRE_ev
    do
      for session in ses-01 ses-02 ses-03 ses-02_min_ses-01 ses-03_min_ses-01 ses-03_min_ses-02
      do
        sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{REGNAME}/$regname/g" -e "s/{SESSION}/$session/g" run_level2.batch | sbatch
      done
    done
  done
done

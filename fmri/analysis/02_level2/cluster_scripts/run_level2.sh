set -e
for modelnum in model1 model2
do
  for sign in pos neg
  do
    for regname in valDiffHT_par valDiffRE_par stimHT_ev stimRE_ev feedbackHT_ev feedbackRE_ev rewardHT_par rewardRE_par valSumHT_par valSumRE_par stimHT-stimRE stimRE-stimHT valDiffHT-valDiffRE valDiffRE-valDiffHT valSumHT-valSumRE valSumRE-valSumHT feedbackHT-feedbackRE feedbackRE-feedbackHT rewardHT-rewardRE rewardRE-rewardHT
    do
      for session in ses-01 ses-02 ses-03
      do
        for task in yesNo
        do
          sed -e "s/{MODELNUM}/$modelnum/g" -e "s/{SIGN}/$sign/g" -e "s/{REGNAME}/$regname/g" -e "s/{SESSION}/$session/g" -e "s/{TASK}/$task/g" run_level2.batch | sbatch
        done
      done
    done
  done
done

from compute_contrast_utils import make_basic_contrasts
from level1_utils import make_level1_design_matrix
import json

data_path = '/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri'

# Binary Choice task

subnum = '601'
session = '01'
task = 'binaryChoice'
runnum = '03'
mnum = 'model1'

design_matrix = make_level1_design_matrix(subnum, session, task, runnum, mnum, data_path, hrf_model = 'spm', drift_model='cosine')

contrasts = make_basic_contrasts(design_matrix)

## Add desired contrasts for the task
contrasts['correctHT-incorrectHT'] = contrasts['choiceCorrectHT_st'] - contrasts['choiceIncorrectHT_st']
contrasts['incorrectHT-correctHT'] = contrasts['choiceIncorrectHT_st'] - contrasts['choiceCorrectHT_st']
contrasts['correctRE-incorrectRE'] = contrasts['choiceCorrectRE_st'] - contrasts['choiceIncorrectRE_st']
contrasts['incorrectRE-correctRE'] = contrasts['choiceIncorrectRE_st'] - contrasts['choiceCorrectRE_st']
contrasts['rewardHT-rewardRE'] = contrasts['rewardHT_par'] - contrasts['rewardRE_par']
contrasts['rewardRE-rewardHT'] = contrasts['rewardRE_par'] - contrasts['rewardHT_par']
contrasts['valDiffHT-valDiffRE'] = contrasts['valDiffHT_par'] - contrasts['valDiffRE_par']
contrasts['valDiffRE-valDiffHT'] = contrasts['valDiffRE_par'] - contrasts['valDiffHT_par']
contrasts['valSumHT-valSumRE'] = contrasts['valSumHT_par'] - contrasts['valSumRE_par']
contrasts['valSumRE-valSumHT'] = contrasts['valSumRE_par'] - contrasts['valSumHT_par']
contrasts['valEffectsOfInterestHT'] = np.vstack((contrasts['valDiffHT_par'], contrasts['valSumHT_par']))
contrasts['valEffectsOfInterestRE'] = np.vstack((contrasts['valDiffRE_par'], contrasts['valSumRE_par']))

## Jsonify
contrasts = {k:v.tolist() for (k,v) in contrasts.items()}

## Save
fn = os.path.join('./level1_contrasts/binaryChoice_%s_contrasts.json')%(mnum)
json.dump(contrasts, open(fn, 'w', encoding='utf-8'), indent=4)

####################################################

# Yes/No task

subnum = '601'
session = '01'
task = 'yesNo'
runnum = '01'
mnum = 'model1'

## Make template design matrix
design_matrix = make_level1_design_matrix(subnum, session, task, runnum, mnum, data_path, hrf_model = 'spm', drift_model='cosine')

## Create dictionary with basic contrasts for the template design matrix
contrasts = make_basic_contrasts(design_matrix)

## Add desired contrasts for the task
contrasts['valHT-valRE'] = contrasts['valHT_par'] - contrasts['valRE_par']
contrasts['valRE-valHT'] = contrasts['valRE_par'] - contrasts['valHT_par']
contrasts['rewardHT-rewardRE'] = contrasts['rewardHT_par'] - contrasts['rewardRE_par']
contrasts['rewardRE-rewardHT'] = contrasts['rewardRE_par'] - contrasts['rewardHT_par']
contrasts['correctHT-incorrectHT'] = contrasts['choiceCorrectHT_st'] - contrasts['choiceIncorrectHT_st']
contrasts['incorrectHT-correctHT'] = contrasts['choiceIncorrectHT_st'] - contrasts['choiceCorrectHT_st']
contrasts['correctRE-incorrectRE'] = contrasts['choiceCorrectRE_st'] - contrasts['choiceIncorrectRE_st']
contrasts['incorrectRE-correctRE'] = contrasts['choiceIncorrectRE_st'] - contrasts['choiceCorrectRE_st']

## Jsonify
contrasts = {k:v.tolist() for (k,v) in contrasts.items()}

## Save
fn = os.path.join('./level1_contrasts/yesNo_%s_contrasts.json')%(mnum)
json.dump(contrasts, open(fn, 'w', encoding='utf-8'), indent=4)

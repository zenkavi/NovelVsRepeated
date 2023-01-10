from compute_contrast_utils import make_basic_contrasts
from level1_utils import make_level1_design_matrix
import json

# Binary Choice task

subnum = '601'
session = '01'
task = 'binaryChoice'
runnum = '03'
mnum = 'model1'

design_matrix = make_level1_design_matrix(subnum, session, task, runnum, mnum, data_path, hrf_model = 'spm', drift_model='cosine')

contrasts = make_basic_contrasts(design_matrix)
contrasts

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
contrasts['valHT-valRE'] = contrasts['valRE_par'] - contrasts['valHT_par']
contrasts['rewardHT-rewardRE'] = contrasts['rewardHT_par'] - contrasts['rewardRE_par']
contrasts['rewardRE-rewardHT'] = contrasts['rewardRE_par'] - contrasts['rewardHT_par']

fn = 'yesNo_%s_contrasts.json'%(mnum)
f = open(fn, 'wb')
f.write(json.dumps(contrasts))
f.close()

import glob
import json
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
import numpy as np
import os
import pandas as pd
import pickle
from level1_utils import get_model_regs

def make_basic_contrasts(design_matrix):
    # first generate canonical contrasts (i.e. regressors vs. baseline)
    contrast_matrix = np.eye(design_matrix.shape[1])
    contrasts = dict([(column, contrast_matrix[i])
                      for i, column in enumerate(design_matrix.columns)])

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])

    beh_regs = design_matrix.columns
    to_filter = ['trans', 'rot', 'drift', 'framewise', 'scrub', 'constant', 'dvars']
    beh_regs = [x for x in beh_regs if all(y not in x for y in to_filter)]

    contrasts = dictfilt(contrasts, beh_regs)

    return contrasts


def compute_contrasts(subnum, session, task, mnum, contrasts_fn, out_path, output_type = 'effect_size', output_space = 'MNI152NLin2009cAsym_res-2'):

    # Make contrast path for each subject within the model output path
    contrasts_path = os.path.join(out_path, "sub-%s/ses-%s/contrasts"%(subnum, session))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)


    # Read in level 1 model
    print("***********************************************")
    print("Loading GLM for sub-%s ses-%s task-%s"%(subnum, session, task))
    print("***********************************************")
    fn = os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_space-%s_%s_level1_glm.pkl' %(subnum, session, subnum, session, task, output_space, mnum))
    f = open(fn, 'rb')
    fmri_glm = pickle.load(f)
    f.close()

    # Read in contrasts file
    print("***********************************************")
    print("Loading contrast file %s"%(contrasts_fn))
    print("***********************************************")
    fn = os.path.join(os.path.dirname(__file__),'level1_contrasts/%s' %(contrasts_fn))
    f = open(fn, 'rb')
    contrasts = json.loads(f.read())
    f.close()
    ## Numpify the contrast file from jsonified lists as elements
    contrasts = {k:np.array(v) for (k, v) in contrasts.items()}

    # Check that the design matrix contains the regressors of interest
    checks_passed = True

    regs = get_model_regs(mnum, task)
    for cur_reg in regs:
        if not cur_reg in contrasts.keys():
            print("Contrast file missing regressor %s"%(cur_reg))
            checks_passed = False
            break

    # Zero padding or removal depending on design matrix size
    dm_num_cols = len(fmri_glm.design_matrices_[0].columns)
    contrasts_num_els = len(contrasts['cross_ev'])

    print("***********************************************")
    print("Contrast file # elements %s; design matrix # columns %s"%(str(contrasts_num_els), str(dm_num_cols)))
    print("***********************************************")

    if dm_num_cols < contrasts_num_els:
        contrasts = {k:v[:dm_num_cols] for (k, v) in contrasts.items()}

    if dm_num_cols > contrasts_num_els:
        n = dm_num_cols - contrasts_num_els
        contrasts = {k:np.pad(v, (0, n), 'constant', constant_values = 0) for (k, v) in contrasts.items()}

    if checks_passed:
        print("***********************************************")
        print("Computing contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
        print("***********************************************")
        # contrasts = make_contrasts(design_matrix[0], mnum) # using the first design matrix since contrasts are the same for all runs
        for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
            contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= output_type)
            nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, output_space, mnum, contrast_id, output_type))
            contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= 'stat') #also save tmaps
            nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, output_space, mnum, contrast_id, 'tmap'))
        print("***********************************************")
        print("Done saving contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
        print("***********************************************")

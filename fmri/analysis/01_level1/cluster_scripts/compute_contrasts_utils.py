import glob
import json
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
import numpy as np
import os
import pandas as pd
import pickle

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


def compute_contrast(subnum, session, task, mnum, contrasts_fn, out_path, output_type = 'effect_size', space = 'MNI152NLin2009cAsym_res-2'):

    # Make contrast path for each subject within the model output path
    contrasts_path = os.path.join(out_path, "sub-%s/ses-%s/contrasts"%(subnum, session))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)


    # Read in level 1 model
    print("***********************************************")
    print("Loading GLM for sub-%s ses-%s task-%s"%(subnum, session, task))
    print("***********************************************")
    fn = os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_space-%s_%s_level1_glm.pkl' %(subnum, session, subnum, session, task, space, mnum))
    f = open(fn, 'rb')
    fmri_glm = pickle.load(f)
    f.close()

    # Read in contrasts file
    print("***********************************************")
    print("Loading contrast file %s"%(contrasts_fn))
    print("***********************************************")
    fn = os.path.join('./level1_contrasts/%s' %(contrasts_fn))
    f = open(fn, 'rb')
    contrasts = json.loads(f.read())
    f.close()


    print("***********************************************")
    print("Computing contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
    print("***********************************************")
    # contrasts = make_contrasts(design_matrix[0], mnum) # using the first design matrix since contrasts are the same for all runs
    for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
        contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= output_type)
        nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, space, mnum, contrast_id, output_type))
        contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= 'stat') #also save tmaps
        nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, space, mnum, contrast_id, 'tmap'))
    print("***********************************************")
    print("Done saving contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
    print("***********************************************")

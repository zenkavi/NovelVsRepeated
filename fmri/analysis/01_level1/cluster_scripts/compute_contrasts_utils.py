import glob
import json
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
import numpy as np
import os
import pandas as pd
import pickle
from level1_utils import get_model_regs
from nilearn.image import new_img_like, load_img, math_img, get_data

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

def compute_session_contrasts(subnum, session1, session2, task, mnum, reg, base_path, output_space = 'MNI152NLin2009cAsym_res-2'):

    # Example Usage
    #
    # base_path = '/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri'
    #
    # task = 'yesNo'
    # mnum = 'model2'
    #
    # regs = ['valHT_par', 'valRE_par', 'stimHT_ev', 'stimRE_ev']
    # subnums = ['601', '609', '611', '619', '621', '629']
    # sessions = [{'session1': 'ses-01', 'session2': 'ses-02'},
    #             {'session1': 'ses-01', 'session2': 'ses-03'},
    #             {'session1': 'ses-02', 'session2': 'ses-03'}]
    #
    # for cur_reg in regs:
    #     for cur_sub in subnums:
    #         for cur_sessions in sessions:
    #             cur_session1 = cur_sessions['session1']
    #             cur_session2 = cur_sessions['session2']
    #
    #             compute_session_contrasts(cur_sub, cur_session1, cur_session2, task, mnum, cur_reg, base_path)

    in_path = os.path.join(base_path, 'derivatives/nilearn/glm/level1', task, mnum, 'sub-'+subnum)

    out_path = os.path.join(in_path, "session_contrasts")
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    # Read in beta maps
    ## Session 1
    map_type = 'effect_size'
    fn1 = 'sub-%s_%s_task-%s_space-%s_%s_%s_%s.nii.gz' %(subnum, session1, task, output_space, mnum, reg, map_type)
    beta1 = load_img(os.path.join(in_path, session1+'/contrasts', fn1))
    beta1_data = get_data(beta1)

    ## Session 2
    fn2 = 'sub-%s_%s_task-%s_space-%s_%s_%s_%s.nii.gz' %(subnum, session2, task, output_space, mnum, reg, map_type)
    beta2 = load_img(os.path.join(in_path, session2+'/contrasts', fn2))
    beta2_data = get_data(beta2)


    # Read in tmaps
    ## Session 1
    map_type = 'tmap'
    fn1 = 'sub-%s_%s_task-%s_space-%s_%s_%s_%s.nii.gz' %(subnum, session1, task, output_space, mnum, reg, map_type)
    tmap1 = load_img(os.path.join(in_path, session1+'/contrasts', fn1))
    tmap1_data = get_data(tmap1)

    ## Session 2
    fn2 = 'sub-%s_%s_task-%s_space-%s_%s_%s_%s.nii.gz' %(subnum, session2, task, output_space, mnum, reg, map_type)
    tmap2 = load_img(os.path.join(in_path, session2+'/contrasts', fn2))
    tmap2_data = get_data(tmap2)


    # Compute SE maps
    ## Session 1
    se1_data = np.divide(beta1_data, tmap1_data, out=np.zeros_like(beta1_data), where = tmap1_data!=0)

    ## Session 2
    se2_data = np.divide(beta2_data, tmap2_data, out=np.zeros_like(beta2_data), where = tmap2_data!=0)

    # Compute session contrast beta map
    contrast_beta_data = np.subtract(beta2_data, beta1_data)
    contrast_beta = new_img_like(beta1, contrast_beta_data)
    print("***********************************************")
    print("Saving contrast beta map for sub-%s %s_min_%s task-%s %s %s"%(subnum, session2, session1, task, mnum, reg))
    print("***********************************************")
    nib.save(contrast_beta, '%s/sub-%s_%s_min_%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(out_path, subnum, session2, session1, task, output_space, mnum, reg, 'effect_size'))

    # Compute session contrast tmap
    contrast_denom_data = np.sqrt(np.power(se1_data, 2) + np.power(se2_data, 2))
    contrast_tmap_data = np.divide(contrast_beta_data, contrast_denom_data, out = np.zeros_like(contrast_beta_data), where = tmap2_data!=contrast_denom_data)
    contrast_tmap = new_img_like(tmap1, contrast_tmap_data)
    print("***********************************************")
    print("Saving contrast tmap for sub-%s %s_min_%s task-%s %s %s"%(subnum, session2, session1, task, mnum, reg))
    print("***********************************************")
    nib.save(contrast_tmap, '%s/sub-%s_%s_min_%s_task-%s_space-%s_%s_%s_%s.nii.gz'%(out_path, subnum, session2, session1, task, output_space, mnum, reg, 'tmap'))

import glob
import json
import nibabel as nib
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import make_first_level_design_matrix
import numpy as np
import os
import pandas as pd
import re
import pickle

def get_from_sidecar(subnum, session, task, runnum, keyname, data_path):

    fn = os.path.join(data_path, 'sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_bold.json'%(subnum, session, subnum, session, task, runnum))
    f = open(fn)
    bold_sidecar = json.load(f)
    f.close()

    # Currently can only extract first level keys from the json. Can extract multiple first level keys.
    if type(keyname)==list:
        out = [bold_sidecar.get(key) for key in keyname]
    else:
        out = bold_sidecar[keyname]

    return out

def get_model_regs(mnum):
    if mnum == 'model1':
        regs = ['cross_ev', 'stim_ev', 'reward_ev', 'reward_par', 'condition_ev', 'choiceCorrect_st', 'valChosenMinusUnchosen_par']

    if mnum == 'model2':
        regs = ['cross_ev', 'stim_ev', 'reward_ev', 'reward_par', 'condition_ev', 'choiceCorrect_st', 'valChosenPlusUnchosen_par']

    if mnum == 'model3':
        regs = ['cross_ev', 'stim_ev', 'reward_ev', 'reward_par', 'condition_ev', 'choiceCorrect_st', 'valueChosen_par', 'valueUnchosen_par']

    if mnum == 'model4':
        regs = ['cross_ev', 'stim_ev', 'reward_ev', 'reward_par', 'condition_ev', 'choiceCorrect_st', 'valueLeft_par', 'valueRight_par']

    return regs

def make_contrasts(design_matrix, mnum):
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

def get_confounds(subnum, session, task, runnum, data_path, scrub_thresh = .5):

    fn = os.path.join(data_path, 'derivatives/sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_desc-confounds_timeseries.tsv'%(subnum, session, subnum, session, task, runnum))

    confounds = pd.read_csv(fn,  sep='\t')

    confound_cols = [x for x in confounds.columns if 'trans' in x]+[x for x in confounds.columns if 'rot' in x]+['std_dvars', 'framewise_displacement']

    formatted_confounds = confounds[confound_cols]

    formatted_confounds = formatted_confounds.fillna(0)

    formatted_confounds['scrub'] = np.where(formatted_confounds.framewise_displacement>scrub_thresh,1,0)

    formatted_confounds = formatted_confounds.assign(
        scrub = lambda dataframe: dataframe['framewise_displacement'].map(lambda framewise_displacement: 1 if framewise_displacement > scrub_thresh else 0))

    return formatted_confounds

def get_events(subnum, session, task, runnum, mnum, data_path):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_events.tsv' %(subnum, session, subnum, session, task, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with demeaned stimulus values and choices
    fn = os.path.join(data_path, 'sub-%s/ses-%s/beh/sub-%s_ses-%s_task-%s_run-%s_beh.tsv' %(subnum, session, subnum, session, task, runnum))
    behavior = pd.read_csv(fn, sep='\t')

    # Get regressors for the model
    regs = get_model_regs(mnum)


    for reg in regs:
        if reg == 'cross_ev':
            cond_cross_ev = events.query('trial_type == "fixCross"')[['onset', 'duration']].reset_index(drop=True)
            cond_cross_ev['trial_type'] = 'cross_ev'
            cond_cross_ev['modulation'] = 1

        if reg == 'stim_ev':
            cond_stim_ev = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_stim_ev['trial_type'] = 'stim_ev'
            cond_stim_ev['modulation'] = 1

        if reg == 'reward_ev':
            cond_reward_ev = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_ev['trial_type'] = 'reward_ev'
            cond_reward_ev['modulation'] = 1

        if reg == 'reward_par':
            cond_reward_par = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_reward_par['trial_type'] = 'reward_par'
            cond_reward_par['modulation'] = behavior['reward_dmn'].reset_index(drop=True)

        if reg == 'condition_ev':
            cond_condition_ev = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_condition_ev['trial_type'] = 'condition_ev'
            cond_condition_ev['modulation'] = behavior['type'].reset_index(drop=True)

        if reg == 'choiceCorrect_st':
            cond_choiceCorrect_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceCorrect_st['duration'] = 0
            cond_choiceCorrect_st['trial_type'] = 'choiceCorrect_st'
            cond_choiceCorrect_st['modulation'] = behavior['correct'].reset_index(drop=True)

        if reg == 'valChosenMinusUnchosen_par':
            cond_valChosenMinusUnchosen_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenMinusUnchosen_par['trial_type'] = 'valChosenMinusUnchosen_par'
            cond_valChosenMinusUnchosen_par['modulation'] = behavior['valChosenMinusUnchosen_dmn'].reset_index(drop=True)

        if reg == 'valChosenPlusUnchosen_par':
            cond_valChosenPlusUnchosen_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosenPlusUnchosen_par['trial_type'] = 'valChosenPlusUnchosen_par'
            cond_valChosenPlusUnchosen_par['modulation'] = behavior['valChosenPlusUnchosen_dmn'].reset_index(drop=True)

        if reg == 'valChosen_par':
            cond_valChosen_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valChosen_par['trial_type'] = 'valChosen_par'
            cond_valChosen_par['modulation'] = behavior['valueChosen_dmn'].reset_index(drop=True)

        if reg == 'valUnchosen_par':
            cond_valUnchosen_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valUnchosen_par['trial_type'] = 'valUnchosen_par'
            cond_valUnchosen_par['modulation'] = behavior['valueUnchosen_dmn'].reset_index(drop=True)

        if reg == 'valLeft_par':
            cond_valLeft_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valLeft_par['trial_type'] = 'valLeft_par'
            cond_valLeft_par['modulation'] = behavior['valueLeft_dmn'].reset_index(drop=True)

        if reg == 'valRight_par':
            cond_valRight_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valRight_par['trial_type'] = 'valRight_par'
            cond_valRight_par['modulation'] = behavior['valueRight_dmn'].reset_index(drop=True)

    # List of var names including 'cond'
    toconcat = [i for i in dir() if 'cond' in i]
    tmp = {}
    for i in toconcat:
        tmp.update({i:locals()[i]})
    formatted_events = pd.concat(tmp, ignore_index=True)

    # Sort everything by order of occurance (i.e. onset)
    formatted_events = formatted_events.sort_values(by='onset')
    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)
    return formatted_events

def make_level1_design_matrix(subnum, session, task, runnum, mnum, data_path, hrf_model = 'spm', drift_model='cosine'):

    tr = get_from_sidecar(subnum, session, task, runnum, 'RepetitionTime', data_path)

    # this does not exist in the sidecars. I can either add a function to bidsify_helpers to extract this from par files
    # or i could read in the preprocessed functional files and the get the fourth dimension from that
    # the second is probably more error-proof for getting the correct information though it would have been nice to have this in the metadata
    # n_scans = get_from_sidecar(subnum, runnum, 'dcmmeta_shape', data_path)[3]
    func_img = nib.load(os.path.join(data_path, 'sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_bold.nii.gz'%(subnum, session, subnum, session, task, runnum)))
    n_scans = func_img.get_fdata().shape[3]

    frame_times = np.arange(n_scans) * tr

    formatted_events = get_events(subnum, session, task, runnum, mnum, data_path)
    formatted_confounds = get_confounds(subnum, session, task, runnum, data_path)

    #takes care of derivative for condition columns if specified in hrf_model
    design_matrix = make_first_level_design_matrix(frame_times,
                                               formatted_events,
                                               drift_model=drift_model,
                                               add_regs= formatted_confounds,
                                               hrf_model=hrf_model)

    return design_matrix

# Fixed effects analysis for all runs of subjects based on tutorial on:
# https://nilearn.github.io/stable/auto_examples/04_glm_first_level/plot_fiac_analysis.html#sphx-glr-auto-examples-04-glm-first-level-plot-fiac-analysis-py
def run_level1(subnum, session, task, mnum, data_path, out_path, save_contrast = True, output_type='effect_size', noise_model='ar1', hrf_model='spm', drift_model='cosine', smoothing_fwhm=5):

    # Make output path for the model if it doesn't exist
    # /shared/fmri/bids/derivatives/nilearn/glm/level1/{TASK}/{MODELNUM}
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    # Make contrast path for each subject within the model output path
    contrasts_path = os.path.join(out_path, "sub-%s/ses-%s/contrasts"%(subnum, session))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)

    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-*_events.tsv'%(subnum, session, subnum, session, task)))
    sub_events.sort()

    #fmri_img: path to preproc_bold's that the model will be fit on
    fmri_img = glob.glob(os.path.join(data_path,"derivatives/sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"%(subnum, session, subnum, session, task)))
    fmri_img.sort()

    if len(fmri_img) == 0:
        print("***********************************************")
        print("No pre-processed BOLD found for sub-%s ses-%s task-%s"%(subnum, session, task))
        print("***********************************************")
    else:
        if task == 'yesNo' and len(fmri_img) != 2:
            print("***********************************************")
            print("Found fewer than 2 runs for sub-%s ses-%s task-%s"%(subnum, session, task))
            print("***********************************************")

        # Design matrix array can contain the design matrix for multiple runs
        design_matrix = []
        for run_events in sub_events:
            runnum = re.findall('\d+', os.path.basename(run_events))[2] #index 0 is subnum, index 1 for session, index 2 is run num
            run_design_matrix = make_level1_design_matrix(subnum, session, task, runnum, mnum, data_path, hrf_model = hrf_model, drift_model=drift_model)
            design_matrix.append(run_design_matrix)
            print("***********************************************")
            print("Saving design matrix for sub-%s ses-%s task-%s run-%s"%(subnum, session, task, runnum))
            print("***********************************************")
            run_design_matrix.to_csv(os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_run-%s_%s_level1_design_matrix.csv' %(subnum, session, subnum, session, task, runnum, mnum)), index=False)

        # Define GLM parmeters
        img_tr = get_from_sidecar(subnum, session, task, runnum, 'RepetitionTime', data_path) #get tr info from current runnum since it's the same for all runs
        mask_img = nib.load(os.path.join(data_path,'derivatives/sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'%(subnum, session, subnum, session, task, runnum)))
        fmri_glm = FirstLevelModel(t_r=img_tr,
                               noise_model=noise_model,
                               hrf_model=hrf_model,
                               drift_model=drift_model,
                               smoothing_fwhm=smoothing_fwhm,
                               mask_img=mask_img,
                               subject_label=subnum,
                               minimize_memory=True)

        # Fit glm to run image using run events
        print("***********************************************")
        print("Running fixed effects GLM for all runs of sub-%s ses-%s task-%s"%(subnum, session, task))
        print("***********************************************")
        fmri_glm = fmri_glm.fit(fmri_img, design_matrices = design_matrix)

        print("***********************************************")
        print("Saving GLM for sub-%s ses-%s task-%s"%(subnum, session, task))
        print("***********************************************")
        fn = os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_%s_level1_glm.pkl' %(subnum, session, subnum, session, task, mnum))
        f = open(fn, 'wb')
        pickle.dump(fmri_glm, f)
        f.close()

        # You don't need this step for group level analyses. You can load FirstLevelModel objects for SecondLevelModel.fit() inputs
        # But if you want to use images instead of FirstLevelModel objects as the input then `output_type` should be `effect_size` so you save the parameter maps and not other statistics
        if save_contrast:
            print("***********************************************")
            print("Running contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix[0], mnum) # using the first design matrix since contrasts are the same for all runs
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= output_type)
                nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, mnum, contrast_id, output_type))
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= 'stat') #also save tmaps
                nib.save(contrast_map, '%s/sub-%s_ses-%s_task-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, session, task, mnum, contrast_id, 'tmap'))
            print("***********************************************")
            print("Done saving contrasts for sub-%s ses-%s task-%s"%(subnum, session, task))
            print("***********************************************")

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

def get_model_regs(mnum, task):

    if task == 'binaryChoice':
        if mnum == 'model1':
            regs = ['cross_ev', 'stimHT_ev', 'rewardHT_ev', 'rewardHT_par', 'stimRE_ev', 'rewardRE_ev', 'rewardRE_par', 'choiceCorrectHT_st', 'choiceCorrectRE_st', 'choiceIncorrectHT_st', 'choiceIncorrectRE_st', 'choiceLeft_st', 'choiceRight_st', 'valSumHT_par', 'valDiffHT_par', 'valSumRE_par', 'valDiffRE_par']

    if task == 'yesNo':
        if mnum == 'model1':
            regs = ['cross_ev', 'stimHT_ev', 'rewardHT_ev', 'rewardHT_par', 'stimRE_ev', 'rewardRE_ev', 'rewardRE_par', 'choiceCorrectHT_st', 'choiceCorrectRE_st', 'choiceIncorrectHT_st', 'choiceIncorrectRE_st', 'choiceYes_st', 'choiceNo_st', 'valHT_par', 'valRE_par']
    return regs


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
    regs = get_model_regs(mnum, task)

    for reg in regs:
        if reg == 'cross_ev':
            cond_cross_ev = events.query('trial_type == "fixCross"')[['onset', 'duration']].reset_index(drop=True)
            cond_cross_ev['trial_type'] = 'cross_ev'
            cond_cross_ev['modulation'] = 1

        if reg == 'stimHT_ev':
            cond_stimHT_ev = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_stimHT_ev['trial_type'] = 'stimHT_ev'
            cond_stimHT_ev['modulation'] = 1
            cond_stimHT_ev['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_stimHT_ev = cond_stimHT_ev.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'stimRE_ev':
            cond_stimRE_ev = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_stimRE_ev['trial_type'] = 'stimRE_ev'
            cond_stimRE_ev['modulation'] = 1
            cond_stimRE_ev['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_stimRE_ev = cond_stimRE_ev.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'rewardHT_ev':
            cond_rewardHT_ev = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardHT_ev['trial_type'] = 'rewardHT_ev'
            cond_rewardHT_ev['modulation'] = 1
            cond_rewardHT_ev['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_rewardHT_ev = cond_rewardHT_ev.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'rewardRE_ev':
            cond_rewardRE_ev = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardRE_ev['trial_type'] = 'rewardRE_ev'
            cond_rewardRE_ev['modulation'] = 1
            cond_rewardRE_ev['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_rewardRE_ev = cond_rewardRE_ev.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'rewardHT_par':
            cond_rewardHT_par = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardHT_par['trial_type'] = 'rewardHT_par'
            cond_rewardHT_par['modulation'] = behavior['reward_dmn'].reset_index(drop=True)
            cond_rewardHT_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_rewardHT_par = cond_rewardHT_par.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'rewardRE_par':
            cond_rewardRE_par = events.query('trial_type == "feedback"')[['onset', 'duration']].reset_index(drop=True)
            cond_rewardRE_par['trial_type'] = 'rewardRE_par'
            cond_rewardRE_par['modulation'] = behavior['reward_dmn'].reset_index(drop=True)
            cond_rewardRE_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_rewardRE_par = cond_rewardRE_par.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'choiceCorrectHT_st':
            cond_choiceCorrectHT_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceCorrectHT_st['duration'] = 0
            cond_choiceCorrectHT_st['trial_type'] = 'choiceCorrectHT_st'
            cond_choiceCorrectHT_st['modulation'] = behavior['correct'].reset_index(drop=True)
            cond_choiceCorrectHT_st['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_choiceCorrectHT_st = cond_choiceCorrectHT_st.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'choiceCorrectRE_st':
            cond_choiceCorrectRE_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceCorrectRE_st['duration'] = 0
            cond_choiceCorrectRE_st['trial_type'] = 'choiceCorrectRE_st'
            cond_choiceCorrectRE_st['modulation'] = behavior['correct'].reset_index(drop=True)
            cond_choiceCorrectRE_st['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_choiceCorrectRE_st = cond_choiceCorrectRE_st.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'choiceIncorrectHT_st':
            cond_choiceIncorrectHT_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceIncorrectHT_st['duration'] = 0
            cond_choiceIncorrectHT_st['trial_type'] = 'choiceIncorrectHT_st'
            cond_choiceIncorrectHT_st['modulation'] = 1 - behavior['correct'].reset_index(drop=True)
            cond_choiceIncorrectHT_st['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_choiceIncorrectHT_st = cond_choiceIncorrectHT_st.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'choiceIncorrectRE_st':
            cond_choiceIncorrectRE_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceIncorrectRE_st['duration'] = 0
            cond_choiceIncorrectRE_st['trial_type'] = 'choiceIncorrectHT_st'
            cond_choiceIncorrectRE_st['modulation'] = 1 - behavior['correct'].reset_index(drop=True)
            cond_choiceIncorrectRE_st['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_choiceIncorrectRE_st = cond_choiceIncorrectRE_st.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'choiceLeft_st':
            cond_choiceLeft_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceLeft_st['duration'] = 0
            cond_choiceLeft_st['trial_type'] = 'choiceLeft_st'
            cond_choiceLeft_st['modulation'] = behavior['choiceLeft'].reset_index(drop=True)

        if reg == 'choiceRight_st':
            cond_choiceRight_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceRight_st['duration'] = 0
            cond_choiceRight_st['trial_type'] = 'choiceRight_st'
            cond_choiceRight_st['modulation'] = 1 - behavior['choiceLeft'].reset_index(drop=True)

        if reg == 'choiceYes_st':
            cond_choiceYes_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceYes_st['duration'] = 0
            cond_choiceYes_st['trial_type'] = 'choiceYes_st'
            cond_choiceYes_st['modulation'] = behavior['choiceYes'].reset_index(drop=True)

        if reg == 'choiceNo_st':
            cond_choiceNo_st = pd.DataFrame(events.query('trial_type == "stim"')['onset'] + events.query('trial_type == "stim"')['duration'], columns = ['onset']).reset_index(drop=True) # this is the same as the feedback onsets
            cond_choiceNo_st['duration'] = 0
            cond_choiceNo_st['trial_type'] = 'choiceNo_st'
            cond_choiceNo_st['modulation'] = 1 - behavior['choiceYes'].reset_index(drop=True)

        if reg == 'valHT_par':
            cond_valHT_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valHT_par['trial_type'] = 'valHT_par'
            cond_valHT_par['modulation'] = behavior['value_dmn'].reset_index(drop=True)
            cond_valHT_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valHT_par = cond_valHT_par.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'valRE_par':
            cond_valRE_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valRE_par['trial_type'] = 'valRE_par'
            cond_valRE_par['modulation'] = behavior['value_dmn'].reset_index(drop=True)
            cond_valRE_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valRE_par = cond_valRE_par.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'valDiffHT_par':
            cond_valDiffHT_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffHT_par['trial_type'] = 'valDiffHT_par'
            cond_valDiffHT_par['modulation'] = behavior['valChosenMinusUnchosen_dmn'].reset_index(drop=True)
            cond_valDiffHT_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valDiffHT_par = cond_valDiffHT_par.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'valDiffRE_par':
            cond_valDiffRE_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valDiffRE_par['trial_type'] = 'valDiffRE_par'
            cond_valDiffRE_par['modulation'] = behavior['valChosenMinusUnchosen_dmn'].reset_index(drop=True)
            cond_valDiffRE_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valDiffRE_par = cond_valDiffRE_par.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'valSumHT_par':
            cond_valSumHT_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumHT_par['trial_type'] = 'valSumHT_par'
            cond_valSumHT_par['modulation'] = behavior['valChosenPlusUnchosen_dmn'].reset_index(drop=True)
            cond_valSumHT_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valSumHT_par = cond_valSumHT_par.query('stim_type == 1').drop('stim_type', axis=1).reset_index(drop=True)

        if reg == 'valSumRE_par':
            cond_valSumRE_par = events.query('trial_type == "stim"')[['onset', 'duration']].reset_index(drop=True)
            cond_valSumRE_par['trial_type'] = 'valSumRE_par'
            cond_valSumRE_par['modulation'] = behavior['valChosenPlusUnchosen_dmn'].reset_index(drop=True)
            cond_valSumRE_par['stim_type'] = behavior['type'].reset_index(drop=True)
            cond_valSumRE_par = cond_valSumRE_par.query('stim_type == 0').drop('stim_type', axis=1).reset_index(drop=True)

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
def run_level1(subnum, session, task, mnum, data_path, out_path, space = 'MNI152NLin2009cAsym_res-2', noise_model='ar1', hrf_model='spm', drift_model='cosine', smoothing_fwhm=5):

    # Make output path for the model if it doesn't exist
    # /shared/fmri/bids/derivatives/nilearn/glm/level1/{TASK}/{MODELNUM}
    if not os.path.exists(out_path):
        os.makedirs(out_path)
        
    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-*_events.tsv'%(subnum, session, subnum, session, task)))
    sub_events.sort()

    #fmri_img: path to preproc_bold's that the model will be fit on
    fmri_img = glob.glob(os.path.join(data_path,"derivatives/sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-*_space-%s_desc-preproc_bold.nii.gz"%(subnum, session, subnum, session, task, space)))
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
            run_design_matrix.to_csv(os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_run-%s_space-%s_%s_level1_design_matrix.csv' %(subnum, session, subnum, session, task, runnum, space, mnum)), index=False)

        # Define GLM parmeters
        img_tr = get_from_sidecar(subnum, session, task, runnum, 'RepetitionTime', data_path) #get tr info from current runnum since it's the same for all runs
        mask_img = nib.load(os.path.join(data_path,'derivatives/sub-%s/ses-%s/func/sub-%s_ses-%s_task-%s_run-%s_space-%s_desc-brain_mask.nii.gz'%(subnum, session, subnum, session, task, runnum, space)))
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
        fn = os.path.join(out_path, 'sub-%s/ses-%s/sub-%s_ses-%s_task-%s_space-%s_%s_level1_glm.pkl' %(subnum, session, subnum, session, task, space, mnum))
        f = open(fn, 'wb')
        pickle.dump(fmri_glm, f)
        f.close()

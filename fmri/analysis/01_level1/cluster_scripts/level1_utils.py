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

def get_task_name(runnum):
    if runnum

def get_from_sidecar(subnum, runnum, keyname, data_path):

    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_bold.json'%(subnum, subnum, runnum))
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
        regs = ['fractalProb_ev', 'stim_ev', 'choiceShift_st', 'reward_ev']

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

def get_confounds(subnum, runnum, data_path, scrub_thresh = .5):

    fn = os.path.join(data_path, 'derivatives/sub-%s/func/sub-%s_task-bundles_run-%s_desc-confounds_timeseries.tsv'%(subnum, subnum, runnum))

    confounds = pd.read_csv(fn,  sep='\t')

    confound_cols = [x for x in confounds.columns if 'trans' in x]+[x for x in confounds.columns if 'rot' in x]+['std_dvars', 'framewise_displacement']

    formatted_confounds = confounds[confound_cols]

    formatted_confounds = formatted_confounds.fillna(0)

    formatted_confounds['scrub'] = np.where(formatted_confounds.framewise_displacement>scrub_thresh,1,0)

    formatted_confounds = formatted_confounds.assign(
        scrub = lambda dataframe: dataframe['framewise_displacement'].map(lambda framewise_displacement: 1 if framewise_displacement > scrub_thresh else 0))

    return formatted_confounds

def get_events(subnum, runnum, mnum, data_path, behavior_path):

    # Read in fmri events
    fn = os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-%s_events.tsv' %(subnum, subnum, runnum))
    events = pd.read_csv(fn, sep='\t')

    # Read in behavioral data with modeled value and RPE estimates
    behavior = pd.read_csv(behavior_path)

    # Extract the correct subnum and runnum from behavioral data
    run_behavior = behavior.query('subnum == %d & session == %d'%(int(subnum), int(runnum)))

    # Demean columns that might be used for parametric regressors
    demean_cols = ['probFractalDraw', 'reward', 'leftFractalRpe', 'leftBundleValAdv','rightFractalRpe', 'rpeLeftRightSum','valChosen', 'valUnchosen', 'valChosenLottery', 'valUnchosenLottery', 'valChosenFractal', 'valUnchosenFractal', 'valBundleSum', 'valChosenMinusUnchosen', 'valSumTvpFrac', 'valSumTvwpFrac', 'valSumQvpFrac', 'valSumQvwpFrac']
    demean_cols = [i for i in demean_cols if i in run_behavior.columns]
    demean_df = run_behavior[demean_cols]
    demean_df = demean_df - demean_df.mean()

    # Get regressors for the model
    regs = get_model_regs(mnum)

    # Get mean durations if parametric rt regressors will be included

    for reg in regs:
        if reg == "fractalProb_ev":
            cond_fractalProb_ev = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_ev['trial_type'] = 'fractalProb_ev'
            cond_fractalProb_ev['modulation'] = 1

        if reg == "fractalProb_par":
            cond_fractalProb_par = events.query('trial_type == "fractalProb"')[['onset', 'duration']].reset_index(drop=True)
            cond_fractalProb_par['trial_type'] = 'fractalProb_par'
            cond_fractalProb_par['modulation'] = demean_df['probFractalDraw'].reset_index(drop=True)

        if reg == 'choiceShift_st':
            cond_choiceShift_st = pd.DataFrame(events.query('trial_type == "stimulus"')['onset']+events.query('trial_type == "stimulus"')['duration'], columns = ['onset'])
            cond_choiceShift_st['duration'] = 0
            cond_choiceShift_st['trial_type'] = 'choiceShift_st'
            cond_choiceShift_st['modulation'] = 1

    # List of var names including 'cond'
    toconcat = [i for i in dir() if 'cond' in i]
    tmp = {}
    for i in toconcat:
        tmp.update({i:locals()[i]})
    formatted_events = pd.concat(tmp, ignore_index=True)

    formatted_events = formatted_events.sort_values(by='onset')
    formatted_events = formatted_events[['onset', 'duration', 'trial_type', 'modulation']].reset_index(drop=True)
    return formatted_events

def make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, hrf_model = 'spm', drift_model='cosine'):

    tr = get_from_sidecar(subnum, runnum, 'RepetitionTime', data_path)

    # this does not exist in the sidecars. I can either add a function to bidsify_helpers to extract this from par files
    # or i could read in the preprocessed functional files and the get the fourth dimension from that
    # the second is probably more error-proof for getting the correct information though it would have been nice to have this in the metadata
    # n_scans = get_from_sidecar(subnum, runnum, 'dcmmeta_shape', data_path)[3]

    frame_times = np.arange(n_scans) * tr

    formatted_events = get_events(subnum, runnum, mnum, data_path, behavior_path)
    formatted_confounds = get_confounds(subnum, runnum, data_path)

    #takes care of derivative for condition columns if specified in hrf_model
    design_matrix = make_first_level_design_matrix(frame_times,
                                               formatted_events,
                                               drift_model=drift_model,
                                               add_regs= formatted_confounds,
                                               hrf_model=hrf_model)

    return design_matrix

# Fixed effects analysis for all runs of subjects based on tutorial on:
# https://nilearn.github.io/stable/auto_examples/04_glm_first_level/plot_fiac_analysis.html#sphx-glr-auto-examples-04-glm-first-level-plot-fiac-analysis-py
def run_level1(subnum, mnum, data_path, behavior_path, out_path, save_contrast = True, output_type='effect_size', noise_model='ar1', hrf_model='spm', drift_model='cosine',smoothing_fwhm=5):

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    contrasts_path = os.path.join(out_path, "sub-%s/contrasts"%(subnum))
    if not os.path.exists(contrasts_path):
        os.makedirs(contrasts_path)

    sub_events = glob.glob(os.path.join(data_path, 'sub-%s/func/sub-%s_task-bundles_run-*_events.tsv'%(subnum, subnum)))
    sub_events.sort()

    #fmri_img: path to preproc_bold's that the model will be fit on
    fmri_img = glob.glob(os.path.join(data_path,"derivatives/sub-%s/func/sub-%s_task-bundles_run-*_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"%(subnum, subnum)))
    fmri_img.sort()

    if len(fmri_img) == 0:
        print("***********************************************")
        print("No pre-processed BOLD found for sub-%s "%(subnum))
        print("***********************************************")
    else:
        if len(fmri_img) != 3:
            print("***********************************************")
            print("Found fewer than 3 runs for sub-%s "%(subnum))
            print("***********************************************")

        design_matrix = []
        for run_events in sub_events:
            runnum = re.findall('\d+', os.path.basename(run_events))[1] #index 0 is subnum, index 1 for runnum
            run_design_matrix = make_level1_design_matrix(subnum, runnum, mnum, data_path, behavior_path, hrf_model = hrf_model, drift_model=drift_model)
            design_matrix.append(run_design_matrix)
            print("***********************************************")
            print("Saving design matrix for sub-%s run-%s"%(subnum, runnum))
            print("***********************************************")
            run_design_matrix.to_csv(os.path.join(out_path, 'sub-%s/sub-%s_run-%s_%s_level1_design_matrix.csv' %(subnum, subnum, runnum, mnum)), index=False)

        #define GLM parmeters
        img_tr = get_from_sidecar(subnum, '1', 'RepetitionTime', data_path) #get tr info from runnum = "1" since it's the same for all runs
        mask_img = nib.load(os.path.join(data_path,'derivatives/sub-%s/func/sub-%s_task-bundles_run-1_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'%(subnum, subnum))) #mask image from first run since it should be the same for all runs
        fmri_glm = FirstLevelModel(t_r=img_tr,
                               noise_model=noise_model,
                               hrf_model=hrf_model,
                               drift_model=drift_model,
                               smoothing_fwhm=smoothing_fwhm,
                               mask_img=mask_img,
                               subject_label=subnum,
                               minimize_memory=True)

        #fit glm to run image using run events
        print("***********************************************")
        print("Running fixed effects GLM for all runs of sub-%s"%(subnum))
        print("***********************************************")
        fmri_glm = fmri_glm.fit(fmri_img, design_matrices = design_matrix)

        print("***********************************************")
        print("Saving GLM for sub-%s"%(subnum))
        print("***********************************************")
        fn = os.path.join(out_path, 'sub-%s/sub-%s_%s_level1_glm.pkl' %(subnum, subnum, mnum))
        f = open(fn, 'wb')
        pickle.dump(fmri_glm, f)
        f.close()

        # You don't need this step for group level analyses. You can load FirstLevelModel objects for SecondLevelModel.fit() inputs
        # But if you want to use images instead of FirstLevelModel objects as the input then `output_type` should be `effect_size` so you save the parameter maps and not other statistics
        if save_contrast:
            print("***********************************************")
            print("Running contrasts for sub-%s"%(subnum))
            print("***********************************************")
            contrasts = make_contrasts(design_matrix[0], mnum) #using the first design matrix since contrasts are the same for all runs
            for index, (contrast_id, contrast_val) in enumerate(contrasts.items()):
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= output_type)
                nib.save(contrast_map, '%s/sub-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, mnum, contrast_id, output_type))
                contrast_map = fmri_glm.compute_contrast(contrast_val, output_type= 'stat') #also save tmaps
                nib.save(contrast_map, '%s/sub-%s_%s_%s_%s.nii.gz'%(contrasts_path, subnum, mnum, contrast_id, 'tmap'))
            print("***********************************************")
            print("Done saving contrasts for sub-%s"%(subnum))
            print("***********************************************")

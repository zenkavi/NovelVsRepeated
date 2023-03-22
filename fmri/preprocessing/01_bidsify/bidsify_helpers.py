import glob
import json
import numpy as np
import os
import pandas as pd
import random
import scipy.io as sio
import shutil

# In this directory each session of each subject has its own directory that contains all the data that was collected in the scanner.
# In addition to anatomical and functional data these directories also include fieldmaps # (not used due to ambiguity regarding the TotalReadoutTime from Philips scanners) and another unidentified acquisition
orig_path = '/Users/zeynepenkavi/Downloads/alldata/data_task/pilot5_fmri_1/data_experiment/results/fmri_rawdata'

# In this directory only the anatomical and functional data from the previous directory are placed into bids-compliant subject and session directories
raw_path = '/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri'

bids_path = '/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri'

subnums = ['601', '609', '611', '619', '621', '629']

sessions = ['01', '02', '03']

data_types = ['anat', 'func']

misc_files = ['dataset_description.json', 'participants.json', 'README', 'CHANGES']

def make_bids_dirs(bids_path_ = bids_path, subnums_ = subnums, sessions_ = sessions, data_types_ = data_types):
    for cur_sub in subnums_:
        for cur_ses in sessions_:
            for cur_dt in data_types_:
                cur_dir = os.path.join(bids_path_, 'sub-'+cur_sub, 'ses-'+cur_ses, cur_dt)
                if not (os.path.exists(cur_dir)):
                    os.makedirs(cur_dir)

def add_misc_bids_files(bids_path_ = bids_path, misc_files_ = misc_files):
    for cur_mf in misc_files_:
        if not os.path.exists(os.path.join(bids_path_, cur_mf)):
            cur_template = os.path.join(os.getcwd(), 'bids_templates', cur_mf)
            cur_fn = os.path.join(bids_path_, cur_mf)
            shutil.copy(cur_template, cur_fn)
        else:
            print(cur_mf + " already exists in " + bids_path_)
    if not os.path.exists(os.path.join(bids_path_, 'participants.tsv')):
        print("Don't forget to create participants.tsv!")

# Minimally organize fmri data from the original path by taking out only the parts you need for the bidsification
def copy_orig_to_raw_fmri(orig_path_ = orig_path, raw_path_ = raw_path, subnums_ = subnums, sessions_ = sessions, data_types_ = data_types, ses_dict_ = {'d3': 'ses-01', 'd7': 'ses-02', 'd11': 'ses-03'}):

    make_bids_dirs(bids_path_ = raw_path, subnums_ = subnums, sessions_ = sessions, data_types_ = data_types)

    fmri_dirs = [i for i in os.listdir(orig_path) if i != '.DS_Store']

    for cur_dur in fmri_dirs:
        cur_sub = cur_dir.split('_')[3][-3:]
        cur_ses = ses_dict_[cur_dir.split('_')[4]]
        cur_raw_func_path = os.path.join(raw_path_, 'sub-'+cur_sub, cur_ses, 'func/')
        cur_raw_anat_path = os.path.join(raw_path_, 'sub-'+cur_sub, cur_ses, 'anat/')
        all_files = os.listdir(os.path.join(orig_path_, cur_dir))
        cur_func_imgs = [i for i in all_files if 'fmri_run' in i]
        cur_anat_imgs = [i for i in all_files if 't1w3danat' in i]

        for cur_fi in cur_func_imgs:
            shutil.copy(os.path.join(orig_path, cur_dir, cur_fi), cur_raw_func_path)

        for cur_ai in cur_anat_imgs:
            shutil.copy(os.path.join(orig_path, cur_dir, cur_ai), cur_raw_anat_path)


# Note: This is written to work on already minimally organized data where each subjects' data is placed into bids-compliant subject and session directories
# Note: The default arguments are specified as how they might be mounted with a docker image (unlike the local paths used in the previous functions above)
def bidsify_func_imgs(raw_path_ = '/raw', bids_path_ = '/bids', subnums_ = subnums, sessions_ = sessions, func_key_ = 'fmri', task_name_dict_ = {'Run1' : 'yesNo', 'Run2': 'yesNo', 'Run3': 'binaryChoice'}):

    for cur_sub in subnums_:
        for cur_ses in sessions_:

            # Check if the raw path to copy data from exists. If not, continue to the next iteration.
            cur_raw_dir = os.path.join(raw_path_, 'sub-'+cur_sub, 'ses-'+cur_ses)
            if not (os.path.exists(cur_raw_dir)):
                print('Path does not exist: ' + cur_raw_dir)
                continue

            # Check if the bids path that will be populated exists. If not, create it.
            cur_bids_dir = os.path.join(bids_path_, 'sub-'+cur_sub, 'ses-'+cur_ses, 'func')
            if not (os.path.exists(cur_bids_dir)):
                print('Creating bids path: ' + cur_bids_dir)
                os.makedirs(cur_bids_dir)

            # Copy func files to appropriate directory
            cur_raw_files = os.listdir(cur_raw_dir)
            cur_func_files = [i for i in cur_raw_files if func_key_ in i]
            for cur_func_file in cur_func_files:
                shutil.copy(os.path.join(cur_raw_dir, cur_func_file), os.path.join(cur_bids_dir, cur_func_file))

            # run dcm2niix
            print("Running dcm2niix for %s ..."%(cur_bids_dir))
            os.system('dcm2niix -ba y -z y %s' %(cur_bids_dir))

            # remove par/rec files from bids_dir (their names will be unaffected from the dcm2niix conversion)
            trsh = [os.remove(os.path.join(cur_bids_dir, i)) for i in cur_func_files]

            # rename dcm2niix output
            conv_out = os.listdir(cur_bids_dir)
            for i in conv_out:
                this_task = task_name_dict_.get(i.split('_')[2])
                this_acq_num = ['0'+s for s in i.split('_')[5].split('.')[0] if s.isdigit()][0]
                this_runnum = ['0'+s for s in i.split('_')[2] if s.isdigit()][0]
                this_ext = i.split('_')[5].split('.')[1]
                if this_ext == 'nii':
                    this_ext = 'nii.gz'
                # new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_task-' + this_task + '_acq-' + this_acq_num + '_run-' + this_runnum + '_bold.' + this_ext
                new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_task-' + this_task + '_run-' + this_runnum + '_bold.' + this_ext
                print("Renaming " + i + " to " + new_name + "...")
                os.rename(os.path.join(cur_bids_dir, i), os.path.join(cur_bids_dir, new_name))

# Note: This is written to work on already minimally organized data where each subjects' data is placed into bids-compliant subject and session directories
# Note: The default arguments are specified as how they might be mounted with a docker image (unlike the local paths used in the previous functions above)
def bidsify_anat_imgs(raw_path_ = '/raw', bids_path_ = '/bids', subnums_ = subnums, sessions_ = sessions, anat_key_ = 't1w3danat', contr_name_dict_ = {'T1w3DAnat': 'T1w'}):

    for cur_sub in subnums_:
        for cur_ses in sessions_:

            # Check if the raw path to copy data from exists. If not, continue to the next iteration.
            cur_raw_dir = os.path.join(raw_path_, 'sub-'+cur_sub, 'ses-'+cur_ses)
            if not (os.path.exists(cur_raw_dir)):
                print('Path does not exist: ' + cur_raw_dir)
                continue

            # Check if the bids path that will be populated exists. If not, create it.
            cur_bids_dir = os.path.join(bids_path_, 'sub-'+cur_sub, 'ses-'+cur_ses, 'anat')
            if not (os.path.exists(cur_bids_dir)):
                print('Creating bids path: ' + cur_bids_dir)
                os.makedirs(cur_bids_dir)

            # Copy func files to appropriate directory
            cur_raw_files = os.listdir(cur_raw_dir)
            cur_anat_files = [i for i in cur_raw_files if anat_key_ in i]
            for cur_anat_file in cur_anat_files:
                shutil.copy(os.path.join(cur_raw_dir, cur_anat_file), os.path.join(cur_bids_dir, cur_anat_file))

            # run dcm2niix
            print("Running dcm2niix for %s ..."%(cur_bids_dir))
            os.system('dcm2niix -ba y -z y %s' %(cur_bids_dir))

            # remove par/rec files from bids_dir (their names will be unaffected from the dcm2niix conversion)
            trsh = [os.remove(os.path.join(cur_bids_dir, i)) for i in cur_anat_files]

            # rename dcm2niix output
            conv_out = os.listdir(cur_bids_dir)
            for i in conv_out:
                this_contr = contr_name_dict_.get(i.split('_')[1])
                this_acq_num = ['0'+s for s in i.split('_')[7].split('.')[0] if s.isdigit()][0]
                this_ext = i.split('_')[7].split('.')[1]
                if this_ext == 'nii':
                    this_ext = 'nii.gz'
                # new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_acq-' + this_acq_num + '_' + this_contr + '.' + this_ext
                new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_' + this_contr + '.' + this_ext
                print("Renaming " + i + " to " + new_name + "...")
                os.rename(os.path.join(cur_bids_dir, i), os.path.join(cur_bids_dir, new_name))


# add extra fields to sidecars: TaskName, SliceTiming
SliceTiming = [0.0, 0.05833, 0.11666, 0.17499, 0.23332, 0.29165, 0.34998, 0.40831, 0.46664, 0.52497, 0.5833, 0.64163, 0.69996, 0.75829, 0.81662, 0.87495, 0.93328, 0.99161, 1.04994, 1.10827, 1.1666, 1.22493, 1.28326, 1.34159, 1.39992, 1.45825, 1.51658, 1.57491, 1.63324, 1.69157, 1.7499, 1.80823, 1.86656, 1.92489, 1.98322, 2.04155, 2.09988, 2.15821, 2.21654, 2.27487, 2.3332, 2.39153]
# Instead of doing this for all subjects and sessions added one top level sidecar for each task manually but validator complains just with that so adding to all
def add_func_metadata(bids_path_ = '/bids', add_fields = {'yesNo': {'TaskName': 'yesNo', 'SliceTiming': SliceTiming}, 'binaryChoice': {'TaskName': 'binaryChoice', 'SliceTiming': SliceTiming}}):

    all_func_sidecars = glob.glob(bids_path_ + '/*/*/func/*_bold.json')

    for cur_sidecar in all_func_sidecars:
        f = open(cur_sidecar,"r")
        data = f.read()
        tmp = json.loads(data)

        if 'SliceTiming' in tmp.keys():
            print('Sidecar contains SliceTiming. Moving onto next. (%s)' %(os.path.basename(cur_sidecar)))
            continue

        else:
            if 'yesNo' in os.path.basename(cur_sidecar):
                cur_task = 'yesNo'
            else:
                cur_task = 'binaryChoice'
            print('Determined task name for %s as %s'%(os.path.basename(cur_sidecar), cur_task))

            print('Updating sidecar...')
            tmp.update(add_fields[cur_task])

            print('Saving updated sidecar...')
            tempfile = os.path.join(os.path.dirname(cur_sidecar), 'tmp'+str(random.randint(0, 1000))+'.json')
            with open(tempfile, 'w') as f:
                json.dump(tmp, f, indent=4)

            # rename temporary file replacing old file
            print('Replacing old sidecar...')
            os.rename(tempfile, cur_sidecar)

# Copy mat files from original path into raw fmri path
def copy_func_timing(orig_path_ = '/alldata/data_task/pilot5_fmri_1/data_experiment/results', raw_path_ = '/raw', ses_dict_ = {'day3': 'ses-01', 'day7': 'ses-02', 'day11': 'ses-03'}):

    task_mats = glob.glob(orig_path_ + '/*/*/task*.mat')

    # loop through all mats
    for cur_mat in task_mats:
        # read it in
        tmp = sio.loadmat(cur_mat)
        # check if it has a 'timing' object
        if 'timing' in tmp.keys():
            # if yes
            #determine the correct raw_path_  by splitting the file name and extracting the subject and session info
            cur_fn = os.path.basename(cur_mat)
            cur_sub = cur_fn.split('_')[1]
            cur_sub = cur_sub.replace('j', '-')
            cur_ses = cur_fn.split('_')[2].split('.')[0]
            cur_ses = ses_dict_.get(cur_ses)
            cur_raw = os.path.join(raw_path_, cur_sub, cur_ses)
            # copy it there
            shutil.copy(cur_mat, cur_raw)
        else:
            continue

def bidsify_func_events(raw_path_ = '/raw', bids_path_ = '/bids', ses_dict_ = {'day3': 'ses-01', 'day7': 'ses-02', 'day11': 'ses-03'}, task_name_dict_ = {'taskYN': 'yesNo', 'taskBC': 'binaryChoice'}, run_dict_ = {'session2': 'run-01', 'session3': 'run-01', 'session4': 'run-02'}):
# onset duration trial_type [amplitude]
    timing_mats = glob.glob(raw_path_ + '/*/*/*.mat')

    for cur_timing in timing_mats:
        print("Processing: %s"%os.path.basename(cur_timing))

        tmp = sio.loadmat(cur_timing, squeeze_me=True)
        timing = tmp['timing']
        timing_vals = timing.item()

        if len(timing.dtype)>6:
            timing_keys = ['Begin', 'onset', 'feedbackOn', 'crossStart', 'crossEnd', 'End', 'session'] #session only exists for the later YN run
            tmp_dict = dict(zip(timing_keys, timing_vals))
            cut_dict = dict()
            for k in timing_keys:
                half_len = int(len(tmp_dict[k])/2)
                cut_dict[k] = tmp_dict[k][-half_len:]
        else:
            timing_keys = ['Begin', 'onset', 'feedbackOn', 'crossStart', 'crossEnd', 'End']
            cut_dict = dict(zip(timing_keys, timing_vals))

        run_begin = float(cut_dict['Begin'])
        run_end = float(cut_dict['End']) - run_begin
        del cut_dict['Begin']
        del cut_dict['End']
        if 'session' in timing_keys:
            del cut_dict['session']

        timing_df = pd.DataFrame(cut_dict) - run_begin
        stim_timing = pd.DataFrame({'onset': timing_df['onset'], 'duration':  timing_df['feedbackOn'] - timing_df['onset'], 'trial_type': 'stim'})
        feedback_timing = pd.DataFrame({'onset': timing_df['feedbackOn'], 'duration':  np.concatenate([np.array(timing_df['crossStart'][1:]), [run_end]]) - timing_df['feedbackOn'], 'trial_type': 'feedback'})
        cross_timing = pd.DataFrame({'onset': timing_df['crossStart'][1:], 'duration': timing_df['crossEnd'][1:] - timing_df['crossStart'][1:], 'trial_type': 'fixCross'})
        run_events = pd.concat([stim_timing, feedback_timing, cross_timing]).sort_values(by=['onset']).reset_index(drop=True)

        split_cur_timing = os.path.basename(cur_timing).split('.')[0].split('_')
        cur_sub = split_cur_timing[1][-3:]
        cur_ses = ses_dict_[split_cur_timing[2]]
        cur_task = task_name_dict_[split_cur_timing[0]]
        if cur_task == "binaryChoice":
            cur_run = 'run-03'
        else:
            cur_run = run_dict_[split_cur_timing[3]]
        cur_bids_fn = 'sub-' + cur_sub + '/'+ cur_ses + '/func/sub-' + cur_sub + '_' + cur_ses + '_task-' + cur_task + '_' + cur_run + '_events.tsv'

        print("Saving: %s"%(cur_bids_fn))
        run_events.to_csv(os.path.join(bids_path_, cur_bids_fn), sep="\t", index=False)

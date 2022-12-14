import os
import shutil
import json
import glob
import scipy.io as sio

# In this directory each session of each subject has its own directory that contains all the data that was collected in the scanner.
# In addition to anatomical and functional data these directories also include fieldmaps # (not used due to ambiguity regarding the TotalReadoutTime from Philips scanners) and another unidentified acquisition
# raw_data_path = '/Users/zeynepenkavi/Downloads/alldata/data_task/pilot5_fmri_1/data_experiment/results/fmri_rawdata'

# In this directory only the anatomical and functional data from the previous directory are placed into bids-compliant subject and session directories
raw_data_path = '/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri'

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
                new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_task-' + this_task + '_acq-' + this_acq_num + '_run-' + this_runnum + '_bold.' + this_ext
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
                new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_acq-' + this_acq_num + '_' + this_contr + '.' + this_ext
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

def copy_func_timing(orig_path_ = '/alldata', raw_path_ = '/raw', subj_dict_ = {'Subj_': 'sub-'}, ses_dict_ = {'day_3': 'ses-01', 'day_7': 'ses-02', 'day_11': 'ses-03'}):

    # day3mats
    # day7mats
    # day11mats

    # loop through all mats
    # read it in
    # sio.loadmat()
    # check if it has a 'timing' object
    # if yes determine the correct raw_path_ and copy it there
    # else continue

def bidsify_func_events(raw_path_ = '...', bids_path_ = '...', ):
# onset duration task_type [amplitude]


# The sent example looks like it just copies the log file and removes the header
# def bidsify_physio():

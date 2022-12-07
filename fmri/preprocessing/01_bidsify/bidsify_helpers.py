import os
import shutil

# In this directory each session of each subject has its own directory that contains all the data that was collected in the scanner.
# In addition to anatomical and functional data these directories also include fieldmaps # (not used due to ambiguity regarding the TotalReadoutTime from Philips scanners) and another unidentified acquisition
# raw_data_path = '/Users/zeynepenkavi/Downloads/alldata/data_task/pilot5_fmri_1/data_experiment/results/fmri_rawdata'

# In this directory only the anatomical and functional data from the previous directory are placed into bids-compliant subject and session directories
raw_data_path = '/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri'

bids_path = '/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri'

subnums = ['601', '609', '611', '619', '621', '629']

sessions = ['01', '02', '03']

data_types = ['anat', 'func']

misc_files = ['dataset_description.json', 'participants.json', 'README', 'CHANGES', 'LICENSE']

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
def bidsify_func_imgs(raw_path_ = '/raw', bids_path_ = '/bids', subnums_ = subnums, sessions_ = sessions, func_key_ = 'fmri', task_name_dict_ = {'Run1' : 'yes-no', 'Run2': 'yes-no', 'Run3': 'binary-choice'}):

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
            os.system('dcm2niix -ba y -z y %s' %(cur_bids_dir))

            # remove par/rec files from bids_dir
            trsh = [os.remove(os.path.join(cur_bids_dir, i)) for i in cur_func_files]

            # rename dcm2niix output
            conv_out = os.listdir(cur_bids_dir)
            for i in conv_out:
                this_task = task_name_dict_.get(i.split('_')[2])
                this_acq_num = i.split('_')[5].split('.')[0]
                this_runnum = ['0'+s for s in i.split('_')[2] if s.isdigit()][0]
                this_ext = i.split('_')[5].split('.')[1]
                if this_ext == 'nii':
                    this_ext = 'nii.gz'
                new_name = 'sub-' + cur_sub + '_ses-' + cur_ses + '_task-' + this_task + '_acq-' + this_acq_num + '_run-' + this_runnum + '_bold.' + this_ext
                os.rename(os.path.join(cur_bids_dir, i), os.path.join(cur_bids_dir, new_name))


# add extra fields to sidecars



# def bidsify_anat():

# def bidsify_physio():

# def bidsify_func_events():

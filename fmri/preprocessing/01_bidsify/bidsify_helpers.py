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
def bidsify_func_imgs(raw_path_, bids_path_, subnums_, sessions_, func_key_ = 'fmri', task_name_dict_ = {'Run1' : 'yes-no', 'Run2': 'yes-no', 'Run3': 'binary-choice'}):

    for cur_sub in subnums_:
        for cur_ses in sessions_:

            # Check if the raw path to copy data from exists. If not, continue to the next iteration.
            cur_raw_dir = os.path.join(raw_path_, 'sub-'+cur_sub, 'ses-'+cur_ses)
            if not (os.path.exists(cur_raw_dir)):
                print('Path does not exist: ' + cur_raw_dir)
                continue

            # Check if the bids path that will be populated exists. If not, create it.
            cur_bids_dir = os.path.join(bids_path_, 'sub-'+cur_sub, 'ses-'+cur_ses, func)
            if not (os.path.exists(cur_bids_dir)):
                os.makedirs(cur_bids_dir)

            # Copy func files to appropriate directory

            # run dcm2niix

            # rename

            # add extra fields to sidecars

            # remove par/rec files from bids_dir

# def bidsify_anat():

# def bidsify_physio():

# def bidsify_func_events():

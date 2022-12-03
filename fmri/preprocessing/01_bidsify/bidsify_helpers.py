import os
import shutil

# raw_data_path = '/Users/zeynepenkavi/Downloads/alldata/data_task/pilot5_fmri_1/data_experiment/results/fmri_rawdata'
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
                cur_dir = os.path.join(bids_path, 'sub-'+cur_sub, 'ses-'+cur_ses, cur_dt)
                if not (os.path.exists(cur_dir)):
                    os.makedirs(cur_dir)

def add_misc_bids_files(bids_path_ = bids_path, misc_files_ = misc_files):
    for cur_mf in misc_files_:
        if not os.path.exists(os.path.join(bids_path, cur_mf)):
            cur_template = os.path.join(os.getcwd(), 'bids_templates', cur_mf)
            cur_fn = os.path.join(bids_path, cur_mf)
            shutil.copy(cur_template, cur_fn)
        else:
            print(cur_mf + " already exists in " + bids_path)
    if not os.path.exists(os.path.join(bids_path, 'participants.tsv')):
        print("Don't forget to create participants.tsv!")

# def bidsify_func_events():

# def bidsify_anat():

# def bidsify_func_imgs():

# def bidsify_physio():

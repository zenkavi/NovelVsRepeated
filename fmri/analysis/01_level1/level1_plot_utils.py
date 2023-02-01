import os
import glob
import pandas as pd
import numpy as np
import nibabel as nib
from nilearn.plotting import plot_stat_map
import matplotlib.pyplot as plt
from nilearn.image import new_img_like, load_img, math_img, get_data
import itertools

fig_path = '/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/fmri/analysis/01_level1/figs'

base_path = '/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri'
contrasts_path = os.path.join(base_path, 'derivatives/nilearn/glm/level1')


def label_matrix_row_cols(fig, a, cols, rows):
#     https://stackoverflow.com/questions/25812255/row-and-column-headers-in-matplotlibs-subplots
    for ax, col in zip(a[0], cols):
        ax.set_title(col)

    for ax, row in zip(a[:,0], rows):
        ax.set_ylabel(row, rotation=0, size='large')

def plot_stat_map_matrix(reg, task, mnum, contrasts_path, map_type,
                         cut_coords = (10), threshold = 2, display_mode = 'y',
                         black_bg = False, vmax = 6, fig_w = 12, fig_h = 24,
                         space = 'MNI152NLin2009cAsym_res-2',
                         subnums = ['601', '609', '611', '619', '621', '629'], sessions = ['01', '02', '03']):
    
    # Example Usage:

    # fig_path = '/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/fmri/analysis/01_level1/figs'

    # base_path = '/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri'
    # contrasts_path = os.path.join(base_path, 'derivatives/nilearn/glm/level1')

    # import matplotlib.pyplot as plt

    # task = 'yesNo'
    # mnum = 'model2'
    # map_type = 'tmap'


    # figs_list = [{'reg': 'valHT_par', 'task': task, 'cut': -6, 'disp_mode': 'x'},
    #             {'reg': 'valHT_par', 'task': task, 'cut': 4, 'disp_mode': 'x'},
    #             {'reg': 'valHT_par', 'task': task, 'cut': 8, 'disp_mode': 'y'},
    #             {'reg': 'valHT_par', 'task': task, 'cut': 40, 'disp_mode': 'y'}]


    # out_path = os.path.join(fig_path, task, mnum)
    # if not os.path.exists(out_path):
    #     os.makedirs(out_path)

    # for cur_dict in figs_list:
    #     reg = cur_dict['reg']
    #     task = cur_dict['task']
    #     cut = cur_dict['cut']
    #     disp_mode = cur_dict['disp_mode']

    #     plot_stat_map_matrix(reg, task, mnum, contrasts_path, map_type, cut_coords = [cut, ], display_mode = disp_mode)

    #     fig_fn = task + '_' + mnum + '_' + reg + '_' + map_type + '_matrix_' + disp_mode + '_'+ str(cut) + '.jpeg'
    #     plt.savefig(os.path.join(out_path, fig_fn), transparent=False, pad_inches = 0.05, bbox_inches = 'tight')

    fig, a = plt.subplots(len(subnums), len(sessions), figsize=(fig_w, fig_h))

    cols = ['ses-'+i for i in sessions]

    for ax, col in zip(a[0], cols):
        ax.set_title(col)

    fig.suptitle('%s-%s-thr-%s'%(task, reg, str(threshold)))
    fig.subplots_adjust(top=0.95)

    for i, cur_sub in enumerate(subnums):
        for j, cur_ses in enumerate(sessions):

            anat_path = os.path.join(base_path, 'derivatives/sub-' + cur_sub + '/anat')

            stat_map_fn = 'sub-' + cur_sub + '_ses-' + cur_ses + '_task-' + task + '_space-' + space + '_' + mnum + '_' + reg + '_' + map_type + '.nii.gz'
            bg_img_fn = 'sub-'+ cur_sub + '_space-' + space + '_desc-preproc_T1w.nii.gz'

            cur_img = os.path.join(contrasts_path, task, mnum, 'sub-'+cur_sub, 'ses-'+cur_ses, 'contrasts', stat_map_fn)

            bg_img = os.path.join(anat_path, bg_img_fn)

            plot_stat_map(cur_img,
                          bg_img = bg_img,
                          cut_coords = cut_coords,
                          threshold = threshold,
                          draw_cross=False,
                          display_mode = display_mode,
                          black_bg = black_bg,
                          axes = a[i, j],
                          vmax = vmax)




def plot_diff_stat_map_matrix(reg, task, mnum, contrasts_path,
                         cut_coords = [8,], threshold = 2, display_mode = 'y',
                         black_bg = False, vmax = 6, fig_w = 16, fig_h = 18,
                         space = 'MNI152NLin2009cAsym_res-2',
                         subnums = ['601', '609', '611', '619', '621', '629']):
    
    fig, a = plt.subplots(len(subnums), 4, figsize=(fig_w, fig_h))
    
    cols = ['ses-01', 'ses-02_min_ses-01', 'ses-03_min_ses-01', 'ses-03_min_ses-02']

    for ax, col in zip(a[0], cols):
        ax.set_title(col)

    fig.suptitle('%s-%s-thr-%s'%(task, reg, str(threshold)))
    fig.subplots_adjust(top=0.95)

    for i, cur_sub in enumerate(subnums):
        
        anat_path = os.path.join(base_path, 'derivatives/sub-' + cur_sub + '/anat')
        bg_img_fn = 'sub-'+ cur_sub + '_space-' + space + '_desc-preproc_T1w.nii.gz'
        bg_img = os.path.join(anat_path, bg_img_fn)
        
        col1_img_fn = 'sub-%s_%s_task-%s_space-%s_%s_%s_tmap.nii.gz' %(cur_sub, 'ses-01', task, space, mnum, reg)
        col1_img = os.path.join(contrasts_path, task, mnum, 'sub-'+cur_sub, 'ses-01/contrasts', col1_img_fn)
        
        plot_stat_map(col1_img,
                      bg_img = bg_img,
                      cut_coords = cut_coords,
                      threshold = threshold,
                      draw_cross=False,
                      display_mode = display_mode,
                      black_bg = black_bg,
                      axes = a[i, 0],
                      vmax = vmax)
        
        for j, cur_col in enumerate(cols[1:]):
                        
            fn = 'sub-%s_%s_task-%s_space-%s_%s_%s_tmap.nii.gz' %(cur_sub, cur_col, task, space, mnum, reg)
            tmap = os.path.join(contrasts_path, task, mnum, 'sub-'+cur_sub, cur_col+'/contrasts', fn)
            
            plot_stat_map(tmap,
                          bg_img = bg_img,
                          cut_coords = cut_coords,
                          threshold = threshold,
                          draw_cross=False,
                          display_mode = display_mode,
                          black_bg = black_bg,
                          axes = a[i, j+1],
                          vmax = vmax)

def get_mean_desmat_cor(task, mnum, l1_path, save_ = True, float_format_ = '%.4f'):

    des_mats = glob.glob(os.path.join(l1_path, task, mnum, '**/**/*design_matrix*'))

    beh_regs = pd.read_csv(des_mats[0]).columns
    to_filter = ['trans', 'rot', 'drift', 'framewise', 'scrub', 'constant', 'dvars']
    beh_regs = [x for x in beh_regs if all(y not in x for y in to_filter)]

    cor_mats = []
    for i, cur_des_mat in enumerate(des_mats):
        cur_des_mat = pd.read_csv(cur_des_mat)
        cor_mats.append(cur_des_mat[beh_regs].corr())

    df_concat = pd.concat(cor_mats)
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()
    
    if save_:
        out_path = os.path.join(l1_path, task, mnum)
        df_means.to_csv(os.path.join(out_path, 'task-%s_%s_mean_desmat_cor.csv'%(task, mnum)), float_format = float_format_)

    return df_means
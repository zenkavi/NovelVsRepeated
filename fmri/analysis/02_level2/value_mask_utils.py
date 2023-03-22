import os
from nilearn.plotting import plot_stat_map
import matplotlib.pyplot as plt
from nilearn.image import new_img_like, load_img, math_img, get_data
import numpy as np
import pandas as pd

# Plot the conjunction mask of Barta et al. and Clithero et al.

mask_fn = '/Users/zeynepenkavi/Downloads/Bartra3A_and_Clithero3_meta_mask.nii'
plot_stat_map(mask_fn, draw_cross = False, cmap = 'green_transparent', colorbar = False)

def get_label_nums(roi_labels, lookup_file):
    
    if 'ROI_MNI_V4.txt' in lookup_file:
        lookup_data = pd.read_csv(lookup_file, sep='\t', header=None, names=["nom_l", "color"])
    else:
        lookup_data = pd.read_csv(lookup_file, sep='\t')
        
    roi_label_nums = list(lookup_data[lookup_data['nom_l'].isin(roi_labels)]['color'])
        
    return roi_label_nums

def make_mask_from_label_nums(label_nums, atlas_fn):
    
    atlas_data = get_data(atlas_fn)
    mask_data = np.where(np.isin(atlas_data, label_nums), 1, 0)
    mask_img = new_img_like(atlas_fn, mask_data)
    
    return mask_img

# Usage:

# v4_fn = '/Users/zeynepenkavi/Downloads/aal_for_SPM12/ROI_MNI_V4.txt'
# v4_atlas_fn = '/Users/zeynepenkavi/Downloads/aal_for_SPM12/ROI_MNI_V4.nii'

# ppc_roi_labels = ['Parietal_Inf_L', 'Parietal_Inf_R', 'Parietal_Sup_L', 'Parietal_Sup_R']
# lofc_roi_labels = ['Frontal_Mid_Orb_L', 'Frontal_Mid_Orb_R', 'Frontal_Inf_Orb_L', 'Frontal_Inf_Orb_R', 'Frontal_Sup_Orb_L', 'Frontal_Sup_Orb_R']
# mofc_roi_labels = ['Frontal_Med_Orb_L', 'Frontal_Med_Orb_R', 'Rectus_L', 'Rectus_R']
# dmpfc_roi_labels = ['Frontal_Sup_Medial_L', 'Frontal_Sup_Medial_R', 'Cingulum_Ant_L', 'Cingulum_Ant_R']
# dlpfc_roi_labels = ['Frontal_Mid_L', 'Frontal_Mid_R', 'Frontal_Sup_L', 'Frontal_Sup_R']
# vlpfc_roi_labels = ['Frontal_Inf_Oper_L', 'Frontal_Inf_Oper_R', 'Frontal_Inf_Tri_L', 'Frontal_Inf_Tri_R']
# LPFC = vlpfc_roi_labels + dlpfc_roi_labels + lofc_roi_labels
# MPFC = mofc_roi_labels + dmpfc_roi_labels


# ppc_label_nums = get_label_nums(ppc_roi_labels, v4_fn)
# ppc_mask = make_mask_from_label_nums(ppc_label_nums, v4_atlas_fn)
# plot_stat_map(ppc_mask, draw_cross = False, cmap = 'green_transparent', colorbar = False, title = "Iigaya et al. PPC ROI")
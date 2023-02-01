from argparse import ArgumentParser
import glob
import nibabel as nib
from nilearn.image import concat_imgs, smooth_img, mean_img, math_img, resample_to_img
import numpy as np
import os
import pandas as pd

from nilearn.glm.second_level import SecondLevelModel, non_parametric_inference

def run_level2(mnum, session, reg, sign, data_path, out_path, num_perm=5000, var_smooth=5):

    reg_path = "%s/%s_%s/%s"%(out_path, reg, mnum, session)
    if not os.path.exists(reg_path):
        os.makedirs(reg_path)

    suffix = reg + '_' + mnum + '_' + session

    # Tutorial for running level 2 from parameter estimate maps
    # https://nilearn.github.io/stable/auto_examples/05_glm_second_level/plot_second_level_one_sample_test.html#sphx-glr-auto-examples-05-glm-second-level-plot-second-level-one-sample-test-py
    input_path = "%s/sub-*/%s/contrasts"%(data_path, session)

    level1_images = glob.glob('%s/sub-*_%s_effect_size.nii.gz'%(input_path, reg))
    level1_images.sort()

    second_level_input = level1_images
    design_matrix = pd.DataFrame([1] * len(second_level_input), columns=['intercept'])

    # Don't need these because non_parametric_inference computes the same uncorrected tmap
    # But save them anyway so you don't have to wait for the permutation test and this is very quick
    # Check if it's already there first though, so you don't do it twice unnecessarily
    if not os.path.exists('%s/%s_unc_tmap.nii.gz'%(reg_path, suffix)):
        second_level_model = SecondLevelModel(smoothing_fwhm=var_smooth)
        second_level_model = second_level_model.fit(second_level_input, design_matrix=design_matrix)

        t_map = second_level_model.compute_contrast(output_type='stat')

        print("***********************************************")
        print("Saving uncorrected tmap for %s"%(suffix))
        print("***********************************************")

        nib.save(t_map, '%s/%s_unc_tmap.nii.gz'%(reg_path, suffix))

    suffix = suffix + '_' + str(sign)

    if sign == "neg":
        from nilearn.image import math_img
        second_level_input = [math_img("img*-1", img=i) for i in second_level_input]

    # The neg-log p-values obtained with nonparametric testing are capped at 3 if the number of permutations is 1e3.
    out_dict = non_parametric_inference(second_level_input,
                         design_matrix=design_matrix,
                         model_intercept=True, n_perm=num_perm,
                         two_sided_test=False, tfce = True,
                         smoothing_fwhm=var_smooth, n_jobs=7, verbose=1)


    print("***********************************************")
    print("Saving neg log p tfce for %s"%(suffix))
    print("***********************************************")

    # These are neg log p values. Threshold at 1 when visualizing
    nib.save(out_dict['logp_max_tfce'], '%s/%s_%s.nii.gz'%(reg_path, suffix, 'logp_max_tfce'))

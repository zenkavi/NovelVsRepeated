# BIDS matches from raw data

- sub-37102-ses-30989 -> SNS_MRI_OFM_Pilot_02  
- sub-37102-ses-30998 -> SNS_MRI_OFM_Pilot_02b_S32  
- sub-45087-ses-30993 -> SNS_MRI_OFM_Pilot_01  
- sub-45087-ses-30994 -> SNS_MRI_OFM_Pilot_01b_S32  
- sub-49636-ses-30978 -> SNS_MRI_OFM_Pilot_03 (no physio)  
- Not bidsified -> SNS_MRI_OFM_Pilot_03b_S32  

# Deciphered from `taskfmri_preprocessingSPM_func.m`

Anatomical file name structure: `sn_{DATE}_{TIME}_{ACQUISITION-NUMBER}_t1w3danat_4_real.nii`  
Functional file name structure: `sn_{DATE}_{TIME}_{ACQUISITION-NUMBER}_fmri_run{RUN}_split.nii`  
Fieldmap file name structire:   `sn_{DATE}_{TIME}_{ACQUISITION-NUMBER}_bomap_splitclea_ec1_typ{0/3}.nii`  
  - Unlike the other Nifti's the bomap Nifti's only have 1 par/rec file for 4 images. Based on the bidsified pilot data that was shared with us from UZH and info from the first post linked below these likely correspond to 2 magnitude (files with typ0.nii) and 2 phase images (files with typ3.nii).
  - Bidsified pilot data also suggests that the single `.par` file for the fieldmaps is converted to a sidecar for the phase images but the magnitude images don't have have `.json` sidecars

# General understanding

- This dataset is collected on a Phillips scanner  
- Bidsifying it will be different/trickier than anything I have worked with before (GE, Siemens)  
- Some helpful posts on how to bidsify. They both include external links on more general info on how to deal with Phillips scanner data too  
  - https://neurostars.org/t/converting-philips-fieldmaps-to-bids-and-finding-echo-time-1-and-echo-time-2/17592/4  
  - https://neurostars.org/t/deriving-slice-timing-order-from-philips-par-rec-and-console-information/17688  
  - UPDATE: As per Todd's recommendation, I will not use fieldmaps for sdc due to the unclarities in total readout time

# Strategy

## Failed attempt to use `bidsify` package

Tried Lukas Snoek's `bidsify` first instead of trying to deciphering every piece of info you need from the par/rec files to bidsify the dataset.  

https://github.com/NILAB-UvA/bidsify  
using the Docker image   
https://hub.docker.com/r/lukassnoek/bidsify  

```
export CONFIG_PATH=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/fmri/preprocessing/01_bidsify
export RAW_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri
export BIDS_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v $CONFIG_PATH:/config -v $RAW_PATH:/raw -v $BIDS_PATH:/bids lukassnoek/bidsify:0.3.7 bidsify -c /config/config.yml -d /raw -o /bids -v
```

But kept running into errors and couldn't get it to work out of the box. Instead I went through the package code and identified the useful functions for my purposes:  

- main > bidsify > **_process_directory** > **convert_mri** > **_get_extra_info_from_par_header**  
  `convert_mri` builds the `dcm2niix` command which looks something like:  

  ```
  dcm2niix -ba y -z y -f outputname /inputdir
  ```

  `dcm2niix` flags: `-ba` is for anonymized BIDS sidecars, `-z` is for different compressions and `-f` for file name.   

  `_get_extra_info_from_par_header` corrects the PAR headers to have the correct number of volumes for the run instead of max number of volumes that is there by default. In this dataset it shouldn't remove any volumes but just correct the header.  

- main > bidsify > **_add_missing_BIDS_metadata_and_save_to_disk**  
adds metadata to sidecars specified in the `metadata` section of `config.yml`. For functional files this includes `TaskName` and  `SliceEncodingDirection`. If you only use a selection of the `bidsify` functions then you'll have to make sure to add these sections later to pass the bidsvalidator

## My own `dcm2niix` + `bidsify_helpers`

Since I couldn't get `bidsify` to work I began using the docker image to interactively work through my own combination of `dcm2niix` and other helper code to reorganize data.

```
export RAW_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri

docker run --rm -it -v $RAW_PATH:/raw lukassnoek/bidsify:0.3.7 sh
dcm2niix -ba y -z y /raw
```

`dcm2niix` is a bit of blunt knife if you don't point it in the right direction.  
It works on all par/rec/nii files it finds in the directory *including all the subdirectories* and all outputs are placed in the top level directory (e.g. using the command above everything found in `raw/sub-601/ses-01`, `raw/sub-601/ses-02` etc are transformed and placed into `/raw`).  

### Naming

Raw --> default `dcm2niix` output --> BIDS  

sn_08092021_125537_3_1_fmri_run1_split.nii --> raw_fMRI_Run1_splitSENSE_20210908125537_3.nii  --> sub-601_ses-01_task-yesNo_run-01_bold.nii.gz  

sn_08092021_133855_8_1_t1w3danat_4_real.nii --> raw_T1w3DAnat_4_Realign_111_v01SE_20210908133855_8.nii --> sub-601_ses-01_T1w.nii.gz  

sub-601_ses-01_task-yesNo_run-01_events.tsv
sub-601_ses-01_task-binaryChoice_run-03_events.json

### Remove incomplete slices from `PAR` files

For `dcm2niix` to work on all functional runs I manually removed incomplete slices from the end of these files:

```
sn_08092021_102613_6_1_fmri_run2_split.par
sn_15092021_091932_5_1_fmri_run2_split.par
sn_16092021_122306_7_1_fmri_run3_split.par
sn_15092021_105445_7_1_fmri_run3_split.par
```

### Interactive testing of bidsify_helpers

Using the `bidsify` docker image

```
export CODE_PATH=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/fmri/preprocessing/01_bidsify
export RAW_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_rawfmri
export BIDS_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v $CODE_PATH:/code -v $RAW_PATH:/raw -v $BIDS_PATH:/bids -w /code lukassnoek/bidsify:0.3.7 sh

python
import os
import shutil
from bidsify_helpers import bidsify_func_imgs, bidsify_anat_imgs, add_func_metadata

subnums = ['601', '609', '611', '619', '621', '629']
sessions = ['01', '02', '03']

# If you run these functions without arguments they use the defaults specified in the script they are defined (ie. specifying subnums above doesn't matter)
bidsify_anat_imgs()
bidsify_func_imgs()
add_func_metadata()
```

### Additional fields for sidecars

Additional fields for sidecars: `TaskName`, `SliceEncodingDirection`, `SliceTiming` (the last two are not required for the validator, however, without them slice timing correction can't be done.)

Useful information re slice timing and slice encoding direction for Philips data:  
https://neurostars.org/t/deriving-slice-timing-order-from-philips-par-rec-and-console-information/17688  
https://neurostars.org/t/bids-fmriprep-specify-phase-encoding-direction-with-respect-to-qform-orientation-in-nifti-header/19800/2  

In the sidecars for the pilot data `SliceTiming` is defined as an array of 42 increasing values equally spaced between 0 and TR 2.49 secs. They are the same for all functional runs of all three subjects. These should indicate when each of the 42 slabs were recorded for each TR.  

BIDS recommends the `SliceEncodingDirection` parameter in metadata when providing `SliceTiming`. Based on the PAR header the "preparation direction" is `RL`. This is also what the pilot data sidecars have as the `PrepDirection` field, although this is not a valid BIDS field and it is not useful for BIDS-apps like fmriprep. Based on the above threads this axis corresponds to `i` for the `SliceEncodingDirection` in RAS orientation. But I also need to know the polarity (i.e. if it is `i` for LR or `i-` for RL).  

The PAR files and pilot BIDS indicated `RL`, and the Nifti header has `sform_xorient` and `qform_xorient` of `Right-to-Left` as well. But `taskfmri_preprocessingSPM_func.m` L147-165 indicates ascending (`spm.temporal.st.prefix = 'a'`) and continous slices (`spm.temporal.st.so = (1:42)`)
and based on the [SPM wiki](https://en.wikibooks.org/wiki/SPM/Slice_Timing#Philips_scanners) ascending single package on this axis is left to right.  

*Confusion and reaching out to Todd for clarification:*

- Todd says EPIs are continous ascending and Anterior to Posterior **phase encoding** but fieldmaps are right to left.  
- The matlab script `taskfmri_preprocessingSPM_func.m` doesn't say anything explicit about slice encoding direction. I assumed it would be right-left axis dues to the `PrepDirection` field.  
- The first post linked above mentions a `Slice scan order = ???HF???;` field from a console report that they use to infer the slice encoding direction. I haven't been able to locate such a field in the par files.   
- Do the par files for the fmap and anatomicals also have the same Prepdirection? Yes, so it's unclear whether this parameter refers to anything specific regarding the functional files.
- Do I even need the `SliceEncodingDirection` especially if I'm not using fieldmaps (that would have required me to specify a `PhaseEncodingDirection` which might have taken precedence over the `SliceEncodingDirection` for slice timing correction)? No, based on the fmriprep documentation this doesn't seem required.  
- 42 slices with 3 mm thickness in AP *slice encoding* direction would *not* make sense to capture the whole brain. The average brain dimensions are 140 x 167 x 93 (w x l x h). The only dimension where this would capture the whole brain is superior-inferior. Slice encoding direction is not the same thing as phase encoding direction!

*Confusion and reaching out to Mike for clarification:*

```
The normal to the slice planes (2D multislice images) is superior-inferior (or inferior-superior). The slices look like they might have been AC-PC aligned at the time of scanning.

So very similar to what most groups do routinely. Phase encoding is definitely AP/PA

Also, the 3D image dimensions are 80 x 80 x 42. There are very few situations where you wouldn't do this with 42 slices with 80 x 80 in-plane
```

### Physio

The sent example looks like it just copies the log file and removes the header  

# Move to S3

```
export BIDS_PATH=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_PATH:/bids amazon/aws-cli s3 sync /bids s3://novel-vs-repeated/fmri/bids
```

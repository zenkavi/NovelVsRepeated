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

But kept running into errors and couldn't get it to work out of the box. Instead went through the package code and identified the useful functions for my purposes:  

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
dcm2niix -ba y -z n /raw
```

Additional fields for sidecars: `TaskName`, `SliceEncodingDirection`, `SliceTiming` (the last two are not required for the validator, however, without them slice timing correction can't be done.)

**For physio**
https://github.com/lukassnoek/scanphyslog2bids  

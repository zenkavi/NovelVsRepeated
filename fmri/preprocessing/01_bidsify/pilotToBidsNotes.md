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
  - Bidsified pilot data also suggests that the single `.par` file for the fieldmaps is converted to a sidecard for the phase images but the magnitude images don't have have `.json` sidecars

# General understanding

- This dataset is collected on a Phillips scanner  
- Bidsifying it will be different/trickier than anything I have worked with before (GE, Siemens)  
- Some helpful posts on how to bidsify. They both include external links on more general info on how to deal with Phillips scanner data too  
  - https://neurostars.org/t/converting-philips-fieldmaps-to-bids-and-finding-echo-time-1-and-echo-time-2/17592/4  
  - https://neurostars.org/t/deriving-slice-timing-order-from-philips-par-rec-and-console-information/17688  
  - UPDATE: As per Todd's recommendation, I will not use fieldmaps for sdc due to the unclarities in total readout time

# Strategy

Try Lukas Snoek's packages first instead of trying to deciphering every piece of info you need from the par/rec files to bidsify the dataset.  

**For images**  
https://github.com/NILAB-UvA/bidsify  
using the Docker image   
https://hub.docker.com/r/lukassnoek/bidsify  

bidsify -c /Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/fmri/preprocessing/01_bidsify/comfig_yaml -d /Users/zeynepenkavi/Dowloads/overtrained_decisions_rawfmri -o /Users/zeynepenkavi/Dowloads/overtrained_decisions_bidsfmri -v -D

**For physio**
https://github.com/lukassnoek/scanphyslog2bids  

*Should you do any manual changes to the raw data file names to make it easier to process through bidsify?*
*E.g. changing the extension of scan or physio logs or functional runs to include task name in the file name*
*Note: "Importantly, any UNIX-style wildcard (e.g. *, ?, and [a,A,1-9]) can be used in the id values in these sections!"** so maybe I can use these for mappings too?

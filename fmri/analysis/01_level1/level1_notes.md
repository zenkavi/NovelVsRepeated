# Steps for level1 analyses

## Push behavior files to S3

```
export BIDS_DIR=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync  /bids s3://novel-vs-repeated/fmri/bids/ --exclude '*' --include '*beh/*'
```

## Push cluster setup scripts in `./cluster_scripts` to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/fmri/analysis:/fmri/analysis amazon/aws-cli s3 sync /fmri/analysis s3://novel-vs-repeated/fmri/analysis --exclude "*.DS_Store"
```

## Make key pair for `fmrianalysis-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name fmrianalysis-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/fmrianalysis-cluster.pem
chmod 400 $KEYS_PATH/fmrianalysis-cluster.pem
aws ec2 describe-key-pairs
```

## Create cluster config using `make_fmrianalysis_cluster_config.sh`

```
cd $STUDY_DIR/fmri/analysis/01_level1/cluster_scripts
sh make_fmrianalysis_cluster_config.sh
```

## Create cluster using the config

```
cd $STUDY_DIR/fmri/analysis/01_level1/cluster_scripts
pcluster create-cluster --cluster-name fmrianalysis-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

## Copy the preprocessed fmri data from s3 to cluster

```
pcluster ssh --cluster-name fmrianalysis-cluster -i $KEYS_PATH/fmrianalysis-cluster.pem

export DATA_PATH=/shared/fmri/bids

#aws s3 sync s3://novel-vs-repeated/fmri/bids $DATA_PATH --exclude '*' --include '*_events.tsv' --include '*_beh.tsv'
#aws s3 sync s3://novel-vs-repeated/fmri/bids/derivatives $DATA_PATH/derivatives --exclude '*' --include '*desc-preproc_bold.nii.gz' --include '*desc-confounds_timeseries.tsv' --include '*_desc-brain_mask.nii.gz'
```

## Test level1 analysis on single subject on head node

```

```

If a subject has fewer scans in different runs this might lead to a lower cosine drift order and causes problems when calculating contrasts combined with other runs because the design matrix ends up with one less column compared to other runs'. In such cases manual modification of the run design matrix might be necessary:

```
run_design_matrix['drift_17'] = 0
```

**Analyses in native space**
*Anatomicals*

Found in:
`bids/derivatives/sub-*/anat`

```
sub-*_desc-brain_mask.nii.gz # averaged brain mask in native space
sub-*_desc-preproc_T1w.nii.gz # averaged anatomical with skull in native space
```

*Functionals*

Found in:
`...`

```

```

### Level 1 for binaryChoice task

- 1 run per session. Each session has 100 trials with *~70 RE and ~30 HT* 
- Possible value regressors: [valueLeft_par, valueRight_par], [valueChosen_par, valueUnchosen_par], valChosenMinusUnchosen_par, valChosenPlusUnchosen_par
  - Value regressors would have the onset and duration of stim
- Other regressors: cross_ev, stim_ev, reward_ev, reward_par, condition (HT vs RE), choice (correct vs incorrect)
Questions:
  - Does how the value regressor correlates with each voxel change across sessions?
  - Does value regressor look different for HT vs RE trials?
  - Does the value regressor's correlations with each voxel change differently depending on the condition?
  - Should be able to model changes across sessions in a single model with interactions of the value and type regressors with session but you'd still want the (posthoc) maps for each case (session 1 + HT + value etc.)
  bold ~ value * stim_type * session

### Level 1 for yesNo task

- 2 runs per session
- Possible value regressors: [valueReference, valueStim], [valueChosen, valueUnchosen], valChosenMinusUnchosen, valChosenPlusUnchosen

## Submit job to process the other subjects

```
cd /shared/fmri/analysis/01_level1/cluster_scripts
sh run_level1.sh -m model1 -t binaryChoice -s 2
```

## Push level 1 outputs back to s3

```
export OUT_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level1
aws s3 sync $OUT_PATH s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level1
```

## Delete cluster

```
pcluster delete-cluster --cluster-name fmrianalysis-cluster
pcluster list-clusters
```

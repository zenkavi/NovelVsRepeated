# Steps for level1 analyses

## Push behavior files to S3

```
export BIDS_DIR=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync /bids s3://novel-vs-repeated/fmri/bids/ --exclude '*' --include '*beh/*'
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

This takes a little bit

```
pcluster ssh --cluster-name fmrianalysis-cluster -i $KEYS_PATH/fmrianalysis-cluster.pem

export DATA_PATH=/shared/fmri/bids

aws s3 sync s3://novel-vs-repeated/fmri/bids $DATA_PATH --exclude '*' --include '*_events.tsv' --include '*_beh.tsv' --include '*_bold.json' --include '*run-*_bold.nii.gz'
aws s3 sync s3://novel-vs-repeated/fmri/bids/derivatives $DATA_PATH/derivatives --exclude '*' --include '*desc-preproc_bold.nii.gz' --include '*desc-confounds_timeseries.tsv' --include '*_desc-brain_mask.nii.gz'
```
## Copy analysis code from s3 to cluster

```
export CODE_PATH=/shared/fmri/analysis/01_level1/cluster_scripts

aws s3 sync s3://novel-vs-repeated/fmri/analysis/01_level1/cluster_scripts $CODE_PATH
```

## Test level1 analysis on single subject on head node

```
export DATA_PATH=/shared/fmri/bids
export OUT_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level1/binaryChoice/model1
export CODE_PATH=/shared/fmri/analysis/01_level1/cluster_scripts

docker run --rm -it -e DATA_PATH=/data -e OUT_PATH=/out \
-v $DATA_PATH:/data -v $OUT_PATH:/out -v $CODE_PATH:/code \
zenkavi/fsl:6.0.3 python ./code/level1.py --subnum 601 --session 01 --task binaryChoice --mnum model1 --space 'MNI152NLin2009cAsym_res-2'
```

## Test contrast computation on single subject on head node

```
export DATA_PATH=/shared/fmri/bids
export OUT_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level1/binaryChoice/model1
export CODE_PATH=/shared/fmri/analysis/01_level1/cluster_scripts

docker run --rm -e DATA_PATH=/data -e OUT_PATH=/out \
-v $DATA_PATH:/data -v $OUT_PATH:/out -v $CODE_PATH:/code \
zenkavi/fsl:6.0.3 python ./code/compute_contrasts.py --subnum 601 --session 01 --task binaryChoice --mnum model1 --output_space 'MNI152NLin2009cAsym_res-2' --contrasts_fn binaryChoice_model1_contrasts.json
```

**Analyses in native space?**

## Submit jobs for levels 1s of all subjects and sessions for both tasks

```
cd /shared/fmri/analysis/01_level1/cluster_scripts

sh run_level1.sh -m model1 -t binaryChoice -s 01 -o MNI152NLin2009cAsym_res-2
sh run_level1.sh -m model1 -t binaryChoice -s 02 -o MNI152NLin2009cAsym_res-2
sh run_level1.sh -m model1 -t binaryChoice -s 03 -o MNI152NLin2009cAsym_res-2
sh run_level1.sh -m model1 -t yesNo -s 01 -o MNI152NLin2009cAsym_res-2
sh run_level1.sh -m model1 -t yesNo -s 02 -o MNI152NLin2009cAsym_res-2
sh run_level1.sh -m model1 -t yesNo -s 03 -o MNI152NLin2009cAsym_res-2
```

## Submit jobs to compute contrasts

Wait for the previous jobs to complete without errors. If you submit before some contrast jobs might be allocated resources before the level 1's have completed running.  

I haven't made all of these to run continuously to have the ability to run other arbitrary contrasts as needed without having to re-estimate the GLM.  

```
cd /shared/fmri/analysis/01_level1/cluster_scripts

sh run_compute_contrasts.sh -m model1 -t binaryChoice -s 01 -o MNI152NLin2009cAsym_res-2 -c binaryChoice_model1_contrasts.json
sh run_compute_contrasts.sh -m model1 -t binaryChoice -s 02 -o MNI152NLin2009cAsym_res-2 -c binaryChoice_model1_contrasts.json
sh run_compute_contrasts.sh -m model1 -t binaryChoice -s 03 -o MNI152NLin2009cAsym_res-2 -c binaryChoice_model1_contrasts.json
sh run_compute_contrasts.sh -m model1 -t yesNo -s 01 -o MNI152NLin2009cAsym_res-2 -c yesNo_model1_contrasts.json
sh run_compute_contrasts.sh -m model1 -t yesNo -s 02 -o MNI152NLin2009cAsym_res-2 -c yesNo_model1_contrasts.json
sh run_compute_contrasts.sh -m model1 -t yesNo -s 03 -o MNI152NLin2009cAsym_res-2 -c yesNo_model1_contrasts.json
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

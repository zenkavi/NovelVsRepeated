# Steps for level2 analyses

## Push cluster setup scripts in `./cluster_scripts` to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/fmri/analysis/02_level2/cluster_scripts:/fmri/analysis/02_level2/cluster_scripts amazon/aws-cli s3 sync /fmri/analysis/02_level2/cluster_scripts s3://novel-vs-repeated/fmri/analysis/02_level2/cluster_scripts --exclude "*.DS_Store" --exclude "*.jpeg"
```

## Push session contrasts and saved uncorrected tmaps

```
export BIDS_DIR=/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync /bids/derivatives/nilearn/glm/level1 s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level1 --exclude "*.DS_Store" --exclude "*.jpeg"

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync /bids/derivatives/nilearn/glm/level2 s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level2

```

## Make key pair for `fmrianalysis-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name fmrianalysis-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/fmrianalysis-cluster.pem
chmod 400 $KEYS_PATH/fmrianalysis-cluster.pem
aws ec2 describe-key-pairs
```

## Create cluster config using `make_fmrianalysis_cluster_config.sh`

Using same cluster configuration as done for `01_level1` analyses since it has everything we need for these analyses as well.

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

## Connect to cluster

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
pcluster ssh --cluster-name fmrianalysis-cluster -i $KEYS_PATH/fmrianalysis-cluster.pem
```

## Copy the level 1 beta maps from s3 to cluster

Try running with `sudo` if it fails

```
export DATA_PATH=/shared/fmri/bids

aws s3 sync s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level1/yesNo/model2 $DATA_PATH/derivatives/nilearn/glm/level1/yesNo/model2 --exclude '*' --include '*_effect_size.nii.gz'
```

## Copy uncorrected level 2 tmaps from s3 to cluster

Try running with `sudo` if it fails

```
export DATA_PATH=/shared/fmri/bids

aws s3 sync s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level2/yesNo/model2 $DATA_PATH/derivatives/nilearn/glm/level2/yesNo/model2
```

## Copy analysis code from s3 to cluster

```
export CODE_PATH=/shared/fmri/analysis/02_level2/cluster_scripts

aws s3 sync s3://novel-vs-repeated/fmri/analysis/02_level2/cluster_scripts $CODE_PATH
```

## Test level2 analysis on head node

```
cd $CODE_PATH

export DATA_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level1/yesNo/model2
export OUT_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level2/yesNo/model2/overall-mean
export CODE_PATH=/shared/fmri/analysis/02_level2/cluster_scripts

docker run --rm -e DATA_PATH=/data -e OUT_PATH=/out \
-v $DATA_PATH:/data -v $OUT_PATH:/out -v $CODE_PATH:/code \
zenkavi/fsl:6.0.3 python ./code/level2.py --mnum model2 --reg valHT_par --sign pos --session ses-01 --num_perm 50
```


## Submit jobs for levels 2s

```
cd /shared/fmri/analysis/02_level2/cluster_scripts

....
```

## Push level 1 outputs back to s3

```
export OUT_PATH=/shared/fmri/bids/derivatives/nilearn/glm/level2
aws s3 sync $OUT_PATH s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level2
```

## Download contrasts you want to visualize

```
export BIDS_DIR=/Users/zeynepenkavi/CpuEaters/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync s3://novel-vs-repeated/fmri/bids/derivatives/nilearn/glm/level2 /bids/derivatives/nilearn/glm/level2 --exclude '*' --include '...'
```


## Delete cluster

```
pcluster delete-cluster --cluster-name fmrianalysis-cluster
pcluster list-clusters
```

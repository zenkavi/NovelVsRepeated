# Steps for fmriprep

## Push cluster setup scripts in `./cluster_scripts` to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/fmri:/fmri amazon/aws-cli s3 sync /fmri s3://novel-vs-repeated/fmri --exclude "*.DS_Store"
```

## Make key pair for `fmriprep-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name fmriprep-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/fmriprep-cluster.pem
chmod 400 $KEYS_PATH/fmriprep-cluster.pem
aws ec2 describe-key-pairs
```

## Create cluster config using `make_fmriprep_cluster_config.sh`

```
cd $STUDY_DIR/fmri/preprocessing/03_fmriprep/cluster_scripts
sh make_fmriprep_cluster_config.sh
```

## Create cluster using the config

```
pcluster create-cluster --cluster-name fmriprep-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

## Copy the bids data from s3 to cluster

```
pcluster ssh --cluster-name fmriprep-cluster -i $KEYS_PATH/fmriprep-cluster.pem
cd /shared
aws s3 sync s3://novel-vs-repeated/fmri ./fmri --exclude '*derivatives/*'
```

## Copy freesurfer license (make sure it exists in the S3 bucket) and make temporary directory for fmriprep

```
mkdir /shared/tmp
aws s3 cp s3://novel-vs-repeated/fmri/license.txt /shared
```

## Test fmriprep on single subject on head node

Note: This will likely crash because the head node instance is does not have enough memory. The goal is to check that the command runs. Any errors will be checked in a later step when reviewing the fmriprep reports.

```
export DATA_PATH=/shared/fmri/bids
export TMP_PATH=/shared/tmp
export FS_LICENSE=/shared/license.txt

docker run -ti --rm  \
-v $DATA_PATH:/data:ro  \
-v $DATA_PATH/derivatives:/out  \
-v $TMP_DIR:/work  \
-v $FS_LICENSE:/opt/freesurfer/license.txt  \
-m=16g  \
--cpus="3"  \
nipreps/fmriprep:22.1.0  \
/data /out participant  \
--participant-label 601 \
-w /work --skip_bids_validation --output-spaces MNI152NLin2009cAsym:res-2 --fs-no-reconall

aws s3 sync /shared/fmri/bids s3://novel-vs-repeated/fmri/bids
```

## Submit job to process the other subjects

```
cd /shared/fmri/preprocessing/03_fmriprep/cluster_scripts
sh run_fmriprep.sh
```

## Push updated bids directory with derivatives directory back to s3

```
aws s3 sync /shared/fmri/bids s3://novel-vs-repeated/fmri/bids
```

## Update local bids directory with bidsonym outputs and fmriprep reports and review them

```
export BIDS_DIR=/Users/zeynepenkavi/Downloads/overtrained_decisions_bidsfmri

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync s3://novel-vs-repeated/fmri/bids/sourcedata /bids/sourcedata

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync s3://novel-vs-repeated/fmri/bids/ /bids --exclude '*' --include '*T1w.nii.gz' --exclude '*derivatives/*'

docker run --rm -it -v ~/.aws:/root/.aws -v $BIDS_DIR:/bids amazon/aws-cli s3 sync s3://novel-vs-repeated/fmri/bids/derivatives /bids/derivatives --exclude '*' --include '*figures/*' --include '*figures/*' --include '*log/*'
```

If you are missing reports try this (`run_fmriprep_reports` jobs for all subjects):

```
export DATA_PATH=/shared/fmri/bids
export TMP_PATH=/shared/tmp
export FS_LICENSE=/shared/license.txt

docker run -ti --rm  \
-v $DATA_PATH:/data:ro  \
-v $DATA_PATH/derivatives:/out  \
-v $TMP_DIR:/work  \
-v $FS_LICENSE:/opt/freesurfer/license.txt  \
-m=16g  \
--cpus="3"  \
nipreps/fmriprep:22.1.0  \
/data /out participant  \
--participant-label 601 \
-w /work --skip_bids_validation --reports-only
```

If you have run into space issues check this answer: https://aws.amazon.com/premiumsupport/knowledge-center/ebs-volume-size-increase/

## Delete cluster

```
pcluster delete-cluster --cluster-name fmriprep-cluster
pcluster list-clusters
```

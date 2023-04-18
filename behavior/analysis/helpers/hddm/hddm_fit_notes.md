# Steps for hddm fitting with JAGS

## Create docker container

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/hddm

docker build -t zenkavi/rjagswiener:0.0.3 -f ./rjagswiener.Dockerfile .
```

## Check image exists

```
docker images
```

## Push docker image to dockerhub

```
docker push zenkavi/rjagswiener:0.0.3
```

## Test scripts in container locally

Note: Remove `-it` from docker command when submitting jobs

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
export INPUT_PATH=$STUDY_DIR/behavior/inputs
export CODE_PATH=$STUDY_DIR/behavior/analysis/helpers/hddm
export OUT_PATH=$STUDY_DIR/behavior/analysis/helpers/cluster_scripts/hddm/jags_out

docker run --rm -it -v $INPUT_PATH:/inputs -v $CODE_PATH:/hddm -v $OUT_PATH:/jags_out \
-e INPUT_PATH=/inputs -e CODE_PATH=/hddm -e OUT_PATH=/jags_out \
zenkavi/rjagswiener:0.0.3 Rscript --vanilla /hddm/fit_yn_hddm.R ---day {DAY} --type {TYPE}
```

## Push behavior files to S3

```
export INPUTS_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 cp /inputs/data_choiceYN.csv s3://novel-vs-repeated/behavior/inputs/data_choiceYN.csv
```

## Push cluster setup and model fitting scripts to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR

docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/behavior/analysis/helpers/hddm:/behavior/analysis/helpers/hddm amazon/aws-cli s3 sync /behavior/analysis/helpers/hddm s3://novel-vs-repeated/behavior/analysis/helpers/hddm --exclude "*.DS_Store"

docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/behavior/analysis/helpers/cluster_scripts/hddm:/behavior/analysis/helpers/cluster_scripts/hddm amazon/aws-cli s3 sync /behavior/analysis/helpers/cluster_scripts/hddm s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts/hddm --exclude "*.DS_Store"
```

## Make key pair for `rjagswiener-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys

aws ec2 create-key-pair --key-name rjagswiener-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/rjagswiener-cluster.pem

chmod 400 $KEYS_PATH/rjagswiener-cluster.pem

aws ec2 describe-key-pairs
```

## Create cluster config using `make_rjagswiener_cluster_config.sh`

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/hddm/
sh make_rjagswiener_cluster_config.sh
```

## Create cluster using the config

```
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/hddm/
pcluster create-cluster --cluster-name rjagswiener-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

## Connect to cluster

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
pcluster ssh --cluster-name rjagswiener-cluster -i $KEYS_PATH/rjagswiener-cluster.pem
```

## Copy the behavioral data from s3 to cluster

```
export DATA_PATH=/shared/behavior/inputs

aws s3 sync s3://novel-vs-repeated/behavior/inputs $DATA_PATH --exclude '*' --include 'data_choiceYN.csv' --include 'data_choiceBC.csv'
```

## Copy model fitting code from s3 to cluster

```
export CODE_PATH=/shared/behavior/analysis/helpers

aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers/hddm $CODE_PATH/hddm

aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts/hddm $CODE_PATH/cluster_scripts/hddm
```

## Test fitting of single job on head node

Hierarchy over subjects for each day

```
export INPUT_PATH=/shared/behavior/inputs
export CODE_PATH=/shared/behavior/analysis/helpers/hddm
export OUT_PATH=/shared/behavior/analysis/helpers/cluster_scripts/hddm/jags_out

docker run --rm -it -v $INPUT_PATH:/inputs -v $CODE_PATH:/hddm -v $OUT_PATH:/jags_out \
-e INPUT_PATH=/inputs -e CODE_PATH=/hddm -e OUT_PATH=/jags_out \
zenkavi/rjagswiener:0.0.3 Rscript --vanilla /hddm/fit_yn_hddm.R --day 2 --type RE
```

Hierarchy over days for each subject

```
export INPUT_PATH=/shared/behavior/inputs
export CODE_PATH=/shared/behavior/analysis/helpers/hddm
export OUT_PATH=/shared/behavior/analysis/helpers/cluster_scripts/hddm/jags_out

docker run --rm -it -v $INPUT_PATH:/inputs -v $CODE_PATH:/hddm -v $OUT_PATH:/jags_out \
-e INPUT_PATH=/inputs -e CODE_PATH=/hddm -e OUT_PATH=/jags_out \
zenkavi/rjagswiener:0.0.3 Rscript --vanilla /hddm/fit_yn_sub_hddm.R --sub 619 --type HT
```

## Submit jobs for levels 1s of all subjects and sessions for both tasks

Only a few examples listed below

```
cd /shared/behavior/analysis/helpers/cluster_scripts/hddm/

sh run_fit_yn_hddm_rjags.sh -t HT -d 4

sh run_fit_yn_hddm_sub_rjags.sh -t RE -s 611

sh run_fit_bc_hddm_rjags.sh -t HT -d 6
```

## Push outputs back to s3

```
export OUT_PATH=/shared/behavior/analysis/helpers/cluster_scripts/hddm/jags_out
aws s3 sync $OUT_PATH s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts/hddm/jags_out
```

## Download contrasts you want to visualize

```
export INPUTS_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 sync s3://novel-vs-repeated/behavior/inputs /inputs --exclude '*' --include '*YN_HDDM_FIT*'
```

## Delete cluster

```
pcluster delete-cluster --cluster-name rjagswiener-cluster
pcluster list-clusters
```

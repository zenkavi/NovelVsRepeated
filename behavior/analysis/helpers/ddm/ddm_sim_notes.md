# Steps for hddm fitting with JAGS

## Push behavior files to S3

Make sure parameter posteriors are pushed

```
export INPUTS_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 sync /inputs s3://novel-vs-repeated/behavior/inputs  --exclude "*.DS_Store"
```

## Push cluster setup and model fitting scripts to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/behavior/analysis/helpers:/behavior/analysis/helpers amazon/aws-cli s3 sync /behavior/analysis/helpers s3://novel-vs-repeated/behavior/analysis/helpers --exclude "*.DS_Store"
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
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts
sh make_rjagswiener_cluster_config.sh
```

## Create cluster using the config

```
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts
pcluster create-cluster --cluster-name rjagswiener-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

## Connect to cluster

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
pcluster ssh --cluster-name rjagswiener-cluster -i $KEYS_PATH/rjagswiener-cluster.pem
```

## Copy the behavioral data and parameter posteriors from s3 to cluster

```
export DATA_PATH=/shared/behavior/inputs

aws s3 sync s3://novel-vs-repeated/behavior/inputs $DATA_PATH --exclude '*' --include 'data_choiceYN.csv' --include 'data_choiceBC.csv' --include 'yn_hddm_mcmc_draws.csv'
```
## Copy model fitting code from s3 to cluster

```
export CODE_PATH=/shared/behavior/analysis/helpers

aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers $CODE_PATH
```

## Test simulating on single subject on head node

```
export DATA_PATH=/shared/behavior

docker run --rm -it -v $DATA_PATH:/behavior -w /behavior zenkavi/rjagswiener:0.0.3 Rscript --vanilla /behavior/analysis/helpers/ddm/sim_yn_ddm.R --subnum 611 --cond HT --day 2 --n_samples 10
```

## Submit jobs for levels 1s of all subjects and sessions for both tasks

Only a few examples listed below

```
cd /shared/behavior/analysis/helpers/cluster_scripts

sh run_sim_yn_hddm.sh -s 611 -c HT -d 4
sh run_sim_yn_hddm.sh -s 629 -c RE -d 8
```

## Push outputs back to s3

```
export OUT_PATH=/shared/behavior/inputs
aws s3 sync $OUT_PATH s3://novel-vs-repeated/behavior/inputs
```

## Download contrasts you want to visualize

```
export INPUTS_DIR=/Users/zeynepenkavi/CpuEaters/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 sync s3://novel-vs-repeated/behavior/inputs /inputs --exclude "*" --include "yn_sim_ddm_*.csv"
```

## Delete cluster

```
pcluster delete-cluster --cluster-name rjagswiener-cluster
pcluster list-clusters
```

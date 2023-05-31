# Steps for hddm fitting with JAGS

## Test simulation functions locally

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
export DATA_PATH=$STUDY_DIR/behavior

docker run --rm -it -v $DATA_PATH:/behavior -w /behavior zenkavi/rjagswiener:0.0.3 Rscript --vanilla /behavior/analysis/helpers/hddm/sim_yn_hddm.R --subnum 611 --cond HT --day 2 --n_samples 4
```

## Push behavior files to S3

Make sure parameter posteriors (`yn_sub_hddm_mcmc_draws.csv` and `yn_hddm_mcmc_draws.csv`) are pushed

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

## Copy the behavioral data and parameter posteriors from s3 to cluster

```
export DATA_PATH=/shared/behavior/inputs

aws s3 sync s3://novel-vs-repeated/behavior/inputs $DATA_PATH --exclude '*' --include 'data_choiceYN.csv' --include 'data_choiceBC.csv' --include 'yn_hddm_mcmc_draws.csv' --include 'yn_sub_hddm_mcmc_draws.csv'
```
## Copy model fitting code from s3 to cluster

```
export CODE_PATH=/shared/behavior/analysis/helpers

aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers/hddm $CODE_PATH/hddm
aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts $CODE_PATH/cluster_scripts --exclude '*.RData' --exclude '*.csv' --exclude '*.out' --exclude '*.err'
```

## Test simulating on single subject on head node

```
export DATA_PATH=/shared/behavior

docker run --rm -it -v $DATA_PATH:/behavior -w /behavior zenkavi/rjagswiener:0.0.3 Rscript --vanilla /behavior/analysis/helpers/hddm/sim_yn_hddm.R --subnum 611 --cond HT --day 2 --n_samples 10
```

## Submit jobs for all subjects and sessions for both tasks

Only a few examples listed below

```
cd /shared/behavior/analysis/helpers/cluster_scripts/hddm/

sh run_sim_yn_hddm.sh -s 611 -c HT -d 4
sh run_sim_yn_hddm.sh -s 629 -c RE -d 8
```

For all jobs

``` 
for subnum in 601 609 611 619 621 629
do
    for cond in HT RE
    do
        for day in 1 2 3 4 5 6 7 8 9 10 11
        do
            sh run_sim_yn_hddm.sh -s $subnum -c $cond -d $day
        done
    done
done
```

## Push outputs back to s3

```
export OUT_PATH=/shared/behavior/analysis/helpers/cluster_scripts/hddm/sim_out
aws s3 sync $OUT_PATH s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts/hddm/sim_out
```

## Download simulated data

```
export OUTPUTS_DIR=/Users/zeynepenkavi/CpuEaters/NovelVsRepeated/behavior/analysis/helpers/cluster_scripts/hddm/sim_out

docker run --rm -it -v ~/.aws:/root/.aws -v $OUTPUTS_DIR:/sim_out amazon/aws-cli s3 sync s3://novel-vs-repeated/behavior/analysis/helpers/cluster_scripts/hddm/sim_out /sim_out --exclude "*" --include "yn_sub_hddm_sim_sub*.csv"
```

## Delete cluster

```
pcluster delete-cluster --cluster-name rjagswiener-cluster
pcluster list-clusters
```

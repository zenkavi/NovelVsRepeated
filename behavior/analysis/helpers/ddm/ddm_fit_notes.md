Previously:

`ddm_model.R` - contains `sim_trial` and `fit_trial` functions for a given model

`fit_task.R` - calls `fit_trial` function from a list of ddm model names in its `fit_task` function

`ddm_Roptim.R` - `optim_save` calls `get_task_nll` defined in `fit_task.R`

GRID SEARCH OR OPTIM?

If grid search: d, sigma, starting point bias, barrier decay, ndt (fix?)
If you try 10 values for each fixing one of these that's 10000 likelihoods to compute for each subject, day, stimulus type

If optim you can start from random points e.g. 500 times and see where the algorithm ends up

To build:

Job submission:
`run_optim_yn_ddm.sh`
`run_optim_yn_ddm.batch`

Cluster creation:
docker file
docker image
cluster config
key pairs
data and script pushing to cluster
connect to cluter

Model running:
`optim_yn_ddm.R` ~ `ddm_Roptim.R` [don't need to use visualMLE `optim_save`]
`sim_yn_ddm.R` ~ `sim_task.R` [DONE]
`fit_yn_ddm.R` ~ `fit_task.R` [DONE]
`yn_ddm.R` ~ `ddm_model.R` [DONE]

------------------------------------------------------------------------------------------------

# Steps for ddm fitting using state space

## Create docker container

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/ddm

docker build -t zenkavi/rddmstatespace:0.0.1 -f ./rddmstatespace.Dockerfile .
```

## Check image exists

```
docker images
```

## Push docker container to dockerhub

```
docker push zenkavi/rddmstatespace:0.0.1
```

## Push behavior files to S3

MAKE THIS MORE SPECIFIC TO THE DATA FILES NEEDED FOR THIS STEP

```
export INPUTS_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 cp /inputs/.... s3://novel-vs-repeated/behavior/inputs/....
docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 cp /inputs/.... s3://novel-vs-repeated/behavior/inputs/....
docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 cp /inputs/.... s3://novel-vs-repeated/behavior/inputs/....
```

## Push cluster setup and model fitting scripts to s3

This is pushing all of `helpers` directory but things you need specifically for this should be in `helpers/ddm` and `helpers/cluster_scripts/ddm`

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/behavior/analysis/helpers:/behavior/analysis/helpers amazon/aws-cli s3 sync /behavior/analysis/helpers s3://novel-vs-repeated/behavior/analysis/helpers --exclude "*.DS_Store"
```

## Make key pair for `rddmstatespace-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name rddmstatespace-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/rddmstatespace-cluster.pem
chmod 400 $KEYS_PATH/rddmstatespace-cluster.pem
aws ec2 describe-key-pairs
```

## Create cluster config using `make_rddmstatespace_cluster_config.sh`

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/ddm/
sh make_rddmstatespace_cluster_config.sh
```

## Create cluster using the config

```
cd $STUDY_DIR/behavior/analysis/helpers/cluster_scripts/ddm/
pcluster create-cluster --cluster-name rddmstatespace-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

## Connect to cluster

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
pcluster ssh --cluster-name rddmstatespace-cluster -i $KEYS_PATH/rddmstatespace-cluster.pem
```

## Copy the behavioral data from s3 to cluster

```
export DATA_PATH=/shared/behavior/inputs

aws s3 sync s3://novel-vs-repeated/behavior/inputs $DATA_PATH --exclude '*' --include 'data_choiceYN.csv' --include 'data_choiceBC.csv'
```

## Copy model fitting code from s3 to cluster

```
export CODE_PATH=/shared/behavior/analysis/helpers

aws s3 sync s3://novel-vs-repeated/behavior/analysis/helpers $CODE_PATH
```

## Test fitting on single subject on head node

```
export DATA_PATH=/shared/behavior

docker run --rm -it -v $DATA_PATH:/behavior -w /behavior zenkavi/rddmstatespace:0.0.1 Rscript --vanilla /behavior/analysis/helpers/hddm/fit_yn_hddm.R --type HT --day 2
```

## Submit jobs for levels 1s of all subjects and sessions for both tasks

Only a few examples listed below

```
cd /shared/behavior/analysis/helpers/cluster_scripts/ddm/

sh run_fit_yn_hddm_rjags.sh -s HT -d 4
sh run_fit_yn_hddm_rjags.sh -s RE -d 4

sh run_fit_bc_hddm_rjags.sh -s HT -d 6
```

## Push outputs back to s3

```
export OUT_PATH=/shared/behavior/inputs
aws s3 sync $OUT_PATH s3://novel-vs-repeated/behavior/inputs
```

## Download contrasts you want to visualize

```
export INPUTS_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated/behavior/inputs

docker run --rm -it -v ~/.aws:/root/.aws -v $INPUTS_DIR:/inputs amazon/aws-cli s3 sync s3://novel-vs-repeated/behavior/inputs /inputs --exclude '*' --include '*YN_HDDM_FIT*'
```

## Delete cluster

```
pcluster delete-cluster --cluster-name rddmstatespace-cluster
pcluster list-clusters
```

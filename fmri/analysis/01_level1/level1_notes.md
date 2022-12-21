# Steps for level1 analyses

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

**CHANGE S3 SYNC COMMAND TO WHAT IS NEEDED TO BE COPIED FOR LEVEL1S**

```
pcluster ssh --cluster-name fmrianalysis-cluster -i $KEYS_PATH/fmrianalysis-cluster.pem
cd /shared
aws s3 sync s3://novel-vs-repeated/fmri ./fmri --exclude '*derivatives/*' --exclude '*sourcedata/*'
```

## Test level1 analysis on single subject on head node


```

```

If a subject has fewer scans in different runs this might lead to a lower cosine drift order and causes problems when calculating contrasts combined with other runs because the design matrix ends up with one less column compared to other runs'. In such cases manual modification of the run design matrix might be necessary:

```
run_design_matrix['drift_17'] = 0
```

### Level 1 for binaryChoice task

- 1 run per session so no need for level 2
- Possible value regressors: [valueLeft_par, valueRight_par], [valueChosen_par, valueUnchosen_par], valChosenMinusUnchosen_par, valChosenPlusUnchosen_par
- Other regressors: cross_ev, stim_ev, reward_ev, reward_par

### Level 1 for yesNo task

- 2 runs per session
- Possible value regressors: [valueReference, valueStim], [valueChosen, valueUnchosen], valChosenMinusUnchosen, valChosenPlusUnchosen

## Submit job to process the other subjects

```
cd /shared/fmri/analysis/01_level1/cluster_scripts
sh run_level1.sh
```

## Push level 1 outputs back to s3

```

```

## Delete cluster

```
pcluster delete-cluster --cluster-name fmrianalysis-cluster
pcluster list-clusters
```

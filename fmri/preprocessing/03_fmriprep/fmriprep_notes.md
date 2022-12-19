# Steps for fmriprep

- Push cluster setup scripts in `./cluster_scripts` to s3

```
export STUDY_DIR=/Users/zeynepenkavi/Documents/RangelLab/NovelVsRepeated
cd $STUDY_DIR
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/fmri:/fmri amazon/aws-cli s3 sync /fmri s3://novel-vs-repeated/fmri --exclude "*.DS_Store"
```

- Make key pair for `fmriprep-cluster`

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name fmriprep-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/fmriprep-cluster.pem
chmod 400 $KEYS_PATH/fmriprep-cluster.pem
aws ec2 describe-key-pairs
```

- Create cluster config using `make_fmriprep_cluster_config.sh`

```
cd $STUDY_DIR/fmri/preprocessing/03_fmriprep/cluster_scripts
sh make_fmriprep_cluster_config.sh
```

- Create cluster using the config

```
pcluster create-cluster --cluster-name fmriprep-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

- Copy the bids data from s3 to cluster

```
pcluster ssh --cluster-name fmriprep-cluster -i $KEYS_PATH/fmriprep-cluster.pem
cd /shared
aws s3 sync s3://novel-vs-repeated/fmri ./fmri
```

- Copy freesurfer license (make sure it exists in the S3 bucket) and make temporary directory for fmriprep

```
mkdir /shared/tmp
aws s3 cp s3://novel-vs-repeated/fmri/license.txt /shared
```

- Test fmriprep on single subject on head node

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

aws s3 sync ...
```

- Submit loop job to process the other two subjects

- Push updated bids directory with de-identified t1s and the sourcedata back to s3

- Download fmriprep reports and review them

```
```

- Delete cluster

```
pcluster delete-cluster --cluster-name fmriprep-cluster
pcluster list-clusters
```

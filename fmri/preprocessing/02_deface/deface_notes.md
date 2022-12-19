See here for [earlier notes on defacing](https://github.com/zenkavi/DescribedVsLearned_fmri/blob/master/preproc/02_deface/defacing_notes.md)

# Steps for defacing

~~- Push cluster setup scripts in `./cluster_scripts` to s3~~

```
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd)/fmri:/fmri amazon/aws-cli s3 sync /fmri s3://novel-vs-repeated/fmri --exclude "*.DS_Store"
```

~~- Make key pair for `bidsonym-cluster`~~

```
export KEYS_PATH=/Users/zeynepenkavi/aws_keys
aws ec2 create-key-pair --key-name bidsonym-cluster --query 'KeyMaterial' --output text > $KEYS_PATH/bidsonym-cluster.pem
chmod 400 $KEYS_PATH/bidsonym-cluster.pem
aws ec2 describe-key-pairs
```

~~- Create cluster config using `make_bidsonym_cluster_config.sh`~~

```
sh make_bidsonym_cluster_config.sh
```

~~- Create cluster using the config~~

```
pcluster create-cluster --cluster-name bidsonym-cluster --cluster-configuration tmp.yaml
pcluster list-clusters
```

~~- Copy the bids data from s3 to cluster~~

```
pcluster ssh --cluster-name bidsonym-cluster -i $KEYS_PATH/bidsonym-cluster.pem
cd /shared
aws s3 sync s3://novel-vs-repeated/fmri ./fmri
```

- Test bidsonym on single subject on head node

```
export DATA_PATH=/shared/fmri/bids
docker run --rm -it -v $DATA_PATH:/data \
peerherholz/bidsonym:v0.0.4 \
/data \
participant \
--participant_label 601 \
--deid pydeface \
--brainextraction bet \
--bet_frac 0.5

aws s3 sync $DATA_PATH/sub-601 s3://novel-vs-repeated/fmri/bids/sub-601
aws s3 sync $DATA_PATH/sourcedata/bidsonym/sub-601 s3://novel-vs-repeated/fmri/bids/sourcedata/bidsonym/sub-601
```

- Submit loop job to process the other two subjects
- Push updated bids directory with de-identified t1s and the sourcedata back to s3
- Delete cluster

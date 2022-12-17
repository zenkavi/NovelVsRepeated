See here for [earlier notes on defacing](https://github.com/zenkavi/DescribedVsLearned_fmri/blob/master/preproc/02_deface/defacing_notes.md)

# Steps for defacing

- Push cluster setup scripts in `./cluster_scripts` to s3
- Make key pair for `bidsonym-cluster`
- Create cluster config using `make_bidsonym_cluster_config.sh`
- Create cluster using the config
- Copy the bids data from s3 to cluster
- Test bidsonym on single subject on head node
- Submit loop job to process the other two subjects
- Push updated bids directory with de-identified t1s and the sourcedata back to s3
- Delete cluster

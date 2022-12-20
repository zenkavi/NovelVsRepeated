#! /bin/zsh
alias aws='docker run --rm -it -v ~/.aws:/root/.aws amazon/aws-cli'
export REGION=`aws configure get region`
export SUBNET_ID=`aws ec2 describe-subnets | jq -j '.Subnets[0].SubnetId'`
export VPC_ID=`aws ec2 describe-vpcs | jq -j '.Vpcs[0].VpcId'`

cat > tmp.yaml << EOF
Region: ${REGION}
Image:
  Os: alinux2
SharedStorage:
  - MountDir: /shared
    Name: default-ebs
    StorageType: Ebs
    EbsSettings:
     VolumeType: gp2
     Size: 128
HeadNode:
  InstanceType: t3.2xlarge
  Networking:
    SubnetId: ${SUBNET_ID}
    ElasticIp: false
  LocalStorage:
   RootVolume:
     Size: 128
  Ssh:
    KeyName: fmriprep-cluster
  CustomActions:
    OnNodeConfigured:
      Script: s3://novel-vs-repeated/fmri/preprocessing/03_fmriprep/cluster_scripts/head-node-setup-env.sh
  Iam:
    S3Access:
      - BucketName: novel-vs-repeated
        EnableWriteAccess: True
    AdditionalIamPolicies:
      - Policy: arn:aws:iam::aws:policy/AmazonS3FullAccess
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: compute
      CapacityType: ONDEMAND
      ComputeResources:
        - Name: compute
          InstanceType: c5.9xlarge
          MinCount: 0
          MaxCount: 6
          DisableSimultaneousMultithreading: true
      ComputeSettings:
        LocalStorage:
          RootVolume:
            Size: 128
      Networking:
        SubnetIds:
          - ${SUBNET_ID}
        PlacementGroup:
          Enabled: true
      CustomActions:
        OnNodeConfigured:
          Script: s3://novel-vs-repeated/fmri/preprocessing/03_fmriprep/cluster_scripts/compute-node-setup-env.sh
      Iam:
        S3Access:
          - BucketName: novel-vs-repeated
            EnableWriteAccess: True
        AdditionalIamPolicies:
          - Policy: arn:aws:iam::aws:policy/AmazonS3FullAccess
EOF

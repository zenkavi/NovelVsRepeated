#! /bin/bash
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull zenkavi/rjagswiener:0.0.3

mkdir /shared/.out
mkdir /shared/.err

export TEST_PATH=/shared/

chown -R ec2-user: /shared

echo "alias squeue='squeue -o \"%.18i %.9P %.18j %.8u %.2t %.10M %.6D %R\"'">> /home/ec2-user/.bash_profile

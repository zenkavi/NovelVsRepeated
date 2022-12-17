#! /bin/bash
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
chkconfig docker on
docker pull peerherholz/bidsonym:v0.0.4

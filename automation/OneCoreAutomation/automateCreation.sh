#!/bin/bash

IP=$1
AWS_KEY=$2

set -e

python3 greengo.py create
cd GreengoCerts
tar -czvf certs.tar.gz certs/ config/
cp certs.tar.gz ..
cd ..
scp setupCoreUbuntu.sh ubuntu@$IP:
scp certs.tar.gz ubuntu@$IP:
set +e
ssh -t -i $AWS_KEY ubuntu@$IP 'chmod +x setupCoreUbuntu.sh && ./setupCoreUbuntu.sh 1'
until ssh -t -i $AWS_KEY ubuntu@$IP 'echo hi'; do
  echo "Trying again..."
  sleep 5
done
set -e
ssh -t -i $AWS_KEY ubuntu@$IP './setupCoreUbuntu.sh 2 && ./setupCoreUbuntu.sh 3 && sudo tar -xzvf certs.tar.gz -C /greengrass && ./setupCoreUbuntu.sh 4'
python3 greengo.py update
python3 greengo.py deploy

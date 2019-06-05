#!/bin/bash
# @author rithik.yelisetty

if [[ $# -eq 0 ]]; then
    echo "No arguments provided. To start bulk creation run"
    echo "./automateCreation.sh <IP_ADDRESS> <CONFIG_FILE_NAME> <BULK (True or False)> <GROUP_NAME> <AWS_KEY>"
    exit 1
fi

IP=$1
FOLDER="${4}-GG-Config"
AWS_KEY=$5

set -e

python3 greengo.py create --config_file $2 --bulk $3

cd $FOLDER
tar -czvf certs.tar.gz certs/ config/
cp certs.tar.gz ..
cd ..

scp -i $AWS_KEY setupCoreUbuntu.sh ubuntu@$IP:
scp -i $AWS_KEY certs.tar.gz ubuntu@$IP:

set +e

ssh -t -i $AWS_KEY ubuntu@$IP 'chmod +x setupCoreUbuntu.sh && ./setupCoreUbuntu.sh 1'
until ssh -t -i $AWS_KEY ubuntu@$IP 'echo hi'; do
  echo "Trying again..."
  sleep 5
done

set -e

ssh -t -i $AWS_KEY ubuntu@$IP './setupCoreUbuntu.sh 2 && ./setupCoreUbuntu.sh 3 && sudo tar -xzvf certs.tar.gz -C /greengrass && ./setupCoreUbuntu.sh 4'
python3 greengo.py update --config_file $2 --bulk $3
python3 greengo.py deploy --config_file $2 --bulk $3

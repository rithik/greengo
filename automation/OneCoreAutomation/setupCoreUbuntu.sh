#!/bin/bash
# @author rithik.yelisetty quinn.ciccoretti
if [[ $# -eq 0 ]]; then
    echo "No arguments provided. To start setup run"
    echo "./setup.sh 1"
    echo "usage: ./setup.sh [step number]"
    echo "where step number is 1-4. Run each step after the last has executed or after reboot."
    echo "Step 1 - Set up the users and groups on the system for use by GreenGrass. Then restart."
    echo "Step 2 - Install and run dependency checker."
    echo "Step 3 - Get the GreenGrass runtime, unzip it, get certificate, and ensure the user has put in private key files."
    echo "Step 4 - Start the GreenGrass process."
    echo "Step 5 - Check to make sure that the GreenGrass Daemon is running - There should be something that says '/greengrass/ggc/packages/1.9.0/bin/daemon' "
    exit 1
fi
echo "Running Step $1"
# First, set up the users and groups on the system for use by greengrass
if [[ $1 = 1 ]]; then
  sudo apt update -y
  sudo apt upgrade -y
  sudo adduser --system ggc_user
  sudo addgroup --system ggc_group
  sudo sh -c "echo 'fs.protected_hardlinks = 1 \n' >> /etc/sysctl.d/98-rpi.conf"
  sudo sh -c "echo 'fs.protected_symlinks = 1' >> /etc/sysctl.d/98-rpi.conf"
  sudo sysctl -a 2> /dev/null | grep fs.protected
  sudo apt install unzip
  sudo apt install python -y
  sudo reboot
fi
# Current version of GG dependency checker, simplifies paths below
DIR=greengrass-dependency-checker-GGCv1.9.0
# Second, install and run dependency checker
if [[ $1 = 2 ]]; then
  curl https://raw.githubusercontent.com/tianon/cgroupfs-mount/951c38ee8d802330454bdede20d85ec1c0f8d312/cgroupfs-mount > cgroupfs-mount.sh
  chmod +x cgroupfs-mount.sh
  sudo bash ./cgroupfs-mount.sh
  mkdir $DIR
  cd $DIR
  wget https://github.com/aws-samples/aws-greengrass-samples/raw/master/greengrass-dependency-checker-GGCv1.9.0.zip
  unzip greengrass-dependency-checker-GGCv1.9.0.zip
  # sudo ./check_ggc_dependencies | more
  echo "Read the following report to ensure that all packages are installed except for NodeJS and Java"
  echo "Only install those if the code deployed is going to be written in JavaScript or Java"
fi
# Third, get the GG runtime, unzip it, get an Amazon rootCA, and make sure the user has put in their hash
if [[ $1 = 3 ]]; then
  wget https://d1onfpft10uf5o.cloudfront.net/greengrass-core/downloads/1.9.1/greengrass-linux-x86-64-1.9.1.tar.gz
  sudo tar -xzvf greengrass-linux-x86-64-1.9.1.tar.gz -C /
  sudo wget -O /greengrass/certs/root.ca.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
  echo "Make sure you have added the HASH-setup.tar.gz file to ensure that this IOT device is connected to the IOT GreenGrass Core"
  echo "To do this, run: sudo tar -xzvf HASH-setup.tar.gz -C /greengrass"
fi
# Last, start the greengrass process
if [[ $1 = 4 ]]; then
  cd /greengrass/ggc/core
  sudo ./greengrassd start
fi
# Ensure that the process is running
if [[ $1 = 5 ]]; then
  ps aux | grep -E 'greengrass.*daemon'
  echo "!!! Make sure that there is an entry that includes '/greengrass/ggc/packages/1.9.0/bin/daemon' !!!"
fi

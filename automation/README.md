## Automation

Throughout my work with AWS' GreenGrass, it's become clear that there are limitations with using GreenGrass due to the fact that this software extremely new. In order to help speed up the process of setup and deployment to GreenGrass Cores, scripts were developed to automate this process. In order to complete any of these steps, an AWS account is needed. An IAM Role, with access to all Lambda, S3, GreenGrass, IOT and EC2 resources (or AdministratorAccess), is required in order to configure the terminal. You must have the aws-cli installed along with the boto3 python3 wrapper also installed. The aws-cli should also be configured by using the command aws configure.

### Single Core Provisioning
The first major obstacle is the fact that the cores have to be setup with the appropriate GreenGrass software so that they can communicate via the MQTT channels with the AWS GreenGrass portal. This necessitated the creation of the files located in the `OneCoreAutomation` folder. In order to setup up the group on the AWS portal and to setup the actual core device, first, the `greengo.yaml` file must be edited with the appropriate configuration. Next, the directory labelled `GreengrassHelloWorld` contains a python file (`greengrassHelloWorld.py`). This file should be modified so that the appropriate lambda function can be deployed to AWS. Once this is complete, run the following line of code in a terminal that can access the device as well as the AWS GreenGrass core:
```
./automateCreation.sh <IP_ADDRESS>
```
where the `<IP_ADDRESS>` should be replaced with the IP Address of the actual GreenGrass Core. The script should run automatically and should show a successful deployment message once fully complete. User input may be required to complete the upgrade of the Ubuntu System and to allow SSH for the very first time.


### Bulk Core Provisioning
Now that single device provisioning is working, the next logical step is to provision groups in bulk. All related code is located in the `BulkProvisioning` folder. In order to do this, we make the assumption that each group will have the exact same configuration other than the name of the group and the name of the core. In order to bulk provision, the first step involves collecting the IP addresses of all of the devices available. These should be recorded in the bulk.py file, under the class declaration and in the line labelled `self.IP_ADDRESSES = [IP_1, IP_2, ...]`. Next, modify the configuration file (`template.yaml`) to create the best configuration file. Next, run the following line of code on same terminal that has access to the external world:
```
python3 bulk.py --number <NUMBER> generate
```
where `<NUMBER>` should be replaced by the number of groups to be created. Note that number of groups to create must be less than or equal to the number of IP Addresses listed.

import os
import errno
import fire
import json
import yaml
import shutil
import urllib
from time import sleep
import logging
from boto3 import session
from botocore.exceptions import ClientError
import zipfile
import sys
import json

logging.basicConfig(
    format='%(asctime)s|%(name).10s|%(levelname).5s: %(message)s',
    level=logging.WARNING)
log = logging.getLogger('b-deploy')
log.setLevel(logging.DEBUG)

class BulkDeployment(object):
    def __init__(self):
        s = session.Session()
        self._region = s.region_name
        if not self._region:
            log.error("AWS credentials and region must be setup. "
                      "Refer AWS docs at https://goo.gl/JDi5ie")
            exit(-1)

        log.info("AWS credentials found for region '{}'".format(self._region))

        self._gg = s.client("greengrass")
        self._lambda = s.client("lambda")
        self._s3 = s.client('s3')
        self.S3_BUCKET_NAME = "greengrass-aws-spike"

    def update_lambda(self, function_name="GreengrassHelloWorld", folder="GreengrassHelloWorld", program_name="greengrassHelloWorld.py", handler="greengrassHelloWorld.function_handler", alias="dev"):
        # Step 1. Zip the file
        zip_filename = folder + ".zip"
        zf = zipfile.ZipFile(zip_filename, "w")
        for path, subdirs, files in os.walk("greengrasssdk"):
            for name in files:
                zf.write(os.path.join(path, name))
        zf.write(program_name)
        zf.close()
        log.info("Zip file Created.")

        # Step 2. Upload zip to S3
        self._s3.upload_file(zip_filename, self.S3_BUCKET_NAME, zip_filename)
        log.info("Uploaded Zip File to S3")

        # Step 3. Upload Lambda Function Code
        self._lambda.update_function_code(FunctionName=function_name, S3Bucket=self.S3_BUCKET_NAME, S3Key=zip_filename)
        log.info("Updated Lambda Function Code")

        # Step 4. Update Function Configuration
        self._lambda.update_function_configuration(FunctionName=function_name, Handler=handler)
        log.info("Updated Lambda Function Handler")

        # Step 5. Publish New Version for Lambda and get version number
        resp = self._lambda.publish_version(FunctionName=function_name)
        version_num = resp["Version"]
        log.info("Published New Version of Lambda: Version {}".format(version_num))

        # Step 6. Update Current Alias
        self._lambda.update_alias(FunctionName=function_name, FunctionVersion=str(version_num), Name=alias)
        log.info("Lambda Alias ({}) Updated".format(alias))
        log.info("Run the deploy method to actually deploy the code to the GreenGrass Cores")

    def deploy(self):
        # Step 7. Bulk Deploy
        gg_groups = self._gg.list_groups()
        version_dict = {}
        for group in gg_groups["Groups"]:
            group_id = group["Id"]
            group_versions = self._gg.list_group_versions(GroupId=group_id)
            version_id = group_versions["Versions"][0]["Version"]
            version_dict[group_id] = version_id

        filename = "deployment.txt"
        deployfile = open(filename,"w+")
        for k in version_dict.keys():
            deployfile.write("{\"GroupId\":\"" + k + "\", \"GroupVersionId\":\"" + version_dict[k] + "\", \"DeploymentType\":\"NewDeployment\"}\n")
        deployfile.close()

        self._s3.upload_file(filename, self.S3_BUCKET_NAME, filename)
        file_uri = "s3://" + self.S3_BUCKET_NAME + "/" + filename
        response = self._gg.start_bulk_deployment(ExecutionRoleArn="arn:aws:iam::376854259490:role/GreenGrassBulk", InputFileUri=file_uri)
        log.info("Start Bulk Deployment")
        bulk_dep_id = response["BulkDeploymentId"]

        # Step 8. View Bulk Deployment Status
        while True:
            response = self._gg.get_bulk_deployment_status(BulkDeploymentId=bulk_dep_id)
            if response["BulkDeploymentStatus"] == "Failed":
                print(response["ErrorMessage"])
                break

            if response["BulkDeploymentStatus"] == "Completed":
                print("Succesfully deployed to all devices")
                break

def main():
    fire.Fire(BulkDeployment)

if __name__ == '__main__':
    main()

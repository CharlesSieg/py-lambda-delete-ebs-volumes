import boto3
import json
import logging
import os

from lib.ec2 import EC2API
from lib.ssm import SSMAPI
from lib.sts import STSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)

infrastructure_automation_role_name= "it-infrastructure-automation-role" #os.environ.get("INFRASTRUCTURE_AUTOMATION_ROLE_NAME")



def lambda_handler(event, context):
  log.debug(f"event = {event}")
  log.debug(f"context = {context}")

  account_ids = event["aws_account_ids"]
  log.debug(f"aws_account_ids = {account_ids}")

  ssm_api = SSMAPI()
  parameter_name = f"/automation/regions"
  regions_json = ssm_api.fetch_parameter(parameter_name)
  regions = json.loads(regions_json)

  sts_api = STSAPI()
  for account_id in account_ids:
    log.debug(f"Assuming role in {account_id}...")
    infrastructure_automation_role_arn = f"arn:aws:iam::{account_id}:role/{infrastructure_automation_role_name}"
    credentials = sts_api.fetch_credentials(infrastructure_automation_role_arn)
    ec2_api = EC2API(credentials)
    for region in regions:
      log.debug(f"Checking for unattached EBS volumes in {region}...")
      unattached_volumes = ec2_api.fetch_ebs_volumes()
      log.debug(f"Found {len(unattached_volumes)} unattached EBS volumes.")
      for volume in unattached_volumes:
        volume_id = volume["VolumeId"]
        log.debug(f"Deleting volume {volume_id}...")
        #ec2_api.delete_ebs_volume()

  return {
    'statusCode': 200,
    'body': json.dumps('Hello World!')
  }
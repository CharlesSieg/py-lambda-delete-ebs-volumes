import boto3
import json
import logging
import os

from lib.ec2 import EC2API
from lib.ssm import SSMAPI
from lib.sts import STSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)

dry_run_val = os.environ.get("DRY_RUN")
dry_run = False if dry_run_val == "false" else True
infrastructure_automation_role_name= os.environ.get("INFRASTRUCTURE_AUTOMATION_ROLE_NAME")


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
    if credentials is None:
      log.debug(f"AUTOMATION ERROR: Could not assume the given role in account {account_id}.")
      continue
    for region_name in regions:
      ec2_api = EC2API(credentials, region_name)
      log.debug(f"Checking for unattached EBS volumes in {region_name}...")
      unattached_volumes = ec2_api.fetch_unattached_ebs_volumes()
      if unattached_volumes is None or len(unattached_volumes) == 0:
        log.debug(f"No unattached EBS volumes found.")
        continue
      log.debug(f"Found {len(unattached_volumes)} unattached EBS volumes.")
      for volume in unattached_volumes:
        volume_id = volume["VolumeId"]
        if dry_run:
          log.debug(f"DRY RUN: Volume {volume_id} would be deleted.")
        else:
          log.debug(f"Deleting volume {volume_id}...")
          if ec2_api.delete_ebs_volume(volume_id):
            log.debug(f"Volume {volume_id} was deleted successfully.")
          else:
            log.debug(f"AUTOMATION ERROR: Volume {volume_id} could not be deleted.")

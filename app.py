import boto3
import json
import logging
import os


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)

infrastructure_automation_role_name= "it-infrastructure-automation-role" #os.environ.get("INFRASTRUCTURE_AUTOMATION_ROLE_NAME")

def fetch_credentials(control_tower_execution_role_arn):
  sts_client = boto3.client('sts')

  # Call the assume_role method of the STSConnection object and pass the role
  # ARN and a role session name.
  assumed_role_object=sts_client.assume_role(
    RoleArn=control_tower_execution_role_arn,
    RoleSessionName="AssumeRoleSession1"
  )

  # From the response that contains the assumed role, get the temporary
  # credentials that can be used to make subsequent API calls
  credentials=assumed_role_object['Credentials']

  return credentials


def fetch_parameter(parameter_name):
  client = boto3.client('ssm')
  response = client.get_parameter(
    Name=parameter_name
  )
  log.debug(response)
  return response["Parameter"]["Value"]


def lambda_handler(event, context):
  # get account_id from event
  # fetch list of regions from SSM
  # assume role in account
  # for each region:
    # describe-volumes
    # attachment.instance-id - The ID of the instance the volume is attached to.
    # attachment.status = null or empty
    #"/automation/regions"
  log.debug(f"event = {event}")
  log.debug(f"context = {context}")

  account_ids = event["aws_account_ids"]
  log.debug(f"aws_account_ids = {account_ids}")

  parameter_name = f"/automation/regions"
  regions_json = fetch_parameter(parameter_name)
  regions = json.loads(regions_json)

  for account_id in account_ids:
    log.debug(f"Assuming role in {account_id}...")
    infrastructure_automation_role_arn = f"arn:aws:iam::{account_id}:role/{infrastructure_automation_role_name}"
    credentials = fetch_credentials(infrastructure_automation_role_arn)
    for region in regions:
      log.debug(f"Checking for unattached EBS volumes in {region}...")

  return {
    'statusCode': 200,
    'body': json.dumps('Hello World!')
  }
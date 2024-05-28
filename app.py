import boto3
import json
import logging


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)

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

  aws_account_ids = event["aws_account_ids"]
  log.debug(f"aws_account_ids = {aws_account_ids}")

  # role_arn = f"arn:aws:iam::{aws_account_id}:role/{role_name}"

  # credentials = fetch_credentials(control_tower_execution_role_arn)

  # body = "Role was created successfully."
  # if not create_automation_role(credentials, aws_account_id):
  #    body = "Role creation failed."
  return {
    'statusCode': 200,
    'body': json.dumps('Hello World!')
  }
import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


class IAMAPI(AWSAPI):
  __client_name__ = "iam"

  def delete_non_default_policy_versions(self, policy_arn, policy_name):
    log.debug(f"Fetching policy versions for {policy_name}...")
    versions = self.list_policy_versions(policy_arn)
    for version in versions:
      if version["IsDefaultVersion"] is not True:
        log.debug(f'Deleting policy version {version["VersionId"]}...')
        self.delete_policy_version(policy_arn, version["VersionId"])

  def fetch_or_create_policy(self, account_id, policy_name, policy_description, policy_filename, policy_vars, policies_path):
    if not policy_name.endswith("-policy"):
      policy_name = policy_name + "-policy"
    log.debug(f"Checking for an existing policy named {policy_name}...")
    policy_document = open(f"{policies_path}/{policy_filename}", "r").read()
    for k, v in policy_vars.items():
      policy_document = policy_document.replace(f"__{k}__", v)
    policy = self.fetch_policy(account_id, policy_name)
    if policy is None:
      # Since the policy does not exist, create it.
      log.debug("The policy does not exist. Creating...")
      policy = self.create_policy(policy_name, policy_document, policy_description)
      if type(policy) is BaseException:
        log.error("The policy could not be created. The automation cannot continue.")
        return None
      else:
        log.debug("The policy was created successfully.")
        time.sleep(5)
    elif type(policy) is BaseException:
      log.error("There was an error checking for the policy. The automation cannot continue.")
      return None
    else:
      log.debug("The policy was found.")
      self.delete_non_default_policy_versions(policy["Arn"], policy_name)
      if self.create_policy_version(policy["Arn"], policy_document):
        log.debug("Policy updated successfully.")
    return policy





  def attach_role_policy(self, role_name, policy_arn):
      """
      response = client.attach_role_policy(
          RoleName='string',
          PolicyArn='string'
      )
      """
      try:
          self.client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
          return True
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.NoSuchEntityException
          # IAM.Client.exceptions.LimitExceededException
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.UnmodifiableEntityException
          # IAM.Client.exceptions.PolicyNotAttachableException
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def create_policy(self, policy_name, policy_document, description):
      """
      response = client.create_policy(
          PolicyName='string',
          Path='string',
          PolicyDocument='string',
          Description='string',
          Tags=[
              {
                  'Key': 'string',
                  'Value': 'string'
              },
          ]
      )
      """
      try:
          response = self.client.create_policy(
              PolicyName=policy_name,
              PolicyDocument=policy_document,
              Description=description,
              Tags=[{"Key": "Owner", "Value": "CloudOps"}],
          )
          return response["Policy"]
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.LimitExceededException
          # IAM.Client.exceptions.EntityAlreadyExistsException
          # IAM.Client.exceptions.MalformedPolicyDocumentException
          # IAM.Client.exceptions.ConcurrentModificationException
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def create_policy_version(self, policy_arn, policy_document):
      """
      response = client.create_policy_version(
          PolicyArn='string',
          PolicyDocument='string',
          SetAsDefault=True|False
      )
      """
      try:
          self.client.create_policy_version(PolicyArn=policy_arn, PolicyDocument=policy_document, SetAsDefault=True)
          return True
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.LimitExceededException
          # IAM.Client.exceptions.EntityAlreadyExistsException
          # IAM.Client.exceptions.MalformedPolicyDocumentException
          # IAM.Client.exceptions.ConcurrentModificationException
          # IAM.Client.exceptions.ServiceFailureException
          return False

  def create_role(self, role_name, assume_role_policy, description):
      """
      https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_role

      response = client.create_role(
          Path='string',
          RoleName='string',
          AssumeRolePolicyDocument='string',
          Description='string',
          MaxSessionDuration=123,
          PermissionsBoundary='string',
          Tags=[
              {
                  'Key': 'string',
                  'Value': 'string'
              },
          ]
      )

      {
          'Role': {
              'Path': 'string',
              'RoleName': 'string',
              'RoleId': 'string',
              'Arn': 'string',
              'CreateDate': datetime(2015, 1, 1),
              'AssumeRolePolicyDocument': 'string',
              'Description': 'string',
              'MaxSessionDuration': 123,
              'PermissionsBoundary': {
                  'PermissionsBoundaryType': 'PermissionsBoundaryPolicy',
                  'PermissionsBoundaryArn': 'string'
              },
              'Tags': [
                  {
                      'Key': 'string',
                      'Value': 'string'
                  },
              ],
              'RoleLastUsed': {
                  'LastUsedDate': datetime(2015, 1, 1),
                  'Region': 'string'
              }
          }
      }
      """
      try:
          response = self.client.create_role(
              AssumeRolePolicyDocument=assume_role_policy,
              Description=description,
              RoleName=role_name,
              Tags=[{"Key": "Owner", "Value": "CloudOps"}],
          )
          return response["Role"]
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.LimitExceededException
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.EntityAlreadyExistsException
          # IAM.Client.exceptions.MalformedPolicyDocumentException
          # IAM.Client.exceptions.ConcurrentModificationException
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def delete_policy_version(self, policy_arn, version_id):
      """
      response = client.delete_policy_version(
          PolicyArn='string',
          VersionId='string'
      )
      """
      try:
          self.client.delete_policy_version(PolicyArn=policy_arn, VersionId=version_id)
          return True
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def fetch_policy(self, account_id, policy_name):
      try:
          response = self.client.get_policy(PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}")
          return response["Policy"]
      except self.client.exceptions.NoSuchEntityException:
          return None
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def fetch_role(self, role_name):
      """
      {
          'Role': {
              'Path': 'string',
              'RoleName': 'string',
              'RoleId': 'string',
              'Arn': 'string',
              'CreateDate': datetime(2015, 1, 1),
              'AssumeRolePolicyDocument': 'string',
              'Description': 'string',
              'MaxSessionDuration': 123,
              'PermissionsBoundary': {
                  'PermissionsBoundaryType': 'PermissionsBoundaryPolicy',
                  'PermissionsBoundaryArn': 'string'
              },
              'Tags': [
                  {
                      'Key': 'string',
                      'Value': 'string'
                  },
              ],
              'RoleLastUsed': {
                  'LastUsedDate': datetime(2015, 1, 1),
                  'Region': 'string'
              }
          }
      }
      """
      try:
          response = self.client.get_role(RoleName=role_name)
          return response["Role"]
      except self.client.exceptions.NoSuchEntityException:
          return None
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def list_policy_versions(self, policy_arn):
      """
      response = client.list_policy_versions(
          PolicyArn='string',
          Marker='string',
          MaxItems=123
      )
      """
      try:
          response = self.client.list_policy_versions(PolicyArn=policy_arn)
          return response["Versions"]
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

  def update_assume_role_policy(self, role_name, assume_role_policy):
      """
      https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.update_assume_role_policy

      response = client.update_assume_role_policy(
          RoleName='string',
          PolicyDocument='string'
      )
      """
      try:
          self.client.update_assume_role_policy(RoleName=role_name, PolicyDocument=assume_role_policy)
          return True
      except BaseException as err:
          log.error(f"Unexpected {err=}, {type(err)=}")
          # TODO: Check for errors.
          # IAM.Client.exceptions.LimitExceededException
          # IAM.Client.exceptions.InvalidInputException
          # IAM.Client.exceptions.EntityAlreadyExistsException
          # IAM.Client.exceptions.MalformedPolicyDocumentException
          # IAM.Client.exceptions.ConcurrentModificationException
          # IAM.Client.exceptions.ServiceFailureException
          return BaseException()

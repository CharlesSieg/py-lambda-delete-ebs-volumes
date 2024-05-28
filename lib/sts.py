import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)

class STSAPI(AWSAPI):
  __client_name__ = "sts"

  def fetch_credentials(self, role_arn):
    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    assumed_role_object = self.client.assume_role(
      RoleArn=role_arn,
      RoleSessionName="AssumeRoleSession1"
    )

    # From the response that contains the assumed role, get the temporary
    # credentials that can be used to make subsequent API calls
    credentials=assumed_role_object['Credentials']

    return credentials

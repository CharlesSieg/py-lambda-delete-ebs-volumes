import boto3


class AWSAPI(object):
  def __init__(self):
    super().__init__()
    self.client = boto3.client(self.__client_name__)

  def __init__(self, credentials):
    super().__init__()
    self.credentials = credentials
    self.client = boto3.client(self.__client_name__,
      aws_access_key_id=credentials['AccessKeyId'],
      aws_secret_access_key=credentials['SecretAccessKey'],
      aws_session_token=credentials['SessionToken']
  )

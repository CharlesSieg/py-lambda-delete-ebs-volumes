import boto3


class AWSAPI(object):
  def __init__(self, credentials=None, region_name="us-east-1"):
    super().__init__()
    if credentials is None:
      self.client = boto3.client(self.__client_name__, region_name=region_name)
    else:
      self.credentials = credentials
      self.client = boto3.client(self.__client_name__,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region_name
      )

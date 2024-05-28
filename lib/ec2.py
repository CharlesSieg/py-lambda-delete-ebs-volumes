import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


class EC2API(AWSAPI):
  __client_name__ = "ec2"

  def delete_ebs_volume(self, volume_id):
    try:
      response = self.client.delete_volume(
        VolumeId=volume_id
      )
      log.debug(response)
      return True
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")
      return False

  def fetch_ebs_volumes(self):
    try:
      response = self.client.describe_volumes()
      log.debug(response)
      return response["Volumes"]
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")
      return None

  def fetch_unattached_ebs_volumes(self):
    try:
      response = self.client.describe_volumes(
        Filters=[
          {
            'Name': 'status',
            'Values': ['available']
          }
        ]
      )
      log.debug(response)
      return response["Volumes"]
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")
      return None

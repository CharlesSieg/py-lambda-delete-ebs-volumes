import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


class EC2API(AWSAPI):
  __client_name__ = "ec2"

  def fetch_ebs_volumes(self):
    response = self.client.describe_volumes()
    log.debug(response)
    return response["Volumes"]

  def fetch_unattached_ebs_volumes(self):
    response = self.client.describe_volumes(
      Filters={
        {
          'Name': 'string',
          'Values': ['string']
        }
      }
    )
    log.debug(response)
    return response["Volumes"]

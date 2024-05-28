import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


class SSMAPI(AWSAPI):
  __client_name__ = "ssm"

  def fetch_parameter(self, parameter_name):
    response = self.client.get_parameter(
      Name=parameter_name
    )
    log.debug(response)
    return response["Parameter"]["Value"]

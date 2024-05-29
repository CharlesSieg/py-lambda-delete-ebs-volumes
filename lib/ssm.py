import json
import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


class SSMAPI(AWSAPI):
  __client_name__ = "ssm"

  def get_parameter(self, parameter_name):
    try:
      response = self.client.get_parameter(
        Name=parameter_name
      )
      log.debug(response)
      return response["Parameter"]["Value"]
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")
      return None

  def put_parameter(self, parameter_name, description, payload):
    try:
      payload_json = json.dumps(payload)
      response = self.client.put_parameter(
        Name=parameter_name,
        Description=description,
        Value=payload_json,
        Overwrite=True,
        Type='String'
      )
      log.debug(response)
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")
      return None

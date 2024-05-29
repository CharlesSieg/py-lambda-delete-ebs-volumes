from dataclasses import dataclass
import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


@dataclass
class ServiceCatalogProduct:
  account_email: str
  account_name: str
  managed_ou: str
  id: str
  path_id: str
  provisioned_product_name: str
  provisioning_artifact_id: str
  sso_user_email: str
  sso_user_first_name: str
  sso_user_last_name: str


class ServiceCatalogAPI(AWSAPI):
  __client_name__ = "servicecatalog"

  def provision_account(self, product):
    args = {
      "PathId": product.path_id,
      "ProductId": product.id,
      "ProvisionedProductName": product.provisioned_product_name,
      "ProvisioningArtifactId": product.provisioning_artifact_id,
      "ProvisioningParameters": [
        {
          "Key": "AccountEmail",
          "Value": product.account_email
        },
        {
          "Key": "AccountName",
          "Value": product.account_name
        },
        {
          "Key": "ManagedOrganizationalUnit",
          "Value": product.managed_ou
        },
        {
          "Key": "SSOUserEmail",
          "Value": product.sso_user_email
        },
        {
          "Key": "SSOUserFirstName",
          "Value": product.sso_user_first_name
        },
        {
          "Key": "SSOUserLastName",
          "Value": product.sso_user_last_name
        }
        ]
      }
    log.debug(f"Calling provision_product with args: {args}")
    response = self.client.provision_product(**args)
    log.debug(response)

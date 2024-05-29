from dataclasses import dataclass
import logging
import time

from lib import AWSAPI


log = logging.getLogger("lambda")
log.setLevel(logging.DEBUG)


@dataclass
class Account:
  id: str
  name: str
  parent_ou: str = None
  status: str = None


class OrganizationsAPI(AWSAPI):
  __client_name__ = "organizations"

  def __init__(self, credentials, management_account_id):
    super().__init__(credentials)
    self.__accounts = []
    self.management_account_id = management_account_id
    self.organization = None
    self.organizational_units = []
    self.organizational_units_by_id = {}

  @property
  def accounts(self):
    items = []
    for account_d in self.__accounts:
      account = Account(id=account_d["Id"], name=account_d["Name"], status=account_d["Status"])
      account.parent_ou = account_d["Parent"]
      items.append(account)
    items.sort(key=lambda account: account.name.lower())
    return items

  def accounts_for_ou(self, ou_id):
    return [account for account in self.accounts if account.parent_ou == ou_id]

  def fetch(self):
    if self.management_account_id is None:
      log.warn("Management account ID has not been provided. Cannot fetch Organizations resources.")
      return
    self.management_account = Account(id=self.management_account_id, name="Management Account")
    self.__fetch()

  #########################################################
  # PRIVATE METHODS
  #########################################################

  def __fetch(self):
    self.__fetch_organization()

    # Fetch all organizational units.
    self.__fetch_root_organizational_unit()
    self.__fetch_organizational_units(self.root_ou)

    # Fetch all accounts.
    self.__fetch_accounts()

  def __fetch_accounts(self):
    log.debug("Fetching accounts...")
    self.__fetch_accounts_by_organizational_unit(self.root_ou)
    for ou in self.organizational_units:
      self.__fetch_accounts_by_organizational_unit(ou)
    log.info(f"{len(self.accounts)} accounts found.")

  def __fetch_accounts_by_organizational_unit(self, ou, next_token=None):
    log.debug(f"Fetching accounts for OU {ou['Name']}...")
    try:
      params = {"ParentId": ou["Id"]}
      if next_token is not None:
        params["NextToken"] = next_token
      op = getattr(self.client, "list_accounts_for_parent")
      response = op(**params)
      log.info(f'{len(response["Accounts"])} accounts found for OU {ou["Name"]}.')
      for d in response["Accounts"]:
        d["Parent"] = ou["Id"]
        self.__accounts.append(d)
      if "NextToken" in response:
        self.__fetch_accounts_by_organizational_unit(ou, response["NextToken"])
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")

  def __fetch_organization(self):
    log.info("Fetching organization...")
    try:
      response = self.client.describe_organization()
      self.organization = response["Organization"]
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")

  def __fetch_organizational_units(self, parent_ou):
    log.debug("Fetching organizational units...")
    try:
      response = self.client.list_organizational_units_for_parent(ParentId=parent_ou["Id"])
      log.info(f'{len(response["OrganizationalUnits"])} child OUs found for {parent_ou["Name"]}.')
      for ou in response["OrganizationalUnits"]:
        ou["Parent"] = parent_ou["Id"]
        self.organizational_units.append(ou)
        log.debug(f'Found {ou["Name"]}.')
        self.__fetch_organizational_units(ou)
    except BaseException as err:
      log.error(f"Unexpected {err=}, {type(err)=}")

  def __fetch_root_organizational_unit(self):
    log.info("Fetching root OU...")
    try:
      response = self.client.list_roots()
      for root in response["Roots"]:
        self.root_ou = root
        break
    except BaseException as err:
        log.error(f"Unexpected {err=}, {type(err)=}")

from socrata.authorization import Authorization
from socrata import Socrata
from sodapy import Socrata as Soda
import json
import utils
import os
# from boxsdk import JWTAuth, Client
# from boxsdk.network.default_network import DefaultNetwork

# box_auth = JWTAuth.from_settings_file('jwt_auth.json')
# box_client = Client(box_auth)

SOCRATA_ID = os.environ['SOCRATA_ID']
SOCRATA_PASS = os.environ['SOCRATA_PASS']
APP_TOKEN = os.environ['APP_TOKEN']

domain = "healthdata.gov"

socrata_py_auth = Authorization(
  domain,
  SOCRATA_ID, 
  SOCRATA_PASS
)

socrata_py_client = Socrata(socrata_py_auth)

sodapy_client = Soda(
    domain,
    APP_TOKEN,
    SOCRATA_ID,
    SOCRATA_PASS
)

with open('profile_reports_config.json') as f:
  profile_reports = json.load(f)

for i in profile_reports:
  try:
    utils.upload_state_report(i['id'], i['name'], domain, socrata_py_client, sodapy_client, SOCRATA_ID, SOCRATA_PASS)
  except:
    pass

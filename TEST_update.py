from boxsdk import JWTAuth, Client
from boxsdk.network.default_network import DefaultNetwork
from socrata.authorization import Authorization
import os
import json
import utils

#box_auth = JWTAuth.from_settings_file('jwt_auth.json')
#box_client = Client(box_auth)
  

domain = "hhs-odp-testing.demo.socrata.com"

socrata_auth = Authorization(
  domain,
  os.environ['SOCRATA_ID'], 
  os.environ['SOCRATA_KEY']
)


with open('test-config.json') as f:
  test_config = json.load(f)

for i in test_config:
  utils.upload_state_report(i['id'], i['name'], domain, socrata_auth)

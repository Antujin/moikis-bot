import pandas as pd
import requests
import os
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import json


class LogAnalyzer:
    def __init__(self):
        self.client_id = os.environ.get('LOGS_CLIENT_ID')
        self.client_secret = os.environ.get('LOGS_CLIENT_SECRET')
        self.token = self.get_access_token()

    def get_access_token(self):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        return oauth.fetch_token(token_url='https://www.warcraftlogs.com/oauth/token', auth=auth)

    def refresh_token(self):
        self.token = self.get_access_token()


if __name__ == '__main__':
    analyzer = LogAnalyzer()
    print(analyzer.token)

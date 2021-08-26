import pandas as pd
import requests
import os
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
import json

pots = {307192: 'Spiritual Healing Potion',
        }

class LogAnalyzer:
    def __init__(self):
        self.client_id = os.environ.get('LOGS_CLIENT_ID')
        self.client_secret = os.environ.get('LOGS_CLIENT_SECRET')
        self.token = self.get_access_token()
        self.api_url = 'https://www.warcraftlogs.com/api/v2/client'

    def get_access_token(self):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        return oauth.fetch_token(token_url='https://www.warcraftlogs.com/oauth/token', auth=auth)

    def refresh_token(self):
        self.token = self.get_access_token()

    def get_boss_fights(self, report_id):
        query = '{reportData {report(code: "%s" ) {fights(killType: Encounters) {id,name,startTime,endTime,kill,friendlyPlayers}}}}' % report_id
        resp = self.send_query(query)
        json_data = json.loads(resp.text)
        df_data = json_data['data']['reportData']['report']['fights']
        return pd.DataFrame(df_data)

    def get_pot_usage(self, report_id, starttime, endtime):
        df = pd.DataFrame()
        for i, ability in enumerate(pots.keys()):
            query = '{reportData {report(code: "%s") {events(startTime: %i, endTime: %i, abilityID: %i, dataType: Healing) {data}}}}' % (report_id, starttime, endtime, ability)
            resp = self.send_query(query)
            print(resp.text)
            json_data = json.loads(resp.text)
            df_data = json_data['data']['reportData']['report']['events']["data"]
            df_new = pd.DataFrame(df_data)
            df = pd.concat([df, df_new], ignore_index=True)
        return df

    def send_query(self, query):
        try:
            return requests.post(self.api_url, json={'query': query},
                                 headers={"Authorization": f'{self.token["token_type"]} {self.token["access_token"]}'})
        except TokenExpiredError as e:
            self.refresh_token()
            return requests.post(self.api_url, json={'query': query},
                                 headers={"Authorization": f'{self.token["token_type"]} {self.token["access_token"]}'})



if __name__ == '__main__':
    analyzer = LogAnalyzer()
    print(analyzer.token)
    df_boss_fights = analyzer.get_boss_fights("f79HjvywxP1QqAbG")
    used_pots = pd.DataFrame()
    for i in range(len(df_boss_fights.index)):
        test_fight = df_boss_fights.loc[i]
        used_pots_this_fight = analyzer.get_pot_usage("f79HjvywxP1QqAbG", test_fight['startTime'], test_fight['endTime'])
        used_pots = pd.concat([used_pots,used_pots_this_fight], ignore_index=True)
    print(used_pots)
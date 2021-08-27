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
        query = f'{{reportData {{report(code: "{report_id}" ) {{fights(killType: Encounters) {{id,name,startTime,endTime,kill,encounterID,friendlyPlayers}} }} }} }}'
        resp = self.send_query(query)
        json_data = json.loads(resp.text)
        df_data = json_data['data']['reportData']['report']['fights']
        return pd.DataFrame(df_data)

    def get_pot_usage(self, report_id, starttime, endtime, fight_ids):
        df = pd.DataFrame()
        for i, ability in enumerate(pots.keys()):
            query = f'{{reportData {{report(code: "{report_id}") {{events(startTime: {starttime}, endTime: {endtime}, abilityID: {ability}, fightIDs: {fight_ids}, dataType: Healing) {{data}} }} }} }}'
            resp = self.send_query(query)
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

    def get_player_data(self, report_id):
        query = f'{{reportData {{report(code: "{report_id}") {{masterData(translate: false) {{actors(type: "Player") {{id, name}} }} }} }} }}'
        resp = self.send_query(query)
        json_data = json.loads(resp.text)
        data = json_data['data']['reportData']['report']['masterData']['actors']
        players = {}
        for player in data:
            players.update({player['id']: player['name']})
        return players

    def analyze_used_healthpots(self, report_id):
        df_boss_fights = self.get_boss_fights(report_id)
        players = self.get_player_data(report_id)
        # print(df_boss_fights[['id', 'name']])
        fightcount = df_boss_fights.index
        used_pots = self.get_pot_usage(report_id, df_boss_fights.loc[0, 'startTime'],
                                       df_boss_fights.loc[fightcount.stop - 1, 'endTime'],
                                       df_boss_fights.loc[:, 'id'].to_numpy())
        print(df_boss_fights.keys())
        groups = used_pots.groupby('fight').groups
        last_encounter_id = 0
        i = 1
        for group in groups.keys():

            locs = groups[group]
            fight_id = used_pots.loc[locs[0], 'fight']
            encounter = df_boss_fights[df_boss_fights['id'] == fight_id].iloc[0]
            if encounter['encounterID'] == last_encounter_id:
                i += 1
            else:
                i = 1
            if encounter['kill']:
                kill = 'kill'
            else:
                kill = 'wipe'
            print(f"{encounter['name']} - Pull {i} ({kill}):")
            for loc in locs:
                pot_user_id = used_pots.loc[loc, 'sourceID']
                player_name = players[pot_user_id]
                print(f"\t{player_name} used a healthpot")
            last_encounter_id = encounter['encounterID']


if __name__ == '__main__':
    analyzer = LogAnalyzer()
    analyzer.analyze_used_healthpots("f79HjvywxP1QqAbG")

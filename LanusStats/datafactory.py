#With great help and a lot of the credit to https://github.com/valensantarone (Valko)

import requests
import pandas as pd
import numpy as np
from .config import headers
from .functions import get_possible_leagues_for_page
from .exceptions import InvalidStat, MatchDoesntHaveInfo

class DataFactory:
    
    def __init__(self):
        self.possible_incidences = ['goals', 'substitutions', 'clearances', 'cornerKicks', 'correctPasses', 'fouls', 'incorrectPasses', 'offsides', 'redCards', 'shots', 'status', 'stealings', 'yellowCards', 'throwIn', 'goalkick', 'nutmegs', 'sombreroFlick', 'penaltyShootout', 'var']

    def make_url(self, league, match_id):
        leagues = get_possible_leagues_for_page(league, None, 'DataFactory')
        league_slug = leagues[league]['slug']
        path = f'https://panorama.datafactory.la/html/v3/htmlCenter/data/deportes/futbol/{league_slug}/events/{match_id}.json?t=172730124'
        return path

    def make_request(self, league, match_id):
        path = self.make_url(league, match_id)
        data = requests.get(path, headers=headers).json()
        return data
    
    def get_incidence_df(self, data, incidence_type):
        if incidence_type not in self.possible_incidences:
            raise InvalidStat(incidence_type, incidence_type, self.possible_incidences)
        incidence = data['incidences'][incidence_type]
        df = pd.DataFrame.from_dict(incidence, orient='index')
        return df
    
    def get_teams_ids(self, data):
        id_home = data['match']['homeTeamId']
        id_away = data['match']['awayTeamId']
        return id_home, id_away
    
    def get_teams_name(self, data):
        home = data['match']['homeTeamName']
        away = data['match']['awayTeamName']
        return home, away
    
    def parse_coordinates(self, df, league, match_id):
        try:
            df['x'] = df['coord'].dropna().apply(lambda x: x['1']['x'])
        except KeyError:
            path = self.make_url(league, match_id)
            raise MatchDoesntHaveInfo(path)
        df['y'] = df['coord'].dropna().apply(lambda x: x['1']['y'])
        df['endX'] = df['coord'].dropna().apply(lambda x: x['2']['x'])
        df['endY'] = df['coord'].dropna().apply(lambda x: x['2']['y'])

        df['x'] = (df['x'] + 1) * 50
        df['y'] = (df['y'] + 1) * 50
        df['endX'] = (df['endX'] + 1) * 50
        df['endY'] = (df['endY'] + 1) * 50

        df.loc[df['t'].apply(lambda x: x['half']) == 2, ['x', 'y', 'endX', 'endY']] = 100 - df.loc[df['t'].apply(lambda x: x['half']) == 2, ['x', 'y', 'endX', 'endY']]

        df['y'] = 100 - df['y']
        df['endY'] = 100 - df['endY']

        df.drop('coord', axis=1, inplace=True)

        return df
    
    def get_minute(self, row):
            if row['t']['half'] == 1:
                return row['t']['m']
            elif row['t']['half'] == 2:
                return row['t']['m']

    def get_seconds(self, row):
        return row['t']['s']
    
    def parse_minutes(self, df):
        df['minute'] = df.apply(self.get_minute, axis=1)
        df['seconds'] = df.apply(self.get_seconds, axis=1)
        df.drop('t', axis=1, inplace=True)
        return df

    def get_recv_name(self, recvId, data):
            if pd.isna(recvId):
                name = None
            else:
                recvId = int(recvId)
                name = data['players'].get(f'{recvId}', {}).get('name', {}).get('last', None)
            return name

    def get_plyr_name(self, plyrId, data):
        plyrId = int(plyrId)
        return data['players'][f'{plyrId}']['name']['last']
    
    def add_home_away_columns(self, data, df):
        home, away = self.get_teams_name(data)
        home_id, away_id = self.get_teams_ids(data)
        df['teamName'] = np.where(df.team == home_id, home, away)
        df['home/away'] = np.where(df.team == home_id, 'home', 'away')
        return df
    
    def get_match_passes(self, league, match_id, all_passes=False):
        data = self.make_request(league, match_id)
        df = self.get_incidence_df(data, 'correctPasses')
        if all_passes:
            df_incorrect = self.get_incidence_df(data, 'incorrectPasses')
            df = pd.concat([df, df_incorrect])

        df = self.parse_coordinates(df, league, match_id)

        df = self.parse_minutes(df)

        df['recvName'] = df['recvId'].apply(lambda x: self.get_recv_name(x, data))
        df['plyrName'] = df['plyrId'].apply(lambda x: self.get_plyr_name(x, data))

        df = self.add_home_away_columns(data, df)

        return df
    
    def get_incidence(self, league, match_id, incidence_type):
        print("Possible values for incidence_type param: ", self.possible_incidences)

        data = self.make_request(league, match_id)
        df = self.get_incidence_df(data, incidence_type)
        
        if 'coord' in df.columns:
            df = self.parse_coordinates(df, league, match_id)

        df = self.parse_minutes(df)

        df = self.add_home_away_columns(data, df)

        return df

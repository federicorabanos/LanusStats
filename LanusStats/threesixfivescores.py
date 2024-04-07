import pandas as pd
import requests
import json
from PIL import Image
import re
from io import BytesIO
from .functions import get_possible_leagues_for_page

class ThreeSixFiveScores:

    def parse_dataframe(self, objeto):
        df = pd.DataFrame(objeto['rows'])
        df_1 = df['entity'].apply(pd.Series)
        df_2 = df['stats'].apply(pd.Series)[0].apply(pd.Series)
        df_concat = pd.concat([df_1, df_2], axis=1)[['id', 'name', 'positionName', 'value']]
        df_concat['estadistica'] = objeto['name']
        return df_concat

    def get_league_top_players_stats(self, league_id):
        response = requests.get(f'https://webws.365scores.com/web/stats/?appTypeId=5&langId=29&timezoneName=America/Buenos_Aires&userCountryId=382&competitions={league_id}&competitors=&withSeasons=true')
        stats = response.json()
        general_stats = stats['stats']
        total_df = pd.DataFrame()
        for i in range(len(general_stats)):
            objeto = general_stats[i]
            stats_df = self.parse_dataframe(objeto)
            total_df = pd.concat([total_df, stats_df])
        return total_df
    
    def get_ids(match_url):
        match = re.search(r'-(\d+-\d+-\d+)', match_url)
        id_1 = match.group(1) if match else None
    
        match = re.search(r'id=(\d+)', match_url)
        id_2 = match.group(1) if match else None

        return id_1, id_2
    
    def get_match_data(self, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        response = requests.get(f'https://webws.365scores.com/web/game/?appTypeId=5&langId=29&timezoneName=America/Buenos_Aires&userCountryId=382&gameId={game_id}&matchupId={matchup_id}&topBookmaker=14')
        match_data = response.json()['game']
        return match_data
    
    def get_match_shotmap(self, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        match_data = self.get_match_data(game_id, matchup_id)
        json_tiros = match_data['chartEvents']['events']
        df = pd.DataFrame(json_tiros)
        return df
    
    def get_players_info(self, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        match_data = self.get_match_data(game_id, matchup_id)
        teams_json = match_data['members']
        teams_df = pd.DataFrame(teams_json)
        return teams_df
    
    def get_team_names(self, match_url):
        values = ['home', 'away']
        names = []
        matchup_id, game_id = self.get_ids(match_url)
        match_data = self.get_match_data(game_id, matchup_id)
        for value in values:
            nombre = match_data[f'{value}Competitor']['name']
            names.append(nombre)
        home, away = names[0], names[1]
        return home, away
    
    def get_general_match_stats(self, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        match_data = self.get_match_data(game_id, matchup_id)
        values = ['home', 'away']
        df_total = pd.DataFrame()
        for value in values:
            df = pd.DataFrame(match_data[f'{value}Competitor']['statistics'])[['name', 'categoryName', 'value']]
            df['equipo'] = match_data[f'{value}Competitor']['name']
            df_total = pd.concat([df_total, df]).reset_index(drop=True)
        return df_total

    def get_player_heatmap_match(self, player, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        match_data = self.get_match_data(game_id, matchup_id)
        players = match_data['homeCompetitor']['lineups']['members']
        df_players = pd.DataFrame(players)
        players_total = pd.DataFrame(match_data['members'])
        df_players = df_players.merge(players_total, on='id', how='left')
        heatmap = requests.get(df_players[df_players['name'] == player].heatMap.iloc[0])
        heatmap_image = Image.open(BytesIO(heatmap.content))
        return heatmap_image

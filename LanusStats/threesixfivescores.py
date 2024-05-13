import pandas as pd
import requests
import json
from PIL import Image
import re
from io import BytesIO
from .functions import get_possible_leagues_for_page
from .exceptions import MatchDoesntHaveInfo
from .config import headers
import time
import numpy as np

class ThreeSixFiveScores:

    def parse_dataframe(self, objeto):
        df = pd.DataFrame(objeto['rows'])
        df_1 = df['entity'].apply(pd.Series)
        df_2 = df['stats'].apply(pd.Series)[0].apply(pd.Series)
        df_concat = pd.concat([df_1, df_2], axis=1)[['id', 'name', 'positionName', 'value']]
        df_concat['estadistica'] = objeto['name']
        return df_concat

    def get_league_top_players_stats(self, league):
        """Get top performers of certain statistics for a league and a season

        Args:
            league (str): Possible leagues in get_available_leagues("365Scores").
                          The page don't show stats from previous seasons.

        Returns:
            total_df: DataFrame with all the stats, values and players.
        """
        leagues = get_possible_leagues_for_page(league, None, '365Scores')
        league_id = leagues[league]['id']
        response = requests.get(f'https://webws.365scores.com/web/stats/?appTypeId=5&langId=29&timezoneName=America/Buenos_Aires&userCountryId=382&competitions={league_id}&competitors=&withSeasons=true', headers=headers)
        time.sleep(3)
        stats = response.json()
        general_stats = stats['stats']
        total_df = pd.DataFrame()
        for i in range(len(general_stats)):
            objeto = general_stats[i]
            stats_df = self.parse_dataframe(objeto)
            total_df = pd.concat([total_df, stats_df])
        return total_df
    
    def get_ids(self, match_url):
        """Extracts ids from a 365Scores match URL.

        Args:
            match_url (str): 365Scores match URL

        Returns:
            id_1, id_2: matchup id and game id.
        """
        match = re.search(r'-(\d+-\d+-\d+)', match_url)
        id_1 = match.group(1) if match else None
    
        match = re.search(r'id=(\d+)', match_url)
        id_2 = match.group(1) if match else None

        return id_1, id_2
    
    def get_match_data(self, match_url):
        """Get data from a match and scrape it.

        Args:
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            match_data: Json with game data.
        """
        
        matchup_id, game_id = self.get_ids(match_url)
        response = requests.get(f'https://webws.365scores.com/web/game/?appTypeId=5&langId=29&timezoneName=America/Buenos_Aires&userCountryId=382&gameId={game_id}&matchupId={matchup_id}&topBookmaker=14', headers=headers)
        time.sleep(3)
        match_data = response.json()['game']
        return match_data
    
    def get_requests_stats(self, match_url):
        """Request to stats of a match

        Args:
            match_url (str): 65Scores match URL.

        Returns:
            response: JSON with the response of the request.
        """
        matchup_id, game_id = self.get_ids(match_url)
        response = requests.get(f'https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=29&timezoneName=America/Buenos_Aires&userCountryId=382&games={game_id}', headers=headers)
        time.sleep(3)
        return response
    
    def get_match_general_stats(self, match_url):
        """Get data from a match and scrape it. Requests about general stats.

        Args:
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            match_stats: Json with game stats.
        """
        
        response = self.get_requests_stats(match_url)
        match_stats = pd.DataFrame(response.json()['statistics'])
        
        team1 = {
            'id': response.json()['competitors'][0]['id'],
            'name': response.json()['competitors'][0]['name']
        }
        
        team2 = {
            'id': response.json()['competitors'][1]['id'],
            'name': response.json()['competitors'][1]['name']
        }
        
        match_stats['team_name'] = np.where(match_stats['competitorId'] == team1['id'], team1['name'], team2['name'])
        return match_stats
    
    def get_match_time_stats(self, match_url):
        """Get time match stats

        Args:
            match_url (str): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            game_statistics: JSON with various stats about time played and wasted in a match.
        """
        
        response = self.get_requests_stats(match_url)
        try:
            game_statistics = response.json()['actualGameStatistics']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        return game_statistics
    
    def get_match_shotmap(self, match_url):
        """Scrape shotmap from the page as a DataFrame, if the match has it.

        Args:
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            df: DataFrame with all the shot details from any shot shown in 365Scores UI.
        """
        match_data = self.get_match_data(match_url)
        try:
            json_tiros = match_data['chartEvents']['events']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        df = pd.DataFrame(json_tiros)
        df['xgot'] = df.xgot.str.replace('-','0')
        df[['xg', 'xgot']] = df[['xg', 'xgot']].astype(float)
        df = pd.concat([df, df['outcome'].apply(pd.Series).rename(columns={'name': 'shot_outcome'})],axis=1).drop(columns='outcome')
        return df
    
    def get_players_info(self, match_url):
        """Get players info for a certain match

        Args:
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            teams_df: Player data for a match as a DataFrame.
        """
        match_data = self.get_match_data(match_url)
        teams_json = match_data['members']
        teams_df = pd.DataFrame(teams_json)
        return teams_df
    
    def get_team_data(self, match_url):
        values = ['home', 'away']
        names = []
        ids = []
        colors = []
        match_data = self.get_match_data(match_url)
        for value in values:
            name = match_data[f'{value}Competitor']['name']
            id = match_data[f'{value}Competitor']['id']
            color = match_data[f'{value}Competitor']['color']
            names.append(name), ids.append(id), colors.append(color)
        
        home = {
            'name': names[0],
            'id': ids[0],
            'color': colors[0]
        }
        
        away = {
            'name': names[1],
            'id': ids[1],
            'color': colors[1]
        }
        
        return home, away
    
    def get_general_match_stats(self, match_url):
        """Get general statistics for teams from a match

        Args:
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            df_total: DataFrame with the data from both teams in a match.
        """
        match_data = self.get_match_data(match_url)
        values = ['home', 'away']
        df_total = pd.DataFrame()
        for value in values:
            df = pd.DataFrame(match_data[f'{value}Competitor']['statistics'])[['name', 'categoryName', 'value']]
            df['equipo'] = match_data[f'{value}Competitor']['name']
            df_total = pd.concat([df_total, df]).reset_index(drop=True)
        return df_total

    def get_player_heatmap_match(self, player, match_url):
        """Get player heatmap for a certain match.

        Args:
            player (str): Player name, must be the same as it shows in the 365Scores page
            match_url (url): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824

        Returns:
            heatmap_image: Image of the
        """
        match_data = self.get_match_data(match_url)
        players = match_data['homeCompetitor']['lineups']['members']
        df_players = pd.DataFrame(players)
        players_total = pd.DataFrame(match_data['members'])
        df_players = df_players.merge(players_total, on='id', how='left')
        try:
            heatmap = requests.get(df_players[df_players['name'] == player].heatMap.iloc[0], headers=headers)
            time.sleep(3)
        except AttributeError:
            raise MatchDoesntHaveInfo(match_url)
        heatmap_image = Image.open(BytesIO(heatmap.content))
        return heatmap_image

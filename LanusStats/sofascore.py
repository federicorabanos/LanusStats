import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from datetime import datetime
import time
from .functions import get_possible_leagues_for_page, get_proxy
from .exceptions import InvalidStrType
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import numpy as np

class SofaScore:
    
    def __init__(self):
        self.league_stats_fields = [
            'goals',
            'yellowCards',
            'redCards',
            'groundDuelsWon',
            'groundDuelsWonPercentage',
            'aerialDuelsWon',
            'aerialDuelsWonPercentage',
            'successfulDribbles',
            'successfulDribblesPercentage'
            'tackles',
            'assists',
            'accuratePassesPercentage',
            'totalDuelsWon',
            'totalDuelsWonPercentage',
            'minutesPlayed',
            'wasFouled',
            'fouls',
            'dispossessed',
            'possesionLost',
            'appearances',
            'started',
            'saves',
            'cleanSheets',
            'savedShotsFromInsideTheBox',
            'savedShotsFromOutsideTheBox',
            'goalsConcededInsideTheBox',
            'goalsConcededOutsideTheBox',
            'highClaims',
            'successfulRunsOut',
            'punches',
            'runsOut',
            'accurateFinalThirdPasses',
            'bigChancesCreated',
            'accuratePasses',
            'keyPasses',
            'accurateCrosses',
            'accurateCrossesPercentage',
            'accurateLongBalls',
            'accurateLongBallsPercentage',
            'interceptions',
            'clearances',
            'dribbledPast',
            'bigChancesMissed',
            'totalShots',
            'shotsOnTarget',
            'blockedShots',
            'goalConversionPercentage',
            'hitWoodwork',
            'offsides',
            'expectedGoals',
            'errorLeadToGoal',
            'errorLeadToShot',
            'passToAssist'
            ]
    
    def get_match_id(self, match_url):
        """Get match id for any match
        Args:
            match_url (string): Full link to a SofaScore match
        Returns:
            string: Match id for a SofaScore match. Used in Urls
        """
        if type(match_url) != str:
            raise InvalidStrType(match_url)
        
        match_id = match_url.split(':')[-1]
        return match_id

    def get_proxy_and_uc_driver(self, url):
        proxy = get_proxy()
        proxy_host = proxy.split(':')[0]
        proxy_port = proxy.split(':')[-1]
        chrome_options = Options()
        chrome_options.add_argument('--proxy-server=http://{}:{}'.format(proxy_host, proxy_port))
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')
        chrome_options.add_argument('accept-language=en-US,en;q=0.9')
        driver = uc.Chrome(headless=True,use_subprocess=False,option=chrome_options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        
        return soup

    def get_match_data(self, match_url):
        
        match_id = self.get_match_id(match_url)
        
        url = f'https://api.sofascore.com/api/v1/event/{match_id}'
        
        soup = self.get_proxy_and_uc_driver(url)
        
        time.sleep(3)
        
        json_data = json.loads(soup.text)
        
        return json_data

    def get_match_momentum(self, match_url):
        
        soup = self.get_proxy_and_uc_driver(match_url)
        
        rectangles = soup.find_all('rect')
        data = []
        for rect in rectangles:
            x_value = float(rect.get('x')) if rect.get('x') is not None else None
            if x_value is not None:
                data.append({
                    'fill': rect.get('fill'),
                    'height': float(rect.get('height')),
                    'width': float(rect.get('width')),
                    'x': x_value,
                    'y': float(rect.get('y'))
                })
        df = pd.DataFrame(data)
        new_df = df[(df['width'] > 1) & (df['width'] < 10)]
        new_df['new_value'] = np.where(new_df.fill.str.contains('secondary'), new_df.height, 
                            np.where(new_df.fill.str.contains('primary'), (new_df.height)*-1, 'other'))
        match_momentum = new_df.reset_index(drop=True)[['x','new_value']]
        
        return match_momentum

    def get_match_shotmap(self, match_url, save_csv=False):
        
        match_id = self.get_match_id(match_url)
        
        url = f'https://api.sofascore.com/api/v1/event/{match_id}/shotmap'
        
        soup = self.get_proxy_and_uc_driver(url)
        
        shots = json.loads(soup.text)['shotmap']
        match_shots = pd.DataFrame(shots)
        today = datetime.now().strftime('%Y-%m-%d')
        if save_csv:
            match_shots.to_csv(f'shots match - {match_id} - {today}.csv')
        players = match_shots.player.apply(pd.Series)
        coordenates = match_shots.playerCoordinates.apply(pd.Series)
        match_shots = pd.concat([match_shots.drop(columns=['player']), players], axis=1)
        match_shots = pd.concat([match_shots.drop(columns=['playerCoordinates']), coordenates], axis=1)
        return match_shots
    
    def get_positions(self, selected_positions):
        """Returns a string for the parameter filters of the scrape_league_stats() request.

        Args:
            selected_positions (list): List of the positions available to filter on the SofaScore UI

        Returns:
            dict: Goalies, Defenders, Midfielders and Forwards and their translation for the parameter of the request
        """
        positions = {
            'Goalkeepers': 'G',
            'Defenders': 'D',
            'Midfielders': 'M',
            'Forwards': 'F'
        }
        abbreviations = [positions[position] for position in selected_positions]
        return '~'.join(abbreviations)
    
    def scrape_league_stats(self, league, season, save_csv=False, accumulation='total', selected_positions = ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']):
        
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        positions = self.get_positions(selected_positions)
        concatenated_fields = "%2C".join(self.league_stats_fields)
        
        ffset = 0
        df = pd.DataFrame()
        for i in range(0,100):
            request_url = f'https://api.sofascore.com/api/v1' +\
                f'/unique-tournament/{league_id}/season/{season_id}/statistics'+\
                f'?limit=100&order=-rating&offset={offset}'+\
                f'&accumulation={accumulation}' +\
                f'&fields={concatenated_fields}'+\
                f'&filters=position.in.{positions}'
                
            soup = self.get_proxy_and_uc_driver(request_url)
            
            response = json.loads(soup.text)
            
            new_df = pd.DataFrame(response['results'])
            new_df['player'] = new_df.player.apply(pd.Series)['name']
            new_df['team'] = new_df.team.apply(pd.Series)['name']
            df = pd.concat([df, new_df])
            
            if response.get('page') == response.get('pages'):
                print('End of the pages')
                break
            offset += 100
            
        if save_csv:
            df.to_csv(f'{league} {season} stats.csv')
        
        return df
    
    def get_team_names(self, match_url):
        """Get the team names for the home and away teams

        Args:
            match_url (string): Full link to a SofaScore match

        Returns:
            strings: Name of home and away team.
        """

        data = self.get_match_data(match_url)

        home_team = data['homeTeam']['name']
        away_team = data['awayTeam']['name']

        return home_team, away_team
    
    def get_players_average_positions(self, match_url):
        """Return player averages positions for each team

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            DataFrame: Each row is a player and columns averageX and averageY 
                denote their average position on the match.
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)

        request_url = f'https://api.sofascore.com/api/v1/event/{match_id}/average-positions', 

        soup = self.get_proxy_and_uc_driver(request_url)
        response = json.loads(soup.text)
        
        names = {'home': home_name, 'away': away_name}
        dataframes = {}
        for team in names.keys():
            data = pd.DataFrame(response[team])
            df = pd.concat(
                [data['player'].apply(pd.Series), data.drop(columns=['player'])],
                axis=1
            )
            df['team'] = names[team]
            dataframes[team] = df
            
        return dataframes['home'], dataframes['away']
    
    ############################################################################
    
    def get_lineups(self, match_url):
        
        match_id = self.get_match_id(match_url)
        
        request_url = f'https://api.sofascore.com/api/v1/event/{match_id}/lineups'
        
        soup = self.get_proxy_and_uc_driver(request_url)
        response = json.loads(soup.text)
        
        return response
    
    def get_player_ids(self, match_url):
        """Get the player ids for a Sofascore match

        Args:
            match_url (string): Full link to a SofaScore match

        Returns:
            dict: Name and ids of every player in the match
                Key: Name
                Value: Id
        """
        response = self.get_lineups(match_url)
        
        teams = ['home', 'away']
        player_ids = {}
        for team in teams:
            data = response[team]['players']

            for item in data:
                player_data = item['player']
                player_ids[player_data['name']] = player_data['id']

        return player_ids
    
    def get_player_heatmap(self, match_url, player):
        """ Get the x-y coordinates to create a player heatmap. Use Seaborn's
        `kdeplot()` to create the heatmap image.

        Args:
            match_url (str): Full link to a SofaScore match
            player (str): Name of the player (must be the SofaScore one). Use
                Sofascore.get_player_ids()

        Returns:
            DataFrame: Pandas dataframe with x-y coordinates for the player
        """
        match_id = self.get_match_id(match_url)

        player_ids = self.get_player_ids(match_url)
        player_id = player_ids[player]

        request_url = f'https://api.sofascore.com/api/v1/event/{match_id}/player/{player_id}/heatmap', 
        
        soup = self.get_proxy_and_uc_driver(request_url)
        response = json.loads(soup.text)
        
        heatmap = pd.DataFrame(response['heatmap'])
        
        return heatmap
    
    def get_player_season_heatmap(self, league, season, player_id):
        
        
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        request_url = f'https://api.sofascore.com/api/v1/player/{player_id}/unique-tournament/{league_id}/season/{season_id}/heatmap/overall'
        
        soup = self.get_proxy_and_uc_driver(request_url)
        response = json.loads(soup.text)
        
        season_heatmap = pd.DataFrame(response['points'])

        return season_heatmap
        
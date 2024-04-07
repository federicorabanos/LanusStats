import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import datetime
import time
from mplsoccer import PyPizza, add_image, FontManager
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from .functions import get_possible_leagues_for_page, possible_stats_exception
from .exceptions import PlayerDoesntHaveInfo, MatchDoesntHaveInfo

class Fbref:

    ##############################################
    def __init__(self):
        self.possible_stats = [
            'stats',
            'keepers',
            'keepersadv',
            'shooting',
            'passing',
            'passing_types',
            'gca',
            'defense',
            'possession',
            'playingtime',
            'misc'
        ]

    ##############################################
        
    def match_info_exception(self, path):
        data = self.get_all_dfs(path)
        try:
            data[17]
        except IndexError:
            raise MatchDoesntHaveInfo(path)
    
    def player_info_exception(self, path):
        data = self.get_all_dfs(path)
        first_df = data[0]
        if first_df.columns[0] not in ['Statistic', 'Estadísticas']:
            raise PlayerDoesntHaveInfo('path')
    
    def get_teams_season_stats(self, stat, league, season=None, save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False):
        
        possible_stats_exception(self.possible_stats, stat)     
        leagues = get_possible_leagues_for_page(league, season, 'Fbref')
        
        if league == 'Big 5 European Leagues':
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{stat}/squads/{leagues[league]["slug"]}-Stats'
        elif season != None:
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{season}/{stat}/{season}/{leagues[league]["slug"]}-Stats'
        elif season != None and league == 'Big 5 European Leagues':
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{season}/{stat}/squads/{season}/{leagues[league]["slug"]}-Stats'
        else:
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{stat}/{leagues[league]["slug"]}-Stats'
            
        
        today = datetime.now().strftime('%Y-%m-%d')
        time.sleep(3)
        
        df_total = pd.read_html(path)

        if stats_vs:
              data = df_total[1]
        else:
              data = df_total[0]
        
        if change_columns_names:
            data.columns = data.columns \
                            .map(lambda x: x[1] if 'Unnamed:' in x[0] else '_'.join([part.replace(' ', '') for part in x]))
            if add_page_name:
                new_columns = [f'{stat}_' + col for col in data.columns]
                data.columns = new_columns
        else:
            data.columns = data.columns.droplevel(0)

        if save_csv:
              data.to_csv(f'{league} - {stat} - {today}.csv')
        return data

    def get_vs_and_teams_season_stats(self, stat, league, season=None, save_excel=False, change_columns_names=False, add_page_name=False):
        """Get For and VS Stats for a team in a season. The two tables show in any stat for any team in a league.

        Args:
            stat (str): Stat available for that league in Fbref
            league (str): League available in the scraper (check get_leagues())
            season (str, optional): String showing the season for the data to be extracted. Defaults to None.
            save_excel (bool, optional): If true it save an excel file. Defaults to False.
            change_columns_names (bool, optional): If you would like to change the columns names. Defaults to False.
            add_page_name (bool, optional): It add the stat name to the columns. Defaults to False.

        Returns:
            df: DataFrame with the stat/stats for that team
            df_vs: DataFrame with the stat/stats against that team
        """
        df = self.get_teams_season_stats(stat, league, season, False, False, change_columns_names, add_page_name)
        df_vs = self.get_teams_season_stats(stat, league, season, False, True, change_columns_names, add_page_name)

        if save_excel:
            path = f'{league} - {stat} vs stats teams.xlsx'
            writer = pd.ExcelWriter(path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Stats')
            df_vs.to_excel(writer, sheet_name='VS Stats')
            writer.close()

        return df, df_vs
    
    def concatenate_teams_df(self, df, df_vs, axis=1):
        df_total = pd.concat([df, df_vs], axis=axis)

        return df_total
        
    def get_all_teams_season_stats(self, league, save_csv=False, stats_vs=False, change_columns_names=False, add_page_name=False):
        
        today = datetime.now().strftime('%Y-%m-%d')
        data = pd.DataFrame()
        for stat in self.possible_stats:
            placeholder = self.get_teams_season_stats(f'{stat}',league, False, stats_vs, change_columns_names, add_page_name)
            data = pd.concat([data, placeholder], axis=1)
        
        if save_csv:
              data.to_csv(f'{league} - {stat} - {today}.csv')

        return data

    def get_table(self, soup):
        return soup.find_all('table')[0]

    def parse_row(self, row):
            cols = None
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            return cols
         
    def get_player_season_stats(self, stat, league, season=None, save_csv=False, add_page_name=False):
        """_summary_

        Args:
            stat (_type_): _description_
            league (_type_): _description_
            save_csv (bool, optional): _description_. Defaults to False.
        """
        possible_stats_exception(self.possible_stats, stat)
        
        leagues = get_possible_leagues_for_page(league, season, 'Fbref')
        
        today = datetime.now().strftime('%Y-%m-%d')
        if league == 'Big 5 European Leagues':
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{stat}/players/{leagues[league]["slug"]}-Stats'
        elif season != None:
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{season}/{stat}/{season}/{leagues[league]["slug"]}-Stats'
        elif season != None and league == 'Big 5 European Leagues':
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{season}/{stat}/players/{season}/{leagues[league]["slug"]}-Stats'
        else:
            path = f'https://fbref.com/en/comps/{leagues[league]["id"]}/{stat}/{leagues[league]["slug"]}-Stats'

        time.sleep(3)
        
        """Most of the code is from @BeGriffis (Twitter): 
        https://github.com/griffisben/griffis_soccer_analysis/blob/main/griffis_soccer_analysis/fbref_code.py
        """
        response = requests.get(path)
        soup = BeautifulSoup(response.content, "html.parser")
        comment = soup.find_all(text=lambda t: isinstance(t, Comment))
        comment_number=0
        for i in range(len(comment)):
            if comment[i].find('\n\n<div class="table_container"') != -1:
                comment_number = i
        comment_table = comment[comment_number]
        table = comment_table.find('table')
        table_html = BeautifulSoup(comment_table[table:], 'html.parser')
        table = self.get_table(table_html)
        data = []
        headings=[]
        headtext = table_html.find_all("th",scope="col")
        for i in range(len(headtext)):
            heading = headtext[i].get_text()
            headings.append(heading)
        headings=headings[1:len(headings)]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row_index in range(len(rows)):
            row = rows[row_index]
            cols = self.parse_row(row)
            data.append(cols)
         
        df_data = pd.DataFrame(data)
        df_data = df_data.rename(columns=df_data.iloc[0])
        df_data = df_data.reindex(df_data.index.drop(0))
        df_data = df_data.replace('',0).drop(columns=['Matches'])
        df_data.insert(4, 'Comp', [league]*len(df_data))
        df_data = df_data.dropna().reset_index(drop=True)


        if add_page_name:
                new_columns = [f'{stat}_' + col if col != 'Player' else col for col in df_data.columns]
                df_data.columns = new_columns

        if save_csv:
              df_data.to_csv(f'{league} - {stat} - {today}.csv')
        
        return df_data

    def get_all_player_season_stats(self, league, save_csv=False):
        
        today = datetime.now().strftime('%Y-%m-%d')
        data = pd.DataFrame()
        gk_data = pd.DataFrame()
        for stat in self.possible_stats:
            print(stat)
            if stat in ['keepers', 'keepersadv']:
                placeholder = self.get_player_season_stats(f'{stat}',league, False, True)
                if len(gk_data) == 0:
                    gk_data = pd.concat([gk_data, placeholder], axis=1)
                else:
                    gk_data = gk_data.merge(placeholder, on='Player', how='left')
            else:
                placeholder = self.get_player_season_stats(f'{stat}',league, False, True)
                if len(data) == 0:
                    data = pd.concat([data, placeholder], axis=1)
                else:
                    data = data.merge(placeholder, on='Player', how='left')
        
        if save_csv:
              data.to_csv(f'{league} - {stat} - {today}.csv')

        #To avoid duplicates of players that played for two clubs in the same competition
        data = data.drop_duplicates(subset=['Player', 'stats_Squad']).reset_index(drop=True)
        gk_data = gk_data.drop_duplicates(subset=['Player', 'keepers_Squad']).reset_index(drop=True)

        return data, gk_data
    
    def get_slice_text_colors(self, player_df):
        sublists, sublist = [], []
        for item in list(player_df.iloc[:, 0]):
            if item is np.nan:
                if sublist:  # Si la sublist no está vacía
                    sublists.append(sublist.copy())
                    sublist.clear()  # Reiniciar la sublist
            else:
                sublist.append(item)
        if sublist:
            sublists.append(sublist.copy())

        slice_colors = ["#2a6f97"] * len(sublists[0]) + ["#588b8b"] * len(sublists[1]) + ["#8d0801"] * len(sublists[2])
        text_colors = ["#FFFFFF"] * len(sublists[0]) + ["#000000"] * len(sublists[1]) + ["#FFFFFF"] * len(sublists[2])
        return slice_colors, text_colors
    
    def get_player_percentiles(self, path):
        self.player_info_exception(path)
        player_df = pd.read_html(path)[0]
        time.sleep(3)
        return player_df
    
    def get_all_dfs(self, path):
        data = pd.read_html(path)
        time.sleep(3)
        return data
    
    def get_player_similarities(self, path):
        self.player_info_exception(path)
        data = pd.read_html(path)[1]
        time.sleep(3)
        return data
    
    def get_match_shots(self, path):
        self.match_info_exception(path)
        data = self.get_all_dfs(path)[17]
        data.columns = data.columns.droplevel(0)
        return data
    
    def get_general_match_team_stats(self, path):
        self.match_info_exception(path)
        data = self.get_all_dfs(path)
        local_df, visit_df = data[3], data[10]
        return local_df, visit_df

    def get_tournament_table(self, path):
        data = self.get_all_dfs(path)[0]
        return data
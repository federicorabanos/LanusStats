import json
import pandas as pd
from datetime import datetime
import time
from .functions import get_possible_leagues_for_page
from .exceptions import InvalidStrType, MatchDoesntHaveInfo, PlayerDoesntHaveInfo
import http.client

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
        
    def httpclient_request(self, path):
        """Request used to SofaScore

        Args:
            path (str): Part of the url to make the request

        Returns:
            data: _description_
        """
        time.sleep(5)
        url = "api.sofascore.com"

        conn = http.client.HTTPSConnection(url)

        conn.request("GET", path)

        res = conn.getresponse()

        data = res.read()

        conn.close()
        
        return data

    def get_match_data(self, match_url):
        """Gets all the general data from a match 

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            json: Data of the match.
        """
        
        match_id = self.get_match_id(match_url)
        
        url = f'api/v1/event/{match_id}'
        
        data = self.httpclient_request(url)
        
        time.sleep(3)
        
        json_data = json.loads(data)
        
        return json_data

    def get_match_momentum(self, match_url):
        """Get values of the momentum graph in SofaScore UI

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            DataFrame: Values needed to make a heatmap with pitch.kdeplot.
        """
        
        match_id = self.get_match_id(match_url)
        
        url = f'/api/v1/event/{match_id}/graph'
        
        data = self.httpclient_request(url)

        try:
            points = json.loads(data)['graphPoints']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        match_momentum = pd.DataFrame(points)
        
        return match_momentum

    def get_match_shotmap(self, match_url, save_csv=False):
        """Get a DataFrame with data of the shots of a match

        Args:
            match_url (str): Full link to a SofaScore match
            save_csv (bool, optional): Save the DataFrame to a csv. Defaults to False.

        Returns:
            DataFrame: Dataframe with all the data from the shotmap shown in SofaScore UI
        """
        
        match_id = self.get_match_id(match_url)
        
        url = f'api/v1/event/{match_id}/shotmap'
        
        data = self.httpclient_request(url)
        try:
            shots = json.loads(data)['shotmap']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
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
        """Get every player statistic that can be asked in league pages on SofaScore.
        Args:
            league (str): Possible leagues in get_available_leagues("Sofascore")
            season (str): Possible saeson in get_available_season_for_leagues("Sofascore", league)
            accumulation (str, optional): Value of the filter accumulation. Can be "per90" and "perMatch". Defaults to 'total'.
            selected_positions (list, optional): Value of the filter positions. Defaults to ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards'].
        Returns:
            DataFrame: DataFrame with each row corresponding to a player and the columns are the fields defined on get_league_stats_fields()
        """
        
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        positions = self.get_positions(selected_positions)
        concatenated_fields = "%2C".join(self.league_stats_fields)
        
        offset = 0
        df = pd.DataFrame()
        for i in range(0,20):
            request_url = f'api/v1' +\
                f'/unique-tournament/{league_id}/season/{season_id}/statistics'+\
                f'?limit=100&order=-rating&offset={offset}'+\
                f'&accumulation={accumulation}' +\
                f'&fields={concatenated_fields}'+\
                f'&filters=position.in.{positions}'
                
            data = self.httpclient_request(request_url)
            
            response = json.loads(data)
            
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
    
    def get_players_match_stats(self, match_url):
        """Returns match data for each player.

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            DataFrames: A DataFrame for home and away teams with each row being 
                a player and in each columns a different statistic or data of 
                the player
        """

        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)
        
        request_url = f'api/v1/event/{match_id}/lineups'
        
        data = self.httpclient_request(request_url)
        response = json.loads(data)
        
        names = {'home': home_name, 'away': away_name}
        dataframes = {}
        for team in names.keys():
            data = pd.DataFrame(response[team]['players'])
            try:
                columns_list = [
                    data['player'].apply(pd.Series), data['shirtNumber'], 
                    data['jerseyNumber'], data['position'], data['substitute'],
                    data['statistics'].apply(pd.Series, dtype=object),
                    data['captain']
                ]
            except KeyError:
                raise MatchDoesntHaveInfo(match_url)
            
            df = pd.concat(columns_list, axis=1)
            df['team'] = names[team]
            dataframes[team] = df
        
        return dataframes['home'], dataframes['away']
    
    def get_team_names(self, match_url):
        """Get the team names for the home and away teams

        Args:
            match_url (string): Full link to a SofaScore match

        Returns:
            strings: Name of home and away team.
        """

        data = self.get_match_data(match_url)

        try:
            home_team = data['event']['homeTeam']['name']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        away_team = data['event']['awayTeam']['name']

        return home_team, away_team
    
    def get_players_average_positions(self, match_url):
        """Return player averages positions for each team

        Args:
            match_url (str): Full link to a SofaScore match

        Returns:
            list of DataFrames: Each row is a player and columns averageX and averageY 
                denote their average position on the match.
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)

        request_url = f'api/v1/event/{match_id}/average-positions'

        data = self.httpclient_request(request_url)
        response = json.loads(data)
        
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
        
        request_url = f'api/v1/event/{match_id}/lineups'
        
        data = self.httpclient_request(request_url)
        response = json.loads(data)
        
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

        request_url = f'api/v1/event/{match_id}/player/{player_id}/heatmap'
        
        data = self.httpclient_request(request_url)
        response = json.loads(data)
        
        try:
            heatmap = pd.DataFrame(response['heatmap'])
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)
        
        return heatmap
    
    def get_player_season_heatmap(self, league, season, player_id):
        """Get a player season heatmap as shown in the player page in SofaScore UI

        Args:
            league (_type_): _description_
            season (_type_): _description_
            player_id (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        request_url = f'api/v1/player/{player_id}/unique-tournament/{league_id}/season/{season_id}/heatmap/overall'
        
        data = self.httpclient_request(request_url)
        response = json.loads(data)
        
        try:
            season_heatmap = pd.DataFrame(response['points'])
        except KeyError:
            raise PlayerDoesntHaveInfo(player_id)

        return season_heatmap

import json
import re
import subprocess
import sys
import numpy as np
from datetime import datetime
from typing import Optional
import time
from .functions import get_possible_leagues_for_page, pd, uc, get_random_rate_sleep
from .exceptions import InvalidStrType, MatchDoesntHaveInfo, PlayerDoesntHaveInfo
from faker import Faker
from faker.providers import user_agent
from bs4 import BeautifulSoup


def _get_chrome_major_version() -> Optional[int]:
    """Detect the installed Chrome major version to avoid chromedriver mismatch."""
    cmds = []
    if sys.platform == "win32":
        cmds = [
            ['reg', 'query', r'HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon', '/v', 'version'],
            ['reg', 'query', r'HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon', '/v', 'version'],
        ]
    elif sys.platform == "darwin":
        cmds = [['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version']]
    else:
        cmds = [
            ['google-chrome', '--version'],
            ['google-chrome-stable', '--version'],
            ['/usr/bin/google-chrome', '--version'],
            ['/usr/bin/google-chrome-stable', '--version'],
            ['chromium-browser', '--version'],
            ['chromium', '--version'],
        ]

    for cmd in cmds:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
            match = re.search(r'(\d+)\.\d+\.\d+', out)
            if match:
                return int(match.group(1))
        except Exception:
            continue
    return None

def _get_system_chromedriver_path() -> Optional[str]:
    """Return the path to a system-installed chromedriver, or None to let uc download its own."""
    candidates = [
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
    ]
    for path in candidates:
        try:
            out = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5).stdout
            if 'ChromeDriver' in out:
                return path
        except Exception:
            continue
    return None


fake = Faker()
fake.add_provider(user_agent)

user_agent_provider = fake.user_agent

class SofaScore:

    def __init__(self) -> None:
        self.league_stats_fields = [
            'goals',
            'yellowCards',
            'redCards',
            'groundDuelsWon',
            'groundDuelsWonPercentage',
            'aerialDuelsWon',
            'aerialDuelsWonPercentage',
            'successfulDribbles',
            'successfulDribblesPercentage',
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
            'passToAssist',
            'rating'
            ]
        self.base_url = 'https://www.sofascore.com/'
        self._driver = None

    def __enter__(self) -> 'SofaScore':
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def close(self) -> None:
        """Close the persistent Chrome session and free resources."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception:
                pass
            try:
                self._driver.service.process.kill()
            except Exception:
                pass
            self._driver = None

    def get_match_id(self, match_url: str) -> str:
        """Get match id for any match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Match id extracted from the URL.
        """
        if type(match_url) != str:
            raise InvalidStrType(match_url)

        match_id = match_url.split(':')[-1]
        return match_id

    def _build_driver(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f'user-agent={Faker().chrome()}')
        return uc.Chrome(
            options=chrome_options,
            version_main=_get_chrome_major_version(),
            driver_executable_path=_get_system_chromedriver_path(),
        )

    def _ensure_driver(self):
        if self._driver is None:
            self._driver = self._build_driver()
        return self._driver

    def _fetch_with_driver(self, driver, path: str) -> dict:
        url = f"{self.base_url}{path}"
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        data = json.loads(soup.text)
        time.sleep(get_random_rate_sleep(1, 3.5))
        return data

    def sofascore_request(self, path: str) -> dict:
        """Make a request to SofaScore reusing the persistent Chrome session.

        Args:
            path: API path relative to the SofaScore base URL.

        Returns:
            Parsed JSON response as a dict.
        """
        driver = self._ensure_driver()
        return self._fetch_with_driver(driver, path)

    def get_match_data(self, match_url: str) -> dict:
        """Get all general data from a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Raw JSON dict with match data.
        """
        match_id = self.get_match_id(match_url)
        data = self.sofascore_request(f'api/v1/event/{match_id}')
        time.sleep(get_random_rate_sleep(1.5, 2.5))
        return data

    def get_match_momentum(self, match_url: str) -> pd.DataFrame:
        """Get values of the momentum graph in SofaScore UI.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            DataFrame with momentum graph points.
        """
        match_id = self.get_match_id(match_url)
        data = self.sofascore_request(f'api/v1/event/{match_id}/graph')

        try:
            points = data['graphPoints']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)

        return pd.DataFrame(points)

    def get_match_shotmap(self, match_url: str, save_csv: bool = False) -> pd.DataFrame:
        """Get a DataFrame with data of the shots of a match.

        Args:
            match_url: Full link to a SofaScore match.
            save_csv: Save the DataFrame to a csv. Defaults to False.

        Returns:
            DataFrame with all shot data shown in SofaScore UI,
            enriched with match_id, teamName and vs teamName.
        """
        match_id = self.get_match_id(match_url)

        data = self.sofascore_request(f'api/v1/event/{match_id}/shotmap')
        if 'shotmap' not in data:
            raise MatchDoesntHaveInfo(match_url)

        match_shots = pd.DataFrame(data['shotmap'])
        if save_csv:
            today = datetime.now().strftime('%Y-%m-%d')
            match_shots.to_csv(f'shots match - {match_id} - {today}.csv')

        players = match_shots['player'].apply(pd.Series)
        coordenates = match_shots['playerCoordinates'].apply(pd.Series)
        match_shots = pd.concat([match_shots.drop(columns=['player']), players], axis=1)
        match_shots = pd.concat([match_shots.drop(columns=['playerCoordinates']), coordenates], axis=1)
        match_shots['match_id'] = match_id

        event_data = self.sofascore_request(f'api/v1/event/{match_id}')
        home_name = (event_data.get('event') or {}).get('homeTeam', {}).get('name')
        away_name = (event_data.get('event') or {}).get('awayTeam', {}).get('name')
        home_id = (event_data.get('event') or {}).get('homeTeam', {}).get('id')
        away_id = (event_data.get('event') or {}).get('awayTeam', {}).get('id')
        tournament_name = (event_data.get('event') or {}).get('season', {}).get('name')
        season_year = (event_data.get('event') or {}).get('season', {}).get('year')

        if 'isHome' in match_shots.columns and home_name is not None and home_id is not None:
            match_shots['teamName'] = np.where(match_shots['isHome'], home_name, away_name)
            match_shots['vs teamName'] = np.where(match_shots['isHome'], away_name, home_name)
            match_shots['teamId'] = np.where(match_shots['isHome'], home_id, away_id)
            match_shots['vs teamId'] = np.where(match_shots['isHome'], away_id, home_id)
        if tournament_name is not None:
            match_shots['tournament'] = tournament_name
        if season_year is not None:
            match_shots['year'] = season_year

        return match_shots

    def get_positions(self, selected_positions: list) -> str:
        """Return the position filter string for scrape_league_stats().

        Args:
            selected_positions: List of positions to include.
                Options: 'Goalkeepers', 'Defenders', 'Midfielders', 'Forwards'.

        Returns:
            Tilde-separated position codes (e.g. 'G~D~M~F').
        """
        positions = {
            'Goalkeepers': 'G',
            'Defenders': 'D',
            'Midfielders': 'M',
            'Forwards': 'F'
        }
        abbreviations = [positions[position] for position in selected_positions]
        return '~'.join(abbreviations)

    def scrape_league_stats(
        self,
        league: str,
        season: str,
        save_csv: bool = False,
        accumulation: str = 'total',
        selected_positions: list = ['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']
    ) -> pd.DataFrame:
        """Get every player statistic available in league pages on SofaScore.

        Args:
            league: League name from get_available_leagues("Sofascore").
            season: Season from get_available_season_for_leagues("Sofascore", league).
            save_csv: Save the result to a CSV file. Defaults to False.
            accumulation: One of 'total', 'per90', 'perMatch'. Defaults to 'total'.
            selected_positions: Positions to include. Defaults to all positions.

        Returns:
            DataFrame with one row per player and all available stats as columns.
        """
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]
        positions = self.get_positions(selected_positions)
        concatenated_fields = "%2C".join(self.league_stats_fields)

        offset = 0
        df = pd.DataFrame()
        for _ in range(0, 20):
            request_url = (
                f'api/v1/unique-tournament/{league_id}/season/{season_id}/statistics'
                f'?limit=100&order=-rating&offset={offset}'
                f'&accumulation={accumulation}'
                f'&fields={concatenated_fields}'
                f'&filters=position.in.{positions}'
            )
            data = self.sofascore_request(request_url)

            new_df = pd.DataFrame(data['results'])
            player_expanded = new_df.player.apply(pd.Series)
            new_df['id'] = player_expanded['id']
            new_df['player'] = player_expanded['name']
            team_expanded = new_df.team.apply(pd.Series)
            new_df['team_id'] = team_expanded['id']
            new_df['team'] = team_expanded['name']
            df = pd.concat([df, new_df])

            if data.get('page') == data.get('pages'):
                print('End of the pages')
                break
            offset += 100

        if save_csv:
            df.to_csv(f'{league} {season} stats.csv')

        return df

    def get_players_match_stats(self, match_url: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Get match stats for each player in a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Tuple of (home_df, away_df), one row per player with stats as columns.
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)

        response = self.sofascore_request(f'api/v1/event/{match_id}/lineups')

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

    def get_team_names(self, match_url: str) -> tuple[str, str]:
        """Get the home and away team names for a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Tuple of (home_name, away_name).
        """
        data = self.get_match_data(match_url)

        try:
            home_team = data['event']['homeTeam']['name']
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)

        away_team = data['event']['awayTeam']['name']
        return home_team, away_team

    def get_players_average_positions(self, match_url: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Get average positions for each player in a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Tuple of (home_df, away_df) with averageX and averageY columns per player.
        """
        match_id = self.get_match_id(match_url)
        home_name, away_name = self.get_team_names(match_url)

        response = self.sofascore_request(f'api/v1/event/{match_id}/average-positions')

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

    def get_lineups(self, match_url: str) -> dict:
        """Get raw lineups JSON for a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Raw lineups dict with 'home' and 'away' keys.
        """
        match_id = self.get_match_id(match_url)
        return self.sofascore_request(f'api/v1/event/{match_id}/lineups')

    def get_player_ids(self, match_url: str) -> dict[str, int]:
        """Get all player IDs for a match.

        Args:
            match_url: Full link to a SofaScore match.

        Returns:
            Dict mapping player name to player ID.
        """
        response = self.get_lineups(match_url)

        player_ids = {}
        for team in ['home', 'away']:
            for item in response[team]['players']:
                player_data = item['player']
                player_ids[player_data['name']] = player_data['id']

        return player_ids

    def get_player_heatmap(self, match_url: str, player: str) -> pd.DataFrame:
        """Get x-y coordinates to create a player heatmap with kdeplot.

        Args:
            match_url: Full link to a SofaScore match.
            player: Exact player name as shown in SofaScore. Use get_player_ids() to look it up.

        Returns:
            DataFrame with x-y coordinates.
        """
        match_id = self.get_match_id(match_url)
        player_ids = self.get_player_ids(match_url)
        player_id = player_ids[player]

        data = self.sofascore_request(f'api/v1/event/{match_id}/player/{player_id}/heatmap')

        try:
            heatmap = pd.DataFrame(data['heatmap'])
        except KeyError:
            raise MatchDoesntHaveInfo(match_url)

        return heatmap

    def get_player_match_events(
        self,
        match_url: str,
        player: str,
        events: Optional[list | str] = None
    ) -> pd.DataFrame:
        """Get x-y coordinates for a player's in-match events.

        Args:
            match_url: Full link to a SofaScore match.
            player: Exact player name as shown in SofaScore. Use get_player_ids() to look it up.
            events: Which event categories to include.
                - None: ['passes', 'ball-carries', 'dribbles', 'defensive']
                - 'all': every available category in the response
                - list: specific categories e.g. ['passes', 'dribbles']

        Returns:
            DataFrame with x-y coordinates and a 'category' column.
        """
        match_id = self.get_match_id(match_url)
        player_ids = self.get_player_ids(match_url)
        player_id = player_ids[player]

        data = self.sofascore_request(f'api/v1/event/{match_id}/player/{player_id}/rating-breakdown')

        if 'error' in data:
            raise MatchDoesntHaveInfo(match_url)

        if events is None:
            categories = [k for k in ['passes', 'ball-carries', 'dribbles', 'defensive'] if k in data]
        elif events == 'all':
            categories = [k for k, v in data.items() if isinstance(v, list)]
        else:
            categories = [k for k in events if k in data]

        if not categories:
            return pd.DataFrame()

        df_player_events = pd.concat(
            [pd.json_normalize(data[k]).assign(category=k) for k in categories],
            ignore_index=True
        )

        df_player_events.rename(columns={
            'playerCoordinates.x': 'x',
            'playerCoordinates.y': 'y',
            'passEndCoordinates.x': 'end_x',
            'passEndCoordinates.y': 'end_y'
        }, inplace=True)

        cols = ['category'] + [c for c in df_player_events.columns if c != 'category']
        return df_player_events[cols]

    def get_player_season_heatmap(self, league: str, season: str, player_id: int) -> pd.DataFrame:
        """Get a player's season heatmap as shown on the SofaScore player page.

        Args:
            league: League name from get_available_leagues("Sofascore").
            season: Season from get_available_season_for_leagues("Sofascore", league).
            player_id: Numeric SofaScore player ID from the player's URL.

        Returns:
            DataFrame with x-y coordinate points.
        """
        league_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['id']
        season_id = get_possible_leagues_for_page(league, season, 'Sofascore')[league]['seasons'][season]

        data = self.sofascore_request(
            f'api/v1/player/{player_id}/unique-tournament/{league_id}/season/{season_id}/heatmap/overall'
        )

        try:
            season_heatmap = pd.DataFrame(data['points'])
        except KeyError:
            raise PlayerDoesntHaveInfo(player_id)

        return season_heatmap

import asyncio
import re
import json
import sys
import time
import threading
import pandas as pd
import nodriver as uc
from .functions import get_possible_leagues_for_page, get_random_rate_sleep
from .exceptions import (
    InvalidStat, MatchDoesntHaveInfo,
    FotMobConnectionError, FotMobParseError, FotMobTimeoutError,
)


class _FotMobResponse:
    """
    Thin wrapper around a parsed dict that exposes a .json() method.
    Keeps all internal callers backward-compatible without changes.
    """
    def __init__(self, data: dict):
        self._data = data

    def json(self):
        return self._data


class FotMob:

    def __init__(self, request_delay: float = 1.0):
        self.player_possible_stats = [
            'goals',
            'goal_assist',
            '_goals_and_goal_assist',
            'rating',
            'goals_per_90',
            'expected_goals',
            'expected_goals_per_90',
            'expected_goalsontarget',
            'ontarget_scoring_att',
            'total_scoring_att',
            'accurate_pass',
            'big_chance_created',
            'total_att_assist',
            'accurate_long_balls',
            'expected_assists',
            'expected_assists_per_90',
            '_expected_goals_and_expected_assists_per_90',
            'won_contest',
            'big_chance_missed',
            'penalty_won',
            'won_tackle',
            'interception',
            'effective_clearance',
            'outfielder_block',
            'penalty_conceded',
            'poss_won_att_3rd',
            'clean_sheet',
            '_save_percentage',
            'saves',
            '_goals_prevented',
            'goals_conceded',
            'fouls',
            'yellow_card',
            'red_card',
        ]

        self.team_possible_stats = [
            'rating_team',
            'goals_team_match',
            'goals_conceded_team_match',
            'possession_percentage_team',
            'clean_sheet_team',
            'expected_goals_team',
            'ontarget_scoring_att_team',
            'big_chance_team',
            'big_chance_missed_team',
            'accurate_pass_team',
            'accurate_long_balls_team',
            'accurate_cross_team',
            'penalty_won_team',
            'touches_in_opp_box_team',
            'corner_taken_team',
            'expected_goals_conceded_team',
            'interception_team',
            'won_tackle_team',
            'effective_clearance_team',
            'poss_won_att_3rd_team',
            'penalty_conceded_team',
            'saves_team',
            'fk_foul_lost_team',
            'total_yel_card_team',
            'total_red_card_team',
        ]

        self._browser = None
        self._warmed_up = False
        self.request_delay = request_delay
        self._FETCH_TIMEOUT = 30   # seconds per request
        self._WARMUP_WAIT = 5      # seconds to resolve Turnstile on homepage
        self._MAX_RETRIES = 3

        # Dedicated background event loop — makes FotMob work from scripts AND
        # Jupyter notebooks (which already have a running event loop that would
        # reject run_until_complete). All browser/async operations run on this
        # thread; _submit() dispatches coroutines to it safely from any context.
        #
        # On Windows, SelectorEventLoop (the default from new_event_loop()) does
        # not support subprocesses — nodriver needs to launch Chrome as a subprocess,
        # so we must use ProactorEventLoop on Windows.
        if sys.platform == 'win32':
            self._loop = asyncio.ProactorEventLoop()
        else:
            self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._loop.run_forever,
            daemon=True,
            name="FotMob-event-loop",
        )
        self._loop_thread.start()

    # ─── Browser lifecycle ────────────────────────────────────────────────────

    async def _start_browser(self):
        """
        Inicia nodriver y hace el warm-up en la homepage de FotMob para que
        Cloudflare Turnstile resuelva automáticamente antes de cualquier request.
        """
        print("[FotMob] Iniciando browser (nodriver)...")
        self._browser = await uc.start()
        await self._browser.get("https://www.fotmob.com")
        await asyncio.sleep(self._WARMUP_WAIT)
        self._warmed_up = True
        print("[FotMob] Browser listo.")

    async def _ensure_browser(self):
        """Garantiza que el browser esté corriendo y el warm-up esté hecho."""
        if self._browser is None or not self._warmed_up:
            await self._start_browser()

    def _submit(self, coro):
        """
        Envía una corrutina al background loop y bloquea hasta obtener el resultado.
        Funciona desde cualquier contexto: script, Jupyter, función async, etc.
        """
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=self._FETCH_TIMEOUT + 15)

    def close(self):
        """
        Cierra el browser de nodriver y libera recursos.

        Uso:
            fotmob = FotMob()
            # ... uso normal ...
            fotmob.close()
        """
        if self._browser is not None:
            try:
                self._browser.stop()
            except Exception:
                pass
            self._browser = None
            self._warmed_up = False
        if self._loop is not None and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    # ─── Core fetch ───────────────────────────────────────────────────────────

    async def _async_fetch(self, url: str) -> dict:
        """
        Navega a `url` con nodriver y extrae el JSON de la respuesta.

        - Extrae el contenido del <pre> que devuelve el browser en endpoints JSON.
        - Si no hay <pre>, asume Cloudflare challenge y reintenta con espera incremental.
        - Si el browser se cae, lo detecta y reinicia antes de reintentar.
        - Timeout por request: self._FETCH_TIMEOUT segundos.

        Args:
            url (str): URL completa a fetchear.

        Returns:
            dict: JSON parseado de la respuesta.

        Raises:
            FotMobConnectionError: Si Cloudflare sigue bloqueando tras los reintentos.
            FotMobParseError: Si la respuesta no es JSON válido.
            FotMobTimeoutError: Si se supera el timeout.
        """
        await self._ensure_browser()

        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                page = await asyncio.wait_for(
                    self._browser.get(url),
                    timeout=self._FETCH_TIMEOUT,
                )
                await asyncio.sleep(2)  # espera mínima para que cargue el contenido
                content = await page.get_content()

                match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
                if not match:
                    # Sin <pre> → probable Cloudflare challenge
                    if attempt < self._MAX_RETRIES:
                        wait_s = self._WARMUP_WAIT * attempt
                        print(
                            f"[FotMob] Challenge detectado, esperando {wait_s}s "
                            f"(intento {attempt}/{self._MAX_RETRIES})..."
                        )
                        await asyncio.sleep(wait_s)
                        continue
                    raise FotMobConnectionError("unknown", content[:200])

                raw = match.group(1).strip()
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    raise FotMobParseError(raw[:500])

            except asyncio.TimeoutError:
                if attempt < self._MAX_RETRIES:
                    print(f"[FotMob] Timeout, reiniciando browser (intento {attempt}/{self._MAX_RETRIES})...")
                    await self._restart_browser()
                    continue
                raise FotMobTimeoutError(url)

            except (FotMobConnectionError, FotMobParseError, FotMobTimeoutError):
                raise

            except Exception as e:
                if attempt < self._MAX_RETRIES:
                    print(f"[FotMob] Error de browser ({type(e).__name__}: {e}), reiniciando (intento {attempt}/{self._MAX_RETRIES})...")
                    await self._restart_browser()
                    continue
                raise

    def _reset_browser(self):
        """Marca el browser como inválido para forzar un reinicio en el próximo fetch."""
        try:
            self._browser.stop()
        except Exception:
            pass
        self._browser = None
        self._warmed_up = False

    async def _restart_browser(self):
        """Resetea el estado del browser y lo reinicia con warm-up."""
        self._reset_browser()
        await self._start_browser()

    def _fetch(self, url: str) -> dict:
        """
        Wrapper sincrónico sobre _async_fetch. Despacha la corrutina al
        background loop dedicado, bloqueando hasta obtener el resultado.
        Funciona desde scripts .py, Jupyter notebooks, y funciones async.

        Args:
            url (str): URL completa a fetchear.

        Returns:
            dict: JSON parseado de la respuesta.
        """
        return self._submit(self._async_fetch(url))

    def fotmob_request(self, path: str) -> _FotMobResponse:
        """
        Hace una request a la API de FotMob usando nodriver con bypass de Cloudflare.

        Args:
            path (str): Path de la API (sin la base URL). Ej: 'matchDetails?matchId=123'

        Returns:
            _FotMobResponse: Objeto con método .json() que retorna el dict de la respuesta.
        """
        url = f'https://www.fotmob.com/api/{path}'
        data = self._fetch(url)
        time.sleep(self.request_delay)
        return _FotMobResponse(data)

    # ─── Public methods (interfaz sin cambios) ────────────────────────────────

    def get_season_tables(self, league, season, table=['all', 'home', 'away', 'form', 'xg']):
        """Get standing tables from a list of possible ones from a certain season in a league.

        Args:
            league (str): Possible leagues in get_available_leagues("Fotmob")
            season (str): Possible season in get_available_season_for_leagues("Fotmob", league)
            table (list, optional): Type of table shown in FotMob UI. Defaults to ['all', 'home', 'away', 'form', 'xg'].

        Returns:
            table_df: DataFrame with the table/s.
        """
        leagues = get_possible_leagues_for_page(league, season, 'Fotmob')
        league_id = leagues[league]['id']
        season_string = season.replace('/', '%2F')
        path = f'leagues?id={league_id}&ccode3=ARG&season={season_string}'
        response = self.fotmob_request(path)
        try:
            tables = response.json()['table'][0]['data']['table']
            table = tables[table]
            table_df = pd.DataFrame(table)
        except KeyError:
            tables = response.json()['table'][0]['data']['tables']
            table_df = tables
            print(
                'This response has a list of two values, because the tables are split. '
                'If you save the list in a variable and then do variable[0]["table"] you will have all of the tables\n'
                'Then just select one ["all", "home", "away", "form", "xg"] that exists and put it inside a pd.DataFrame()\n'
                'Something like pd.DataFrame(variable[0]["table"]["all"])'
            )
        return table_df

    def request_match_details(self, match_id):
        """Get match details with a request.

        Args:
            match_id (str): Id of a certain match, could be found in the URL.

        Returns:
            _FotMobResponse: Object with .json() returning the full match details dict.
        """
        path = f'matchDetails?matchId={match_id}'
        response = self.fotmob_request(path)
        return response

    def get_players_stats_season(self, league, season, stat):
        """Get players stats for a certain season and league. Possible stats are player_possible_stats.

        Args:
            league (str): Possible leagues in get_available_leagues("Fotmob")
            season (str): Possible season in get_available_season_for_leagues("Fotmob", league)
            stat (str): Value inside player_possible_stats

        Raises:
            InvalidStat: Raised when the input of stat is not inside the possible list values.

        Returns:
            df: DataFrame with the values and player names for that stat.
        """
        print(f'Possible values for stat parameter: {self.player_possible_stats}')
        if stat not in self.player_possible_stats:
            raise InvalidStat(stat, self.player_possible_stats)
        leagues = get_possible_leagues_for_page(league, season, 'Fotmob')
        league_id = leagues[league]['id']
        season_id = leagues[league]['seasons'][season]
        path = f'leagueseasondeepstats?id={league_id}&season={season_id}&type=players&stat={stat}'
        response = self.fotmob_request(path)
        stats_data = response.json()['statsData']
        df = pd.DataFrame(stats_data)
        df = pd.concat([df, df.statValue.apply(pd.Series)], axis=1)
        return df

    def get_teams_stats_season(self, league, season, stat):
        """Get teams stats for a certain season and league. Possible stats are team_possible_stats.

        Args:
            league (str): Possible leagues in get_available_leagues("Fotmob")
            season (str): Possible season in get_available_season_for_leagues("Fotmob", league)
            stat (str): Value inside team_possible_stats

        Raises:
            InvalidStat: Raised when the input of stat is not inside the possible list values.

        Returns:
            df: DataFrame with stat values for teams in a league and season.
        """
        print(f'Possible values for stat parameter: {self.team_possible_stats}')
        if stat not in self.team_possible_stats:
            raise InvalidStat(stat, self.team_possible_stats)
        leagues = get_possible_leagues_for_page(league, season, 'Fotmob')
        league_id = leagues[league]['id']
        season_id = leagues[league]['seasons'][season]
        path = f'leagueseasondeepstats?id={league_id}&season={season_id}&type=teams&stat={stat}'
        response = self.fotmob_request(path)
        stats_data = response.json()['statsData']
        df = pd.DataFrame(stats_data)
        df = pd.concat([df, df.statValue.apply(pd.Series)], axis=1)
        return df

    def get_match_shotmap(self, match_id):
        """Scrape a match shotmap, if it has one.

        Args:
            match_id (str): Id of a FotMob match, could be found in the URL.
                            Example: https://www.fotmob.com/es/matches/boca-juniors-vs-newells-old-boys/3ef4me#4393680
                            4393680 is the match_id.

        Raises:
            MatchDoesntHaveInfo: Raised when the match associated with the match_id doesn't have a shotmap.

        Returns:
            shotmap: DataFrame with the data for all the shots shown in the FotMob UI.
        """
        response = self.request_match_details(match_id)
        df_shotmap = pd.DataFrame(response.json()['content']['shotmap']['shots'])
        if df_shotmap.empty:
            raise MatchDoesntHaveInfo(match_id)
        ongoalshot = df_shotmap.onGoalShot.apply(pd.Series).rename(columns={'x': 'goalMouthY', 'y': 'goalMouthZ'})
        shotmap = pd.concat([df_shotmap, ongoalshot], axis=1).drop(columns=['onGoalShot'])
        return shotmap

    def get_team_colors(self, match_id):
        """Get team colors as FotMob UI uses.

        Args:
            match_id (str): Id of a FotMob match, could be found in the URL.
                            Example: https://www.fotmob.com/es/matches/boca-juniors-vs-newells-old-boys/3ef4me#4393680
                            4393680 is the match_id.

        Returns:
            home_color, away_color: strings with hex codes.
        """
        response = self.request_match_details(match_id)
        colors = response.json()['general']['teamColors']
        home_color = colors['darkMode']['home']
        away_color = colors['darkMode']['away']

        if home_color == '#ffffff':
            home_color = colors['lightMode']['home']
        if away_color == '#ffffff':
            away_color = colors['lightMode']['away']
        return home_color, away_color

    def get_general_match_stats(self, match_id):
        """Get general match stats for a certain match (shots, passes, duels won for the teams).

        Args:
            match_id (str): Id of a FotMob match, could be found in the URL.
                            Example: https://www.fotmob.com/es/matches/boca-juniors-vs-newells-old-boys/3ef4me#4393680
                            4393680 is the match_id.

        Returns:
            total_df: DataFrame with the stats of the teams for a certain match.
        """
        response = self.request_match_details(match_id)
        total_df = pd.DataFrame()
        stats_df = response.json()['content']['stats']['Periods']['All']['stats']
        for item in stats_df:
            total_df = pd.concat([pd.DataFrame(item['stats']), total_df])
        total_df = pd.concat(
            [total_df, total_df.stats.apply(pd.Series).rename(columns={0: 'home', 1: 'away'})],
            axis=1,
        ).drop(columns=['stats']).dropna(subset=['home', 'away'])
        return total_df

    def get_player_season_stats(self, season_index, competition_index, player_id):
        """Scrape a player stats from a certain league and season, if they have one.

        Args:
            season_index (str): Position of the season in the dropdown on FotMob UI.
            competition_index (str): Position of the competition in a season in the dropdown on FotMob UI.
            player_id (str): FotMob Id of a player. Could be found in the URL of a specific player.
                             Example: https://www.fotmob.com/es/players/727095/ignacio-ramirez
                             727095 is the player_id.

        Returns:
            dict: JSON with the data for all the stats shown in the FotMob UI.
        """
        path = f'playerStats?playerId={player_id}&seasonId={season_index}-{competition_index}&isFirstSeason=false'
        response = self.fotmob_request(path)
        return response.json()

    def get_player_shotmap(self, season_index, competition_index, player_id):
        """Scrape a player shotmap from a certain league and season, if they have one.

        Args:
            season_index (str): Position of the season in the dropdown on FotMob UI.
            competition_index (str): Position of the competition in a season in the dropdown on FotMob UI.
            player_id (str): FotMob Id of a player. Could be found in the URL of a specific player.
                             Example: https://www.fotmob.com/es/players/727095/ignacio-ramirez
                             727095 is the player_id.

        Returns:
            shotmap: DataFrame with the data for all the shots shown in the FotMob UI.
        """
        response = self.get_player_season_stats(season_index, competition_index, player_id)
        try:
            shotmap = pd.DataFrame(response['shotmap'])
        except TypeError:
            raise MatchDoesntHaveInfo(player_id)
        return shotmap

    def get_player_percentiles(self, season_index, competition_index, player_id):
        """Scrape a player percentiles from a certain league and season, if they have one.

        Args:
            season_index (str): Position of the season in the dropdown on FotMob UI.
            competition_index (str): Position of the competition in a season in the dropdown on FotMob UI.
            player_id (str): FotMob Id of a player. Could be found in the URL of a specific player.
                             Example: https://www.fotmob.com/es/players/727095/ignacio-ramirez
                             727095 is the player_id.

        Returns:
            df_percentiles: DataFrame with the data for all the percentiles shown in the FotMob UI.
        """
        response = self.get_player_season_stats(season_index, competition_index, player_id)
        try:
            stats = pd.DataFrame(response['statsSection']['items'])
            df_exploded = stats.explode('items')
            df_percentiles = pd.json_normalize(df_exploded["items"])
        except TypeError:
            raise MatchDoesntHaveInfo(player_id)
        return df_percentiles

    def get_player_data(self, player_id):
        """Scrape a player data.

        Args:
            player_id (str): FotMob Id of a player. Could be found in the URL of a specific player.
                             Example: https://www.fotmob.com/es/players/727095/ignacio-ramirez
                             727095 is the player_id.

        Returns:
            dict: JSON with the data available of a player.
        """
        path = f'/data/playerData?id={player_id}'
        response = self.fotmob_request(path)
        return response.json()

class InvalidStat(Exception):
    def __init__(self, param, invalid_value, possible_values):
        super().__init__(f"Value '{invalid_value}' for param '{param}' is invalid. Possible values are {possible_values}.\nEl valor '{invalid_value}' para el parámetro '{param}' no es válido. Los valores válidos son: {possible_values}")

class InvalidLeagueException(Exception):
    def __init__(self, league, possible_leagues_list):
        self.message = f"League {league} is not valid for any of the possible leagues {possible_leagues_list}."
        super().__init__(self.message)
        
class InvalidSeasonException(Exception):
    def __init__(self, season, possible_seasons_list):
        self.message = f"Season {season} is not valid for any of the possible seasons for this league {possible_seasons_list}."
        super().__init__(self.message)

class PlayerDoesntHaveInfo(Exception):
    def __init__(self, path):
        self.message = f"Player in path {path} doesn't have enough information for this functions, try with another one.\nEl jugador en el path {path} no tiene la información para estas funciones, pruebe con otro."
        super().__init__(self.message)

class MatchDoesntHaveInfo(Exception):
    def __init__(self, path):
        self.message = f"Match in path {path} doesn't have enough information for this functions, try with another one.\nEl partido en el path {path} no tiene la información para estas funciones, pruebe con otro."
        super().__init__(self.message)
        
class InvalidStrType(Exception):
    def __init__(self, param):
        self.message = f"{param} must be a string.\n{param} debe ser un string"
        super().__init__(self.message)

class FotMobConnectionError(Exception):
    """Raised when FotMob blocks the connection (Cloudflare challenge not resolved)."""
    def __init__(self, status, content_preview):
        super().__init__(
            f"FotMob bloqueó la conexión (status: {status}). "
            f"Primeros 200 chars de la respuesta: {content_preview}"
        )

class FotMobParseError(Exception):
    """Raised when the FotMob response is not valid JSON."""
    def __init__(self, raw):
        super().__init__(
            f"La respuesta de FotMob no es JSON válido. Contenido crudo: {raw}"
        )

class FotMobTimeoutError(Exception):
    """Raised when a single FotMob request exceeds the configured timeout."""
    def __init__(self, url):
        super().__init__(f"Timeout al hacer request a: {url}")
        

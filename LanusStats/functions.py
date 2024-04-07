from .exceptions import *

def get_possible_leagues(league, season, page):
    """Dictionary with all the possible pages, leagues and season for the scraper.
    Also contains some exception to prevent errors such as a league or page that is not a part of the scraper.

    Args:
        league (str): League to scrape
        season (str): Season to scrape
        page (str): Page to scrape

    Raises:
        InvalidStrType: If a parameter is not a string
        InvalidLeagueException: If a league is not inside all the leagues possibles
        InvalidSeasonException: If a season is not inside all the seasons possibles

    Returns:
        dict: dictionary with the possible leagues
    """
    possible_leagues = {
        'Fbref': {
            'Copa de la Liga': {
                'id': 905,
                'slug': 'Copa-de-la-Liga-Profesional',
                'seasons': {
                    '2024', '2023', '2022', '2021', '2020'
                }
            },
            'Primera Division Argentina': {
                'id': 21,
                'slug': 'Primera-Division',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Uruguay': {
                'id': 45,
                'slug': 'Primera-Division',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Brasileirao': {
                'id': 24,
                'slug': 'Serie-A',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Brasileirao B': {
                'id': 38,
                'slug': 'Serie-B',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Colombia': {
                'id': 41,
                'slug': 'Primera-A',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Chile': {
                'id': 35,
                'slug': 'Primera-Division',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Peru': {
                'id': 44,
                'slug': 'Liga-1',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Venezuela': {
                'id': 105,
                'slug': 'Liga-FUTVE',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Ecuador': {
                'id': 58,
                'slug': 'Serie-A',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Bolivia': {
                'id': 74,
                'slug': 'Bolivian-Primera-Division',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Primera Division Paraguay': {
                'id': 61,
                'slug': 'Primera-Division',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Brasileirao F': {
                'id': 206,
                'slug': 'Serie-A1',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'MLS': {
                'id': 22,
                'slug': 'Major-League-Soccer',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'USL Championship': {
                'id': 73,
                'slug': 'USL-Championship',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Premier League': {
                'id': 9,
                'slug': 'Premier-League',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'La Liga': {
                'id': 12,
                'slug': 'La-Liga',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Ligue 1': {
                'id': 13,
                'slug': 'Ligue-1',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Bundesliga': {
                'id': 20,
                'slug': 'Bundesliga',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Serie A': {
                'id': 11,
                'slug': 'Serie-A',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Big 5 European Leagues': {
                'id': 'Big5',
                'slug': 'Big-5-European-Leagues',
                'seasons': {
                    '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            }
        },
        'Sofascore': { #https://github.com/oseymour/ScraperFC/ some of the leagues ids were taken from here
            "Argentina Liga Profesional": {
                "id": 155,
                "seasons": {
                    "08/09": 1636,
                    "09/10": 2323,
                    "10/11": 2887,
                    "11/12": 3613,
                    "12/13": 5103,
                    "13/14": 6455,
                    "2014": 8338,
                    "2015": 9651,
                    "2016": 11237,
                    "16/17": 12117,
                    "17/18": 13950,
                    "18/19": 18113,
                    "19/20": 24239,
                    "2021": 37231,
                    "2022": 41884,
                    "2023": 47647,
                },
            },
            "Argentina Copa de la Liga Profesional": {
                "id": 13475,
                "seasons": {
                    "2019": 23108,
                    "2020": 34618,
                    "2021": 35486,
                    "2022": 40377,
                    "2023": 47644,
                    "2024": 57487
                },
            },
            "Argentina Primera Nacional": {
                "id": 703,
                "seasons": {
                    "2023": 48079, "2024": 57782
                },
            },
            "Brasileirão Série A": {
                "id": 325,
                "seasons": {
                    "20/21": 27591,
                    "2021": 36166,
                    "2022": 40557,
                    "2023": 48982
                },
            },
            "Bolivia Division Profesional": {
                "id": 16736,
                "seasons": {
                    "2023": 48353
                },
            },
            "Chile Primera Division": {
                "id": 11653,
                "seasons": {
                    "2023": 48017
                }
            },
            "Colombia Primera A Apertura": {
                "id": 11539,
                "seasons": {
                    "2022": 40320,
                    "2023": 48283,
                    "2024": 57374
                },
            },
            "Colombia Primera A Clausura": {
                "id": 11536,
                "seasons": {
                    "2022": 42387,
                    "2023": 52847
                },
            },
            "Ecuador LigaPro": {
                "id": 240,
                "seasons": {
                    "2022": 40503,
                    "2023": 48720
                },
            },
            "Mexico LigaMX Apertura": {
                "id": 11621,
                "seasons": {
                    "2022": 42017,
                    "2023": 52052
                },
            },
            "Mexico LigaMX Clausura": {
                "id": 11620,
                "seasons": {
                    "2022": 40080,
                    "2023": 47656,
                    "2024": 57315
                },
            },
            "Peru Liga 1": {
                "id": 406,
                "seasons": {
                    "2022": 40118,
                    "2023": 48078,
                    "2024": 57741
                },
            },
            "Uruguay Primera Division": {
                "id": 278,
                "seasons": {
                    "2023": 48634,
                },
            },
            "Venezuela Primera Division": {
                "id": 231,
                "seasons": {
                    "2023": 48742,
                    "2024": 57694
                },
            },
            "World Cup": {
                "id": 16,
                "seasons": {
                    "1930": 40712, "1934": 17559, "1938": 17560, "1950": 40714,
                    "1954": 17561, "1958": 17562, "1962": 17563, "1966": 17564,
                    "1970": 17565, "1974": 17566, "1978": 17567, "1982": 17568,
                    "1986": 17569, "1990": 17570, "1994": 17571, "1998": 1151,
                    "2002": 2636, "2006": 16, "2010": 2531, "2014": 7528,
                    "2018": 15586, "2022": 41087,
                },
            },
            "Premier League": {
                "id": 17,
                "seasons": {
                    "15/16": 10356,
                    "16/17": 11733, "17/18": 13380, "18/19": 17359,
                    "19/20": 23776, "20/21": 29415, "21/22": 37036, 
                    "22/23": 41886, "23/24": 52186,
                },
            },
            "La Liga": {
                "id": 8,
                "seasons": {
                    "15/16": 10495,
                    "16/17": 11906, "17/18": 13662, "18/19": 18020,
                    "19/20": 24127, "20/21": 32501, "21/22": 37223, 
                    "22/23": 42409, "23/24": 52376,
                },
            },
            "Bundesliga": {
                "id": 35,
                "seasons": {
                    "15/16": 10419,
                    "16/17": 11818, "17/18": 13477, "18/19": 17597, 
                    "19/20": 23538, "20/21": 28210, "21/22": 37166, 
                    "22/23": 42268, "23/24": 52608,
                },
            },
            "Serie A": {
                "id": 23,
                "seasons": {
                    "15/16": 10596, "16/17": 11966, 
                    "17/18": 13768, "18/19": 17932, "19/20": 24644, 
                    "20/21": 32523, "21/22": 37475, "22/23": 42415, 
                    "23/24": 52760,
                },
            },
            "Ligue 1": {
                "id": 34,
                "seasons": {
                    "15/16": 10373, "16/17": 11648, 
                    "17/18": 13384, "18/19": 17279, "19/20": 23872, 
                    "20/21": 28222, "21/22": 37167, "22/23": 42273, 
                    "23/24": 52571,
                },
            },
            "Copa Libertadores": {
                "id": 384,
                "seasons": {
                    "2018": 15806, "2019": 19989, "2020": 26785, 
                    "2021": 35576, "2022": 40174, "2023": 47974, 
                    "2024": 57296,
                }
            },
            "Copa Sudamericana": {
                "id": 480,
                "seasons": {
                    "2018": 15809, "2019": 19990, "2020": 26788, 
                    "2021": 35645, "2022": 40175, "2023": 47968, 
                    "2024": 57297,
                }
            }, 
        },
        '365Scores': {
            'Argentina Copa de la Liga': {
                'id': 7214,
                'seasons': None
            },
            'Primera Division Argentina': {
                'id': 72,
                'seasons': None
            },
            'Primera Nacional Argentina': {
                'id': 419,
                'seasons': None
            },
            'Brasileirao': {
                'id': 113,
                'seasons': None
            },
            'Champions League': {
                'id': 572,
                'seasons': None
            },
            'Primera Division Colombia': {
                'id': 620,
                'seasons': None
            }
        },
        'Fotmob': {
            'Premier League': {
                'id': 47,
                'seasons': {
                    '2023/2024': 20720, '2022/2023': 17664, '2021/2022': 16390, '2020/2021': 15382  
                }
            },
            'Argentina Copa de la Liga': {
                'id': 10007,
                'seasons': {
                    '2024': 22636, '2023': 18412, '2022': 17683, '2021': 16512, '2017/2020': 14230
                }
            },
            'Argentina Primera Division': {
                'id': 112,
                'seasons': {
                    '2024': 22636, '2023': 19058, '2022': 17301, '2021/2022': 16057, '2020/2021': 15756
                }
            },
            'La Liga': {
                'id': 87,
                'seasons': {
                    '2023/2024': 21053, '2022/2023': 17852, '2021/2022': 16520, '2020/2021': 15585
                }
            }
        }
    }
    
    #Exceptions or cases of error
    if season != None and type(season) != str:
        raise InvalidStrType(season)
    if type(league) != str:
        raise InvalidStrType(league)
    
    possible_leagues_list = list(possible_leagues[page].keys())
    if league not in possible_leagues_list:
        raise InvalidLeagueException('league', possible_leagues_list)
    
    possible_seasons_list = list(possible_leagues[page][league]['seasons'])
    if season != None and season not in possible_seasons_list:
        raise InvalidSeasonException('league', possible_seasons_list)
    
    return possible_leagues

def get_possible_leagues_for_page(league, season, page):
    """Get possible leagues for a particular page

    Args:
        league (str): League to scrape
        season (str): Season to scrape
        page (str): Page to scrape

    Returns:
        dict: leagues that are possible for that page.
    """
    leagues = get_possible_leagues(league, season, page)[page]
    return leagues
    
def possible_stats_exception(possible_stats, stat):
    if stat not in possible_stats:
        raise InvalidStat('stat', stat, possible_stats)
    
def invalid_type_str_exception(params):
    if type(params) != str:
        raise InvalidStrType(params)
    
def get_available_pages():
    """Get available pages inside the scraper functions of this repo

    Returns:
        list: List of possible leagues to scrape.
    """
    dict_possible = get_possible_leagues('Argentina Copa de la Liga', '2023', 'Fotmob')
    return dict_possible.keys()

def get_available_leagues(page):
    """Get available leagues inside a page (passed as a parameter) for the scraper functions of that page class.

    Args:
        page (str): Page inside the array of get_available_pagues()

    Returns:
        list: List of possible leagues to scrape in this page.
    """
    available_leagues = list(get_possible_leagues('Argentina Copa de la Liga', '2023', 'Fotmob')[page].keys())
    return available_leagues

def get_available_season_for_leagues(page, league):
    """Get avaiable seasons configured inside of the functions get_possible_leagues as well as all the data for that page and league.

    Args:
        page (str): Page inside the array of get_available_pagues()
        league (str): League inside the array of get_available_leagues(page)

    Returns:
        dict: League data with the seasons inside
    """
    league_data = get_possible_leagues('Argentina Copa de la Liga', '2023', 'Fotmob')[page][league]
    return league_data

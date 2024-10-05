from .exceptions import *
import numpy as np

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
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'La Liga': {
                'id': 12,
                'slug': 'La-Liga',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Ligue 1': {
                'id': 13,
                'slug': 'Ligue-1',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Bundesliga': {
                'id': 20,
                'slug': 'Bundesliga',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Serie A': {
                'id': 11,
                'slug': 'Serie-A',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Big 5 European Leagues': {
                'id': 'Big5',
                'slug': 'Big-5-European-Leagues',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Danish Superliga': {
                'id': 50,
                'slug': 'Superliga',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Eredivise': {
                'id': 23,
                'slug': 'Eredivise',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Primeira Liga Portugal': {
                'id': 32,
                'slug': 'Primeira-Liga',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Copa America': {
                'id': 685,
                'slug': 'Copa-America',
                'season': {
                    '2024', '2021', '2019'
                }
            },
            'Euros': {
                'id': 676,
                'slug': 'European-Championship',
                'seasons': {
                    '2024', '2021', '2016'
                }
            },
            'Saudi League': {
                'id': 70,
                'slug': 'Saudi-Professional-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022'
                }
            },
            'EFL Championship': {
                'id': 10,
                'slug': 'Championship',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'La Liga 2': {
                'id': 17,
                'slug': 'Segunda-Division',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Belgian Pro League': {
                'id': 37,
                'slug': 'Belgian-Pro-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Challenger Pro League': {
                'id': 69,
                'slug': 'Challenger-Pro-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022'
                }
            },
            '2. Bundesliga': {
                'id': 33,
                'slug': '2-Bundesliga',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Ligue 2': {
                'id': 60,
                'slug': 'Ligue-2',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Serie B': {
                'id': 18,
                'slug': 'Serie-B',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'J1 League': {
                'id': 25,
                'slug': 'J1-League',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'NSWL': {
                'id': 182,
                'slug': 'NSWL',
                'seasons': {
                    '2024', '2023', '2022', '2021'
                }
            },
            'Wowens Super League': {
                'id': 189,
                'slug': 'Womens-Super-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Liga F': {
                'id': 230,
                'slug': 'Liga-F',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Premier Division South Africa': {
                'id': 52,
                'slug': 'Premier-Division',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021'
                }
            },
            'Champions League': {
                'id': 8,
                'slug': 'Champions-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Europa League': {
                'id': 19,
                'slug': 'Europa-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            },
            'Conference League': {
                'id': 882,
                'slug': 'Conference-League',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023'
                }
            },
            'Copa Libertadores': {
                'id': 14,
                'slug': 'Copa-Libertadores',
                'seasons': {
                    '2024', '2023', '2022', '2021', '2020', '2019', '2018'
                }
            },
            'Liga MX': {
                'id': 31,
                'slug': 'Liga-MX',
                'seasons': {
                    '2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019'
                }
            }
        },
        'Sofascore': { #https://github.com/oseymour/ScraperFC/ some of the leagues ids were taken from here
            "Argentina Liga Profesional": {
                "id": 155,
                "seasons": {
                    "08/09": 1636, "09/10": 2323, "10/11": 2887, "11/12": 3613, "12/13": 5103,
                    "13/14": 6455, "2014": 8338, "2015": 9651, "2016": 11237, "16/17": 12117,
                    "17/18": 13950, "18/19": 18113, "19/20": 24239, "2021": 37231, "2022": 41884,
                    "2023": 47647, "2024": 57478
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
                    "2023": 48982,
                    "2024": 58766
                },
            },
            "Bolivia Division Profesional": {
                "id": 16736,
                "seasons": {
                    "2023": 48353, "2024": 58156
                },
            },
            "Chile Primera Division": {
                "id": 11653,
                "seasons": {
                    "2023": 48017, "2024": 57883
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
                    "2023": 52847,
                    "2024": 63819
                },
            },
            "Ecuador LigaPro": {
                "id": 240,
                "seasons": {
                    "2022": 40503,
                    "2023": 48720,
                    "2024": 58043
                },
            },
            "Mexico LigaMX Apertura": {
                "id": 11621,
                "seasons": {
                    "2022": 42017,
                    "2023": 52052,
                    "2024": 61419
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
                    "2023": 48634, "2024": 58264
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
            "Euros": {
                "id": 1,
                "seasons": {
                    "2024": 56953, "2021": 26542, "2016": 11098, "2012": 4136, "2008": 1162,
                    "2004": 356, "2000": 358
                }
            },
            "Copa America": {
                "id": 133,
                "seasons": {
                    "2024": 57114, "2021": 26681, "2019": 22352, "2016": 11115
                }
            },
            "Premier League": {
                "id": 17,
                "seasons": {
                    "15/16": 10356,
                    "16/17": 11733, "17/18": 13380, "18/19": 17359,
                    "19/20": 23776, "20/21": 29415, "21/22": 37036, 
                    "22/23": 41886, "23/24": 52186, "24/25": 61627
                },
            },
            "La Liga": {
                "id": 8,
                "seasons": {
                    "15/16": 10495,
                    "16/17": 11906, "17/18": 13662, "18/19": 18020,
                    "19/20": 24127, "20/21": 32501, "21/22": 37223, 
                    "22/23": 42409, "23/24": 52376, "24/25": 61643
                },
            },
            "Bundesliga": {
                "id": 35,
                "seasons": {
                    "15/16": 10419,
                    "16/17": 11818, "17/18": 13477, "18/19": 17597, 
                    "19/20": 23538, "20/21": 28210, "21/22": 37166, 
                    "22/23": 42268, "23/24": 52608, "24/25": 63516
                },
            },
            "Serie A": {
                "id": 23,
                "seasons": {
                    "15/16": 10596, "16/17": 11966, 
                    "17/18": 13768, "18/19": 17932, "19/20": 24644, 
                    "20/21": 32523, "21/22": 37475, "22/23": 42415, 
                    "23/24": 52760, "24/25": 63515
                },
            },
            "Ligue 1": {
                "id": 34,
                "seasons": {
                    "15/16": 10373, "16/17": 11648, 
                    "17/18": 13384, "18/19": 17279, "19/20": 23872, 
                    "20/21": 28222, "21/22": 37167, "22/23": 42273, 
                    "23/24": 52571, "24/25": 61736
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
            "MLS": {
                "id": 242,
                "seasons": {
                    "2021": 35964, "2022": 40071, "2023": 47955, "2024": 57317,
                }
            },
            "Saudi Pro League": {
                "id": 955,
                "seasons": {
                    "20/21": 34459, "21/22": 37597, "22/23": 44908, "23/24": 53241, "24/25": 63998
                }
            },
            "J1 League": {
                "id": 196,
                "seasons": {
                    "2021": 35273, "2022": 40230, "2023": 48055, "2024": 57353,
                }
            },
            "NSWL": {
                "id": 1690,
                "seasons": {
                    "2021": 36480, "2022": 40863, "2023": 48864, "2024": 58145,
                }
            },
            "USL Championship": {
                "id": 13363,
                "seasons": {
                    "2021": 36157, "2022": 40364, "2023": 48258, "2024": 57319,
                }
            },
            "La Liga 2": {
                "id": 54,
                "seasons": {
                    "20/21": 32502, "21/22": 37225, "22/23": 42410, "23/24": 52563, "24/25": 62048
                }
            }
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
            },
            'Copa America': {
                'id': 595,
                'seasons': None
            },
            'Euros': {
                'id': 6316,
                'seasons': None
            }
        },
        'Fotmob': {
            'Premier League': {
                'id': 47,
                'seasons': {
                    '2024/2025': 23685, '2023/2024': 20720, '2022/2023': 17664, '2021/2022': 16390, '2020/2021': 15382  
                }
            },
            'Bundesliga': {
                'id': 54,
                'seasons': {
                    '2024/2025': 23794, '2023/2024': 20946, '2022/2023': 17801, '2021/2022': 16494, '2020/2021': 15481  
                }
            },
            'La Liga': {
                'id': 87,
                'seasons': {
                    '2024/2025': 23686, '2023/2024': 21053, '2022/2023': 17852, '2021/2022': 16520, '2020/2021': 15585
                }
            },
            'Serie A': {
                'id': 55,
                'seasons': {
                    '2024/2025': 23819, '2023/2024': 20956, '2022/2023': 17866, '2021/2022': 16621, '2020/2021': 15604
                }
            },
            'Ligue 1': {
                'id': 53,
                'seasons': {
                    '2024/2025': 23724, '2023/2024': 20868, '2022/2023': 17810, '2021/2022': 16499, '2020/2021': 15293
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
                    '2024': 22635, '2023': 19058, '2022': 17301, '2021/2022': 16057, '2020/2021': 15756
                }
            },
            'Primera Division Colombia': {
                'id': 274,
                'seasons': {
                    '2024-Clausura': "22613-Clausura",'2024-Apertura': "22613-Apertura", '2023-Clausura': "18664-Clausura", '2023-Apertura': "18664-Clausura",
                    '2022-Clausura': "17283-Clausura", "2022-Apertura": "17283-Apertura"
                }
            },
            'Primera Division Chile': {
                'id': 273,
                'seasons': {
                    '2024': 22749, '2023': 18600, '2022': 17370, "2021": 16185
                }
            },
            'Brasileirao': {
                'id': 268,
                'seasons': {
                    '2024': 22978, '2023': 18982, '2022': 17409, "2021": 16201
                }
            },
            'Primera Division Peru': {
                'id': 131,
                'seasons': {
                    '2024': 22698, '2023': 18625, '2022': 17172, "2021": 16143
                }
            },
            'Copa America': {
                'id': 44,
                'seasons': {
                    '2024': 22518, '2021': 15148, '2019': 13572
                }
            },
            'Euros': {
                'id': 50,
                'seasons': {
                    '2024': 18307, '2021': 12715, '2016': 8479
                }
            }
        },
        "Transfermarkt": {
            "Primera Division Argentina": {
                "slug": "superliga",
                "id": "AR1N",
                "seasons": None
            },
            "Argentina Copa de la Liga": {
                "slug": "copa-de-la-liga-profesional-de-futbol",
                "id": "CDLP",
                "seasons": None
            },
            "Primera Division Chile": {
                "slug": "primera-division-de-chile",
                "id": "CLPD",
                "seasons": None
            },
            "Brasileirao": {
                "slug": "campeonato-brasileiro-serie-a",
                "id": "BRA1",
                "seasons": None
            },
        },
        "DataFactory": {
            "Primera Division Argentina": {
                "slug": "primeraa",
                "seasons": None
            },
            "Copa de la Liga Argetina": {
                "slug": "copalpf",
                "seasons": None
            },
            "Bundesliga": {
                "slug": "alemania",
                "seasons": None
            },
            "Primera Division Chile": {
                "slug": "chile",
                "seasons": None
            },
            "Copa Libertadores": {
                "slug": "libertadores",
                "seasons": None
            },
            "Copa Sudamericana": {
                "slug": "sudamericana",
                "seasons": None
            },
            "Eliminatorias Sudamericanas": {
                "slug": "copalpf",
                "seasons": None
            },
            "La Liga": {
                "slug": "espana",
                "seasons": None
            },
            "Ligue 1": {
                "slug": "francia",
                "seasons": None
            },
            "Premier League": {
                "slug": "premierleague",
                "seasons": None
            },
            "Serie A": {
                "slug": "italia",
                "seasons": None
            },
            "Mundial": {
                "slug": "mundial",
                "seasons": None
            },
            "Primera Division Paraguay": {
                "slug": "paraguay",
                "seasons": None
            },
            "Champions League": {
                "slug": "champions",
                "seasons": None
            },
            "Champions League": {
                "slug": "champions",
                "seasons": None
            },
            "Primera Division Uruguay": {
                "slug": "uruguay",
                "seasons": None
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
    if page not in ['Transfermarkt', '365Scores', 'DataFactory']:
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

def semicircle(r, h, k):
    x0 = h - r  # determine x start
    x1 = h + r  # determine x finish
    x = np.linspace(x0, x1, 10000)  # many points to solve for y

    # use numpy for array solving of the semicircle equation
    y = k - np.sqrt(r**2 - (x - h)**2)  
    return x, y

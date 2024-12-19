import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from .config import headers as request_headers
from .functions import get_possible_leagues
from .exceptions import PlayerDoesntHaveInfo


class Transfermarkt:
    
    def __init__(self):
        self.page = "Transfermarkt"
    
    def transfermarkt_request_to_soup(self, url):
        response = requests.get(url, headers=request_headers)
        time.sleep(3)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    
    def get_items_table(self, soup):
        table = soup.find('table', {'class': 'items'})
        return table
    
    def parse_name(self, name):
        parsed_name = '-'.join(name.lower().split())
        return parsed_name

    def get_head_coach_historical_data(self, name, headcoach_id):
        modified_name = self.parse_name(name)
        url = f'https://www.transfermarkt.com.ar/{modified_name}/stationen/trainer/{headcoach_id}/plus/1'
        soup = self.transfermarkt_request_to_soup(url)
        table = self.get_items_table(soup)
        
        try:
            headers = [header.get_text() for header in table.find_all('th')]
        except AttributeError:
            raise(PlayerDoesntHaveInfo(url))

        rows = []
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all('td')
            cells = [cell.get_text(strip=True) if cell.find('img') is None else cell.find('img')['src'] for cell in cells]
            rows.append(cells)
            
        df = pd.DataFrame(rows, columns=headers).drop(columns=['wappen'])
        return df
    
    def get_transfermarkt_age(self, date):
        age = date.split(' ')[0].split('/')[-1]
        try:
            age = int(age)
        except ValueError:
            age = None
        return age
    
    def get_season_id(self, season):
        if len(season.split('/')) > 1:
            season_id = season.split('/')[0]
        else:
            season_id = int(season) - 1
        return season_id
    
    def scrape_players_for_teams(self, team_name, team_id, season):
        season_id = self.get_season_id(season)
        team_name_url = self.parse_name(team_name)
        url = f'https://www.transfermarkt.com.ar/{team_name_url}/kader/verein/{team_id}/plus/1/galerie/0?saison_id={season_id}'
        soup = self.transfermarkt_request_to_soup(url)
        table = self.get_items_table(soup)

        # Encontrar los encabezados (th)
        headers = table.find('thead').find_all('th')

        # Obtener los nombres de las columnas
        column_names = [header.get_text(strip=True) for header in headers]
        column_names.append('Pais')
        column_names.append('Seg nacionalidad')
        print(column_names)
        del column_names[3]

        # Encontrar las filas (tr) en el cuerpo de la tabla (tbody)
        rows = table.find('tbody').find_all('tr')

        filas = []
        # Iterar sobre las filas y extraer los datos de las celdas (td)
        for row in rows:
            row_data = []
            cells = row.find_all('td')
            paises = row.find_all('img', {'class': 'flaggenrahmen'})
            lista_paises = [pais['title'] for pais in paises if not []]
            for cell in cells:
                row_data.append(cell.get_text(strip=True))
            for pais in lista_paises:
                row_data.append(pais)
            fila_final = [row_data[i] for i in range(len(row_data)) if i not in [2, 6, 10]]
            filas.append(fila_final)
            # Agregar la fila al DataFrame

        filas_df = []
        for elemento in range(0, len(filas), 3):
            del filas[elemento][1]
            filas_df.append(filas[elemento])
        try:
            df = pd.DataFrame(filas_df, columns=column_names)
        except ValueError:
            del column_names[-1]
            df = pd.DataFrame(filas_df, columns=column_names)
            
        df = df.rename(columns={
            'Altura': 'Fecha de nac.',
            'F. Nacim./Edad': 'Posicion',
            'Pie': 'Altura',
            'Fichado': 'Pie',
            'antes': 'Fichado'
        })
        df['equipo'] = team_name_url
        if "Club actual" in list(df.columns):
            df = df.drop(columns=['Fecha de nac.']).rename(columns={'Club actual': 'Fecha de nac.'})
        df['Año nac.'] = df['Fecha de nac.'].apply(self.get_transfermarkt_age)
        return df
    
    def get_league_teams_valuations(self, league, season):
        season_id = self.get_season_id(season)
        slug_league = get_possible_leagues(league, None, self.page)["Transfermarkt"][league]['slug']
        id_league = get_possible_leagues(league, None, self.page)["Transfermarkt"][league]['id']
        league_url = f'https://www.transfermarkt.com/{slug_league}/startseite/wettbewerb/{id_league}'
        league_url = league_url + '/plus/?saison_id=' + f'{season_id}'

        soup = self.transfermarkt_request_to_soup(league_url)
        div = soup.findAll('div', {'class':'responsive-table'})[0]
        data_table = div.find('table')

        dt_body = data_table.find('tbody')
        data = []
        rows = dt_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append(cols)

        df_total = pd.DataFrame(data, columns=[0, 'Club', 'Squad size', 'Mean age', 'Foreigners', 'Mean market value', 'Total market value (M€)']).drop(columns=0)
        return df_total

    def get_player_transfer_history(self, player_id):
        response = requests.get(f'https://www.transfermarkt.com.ar/ceapi/transferHistory/list/{player_id}', headers=request_headers)
        time.sleep(3)
        transfer_df = pd.DataFrame(response.json()['transfers'])
        df_from = transfer_df['from'].apply(pd.Series).rename(columns={'clubName': 'club_from'})['club_from']
        df_to = transfer_df['to'].apply(pd.Series).rename(columns={'clubName': 'club_to'})['club_to']
        final_df = pd.concat([transfer_df, df_from, df_to], axis=1)
        return final_df
    
    def get_player_positions_played(self, player_name, player_id):
        player_name = self.parse_name(player_name)
        url = f'https://www.transfermarkt.co.uk/{player_name}/leistungsdaten/spieler/{player_id}/plus/0?saison=ges'
        soup = self.transfermarkt_request_to_soup(url)
        try:
            table = soup.find_all('table')[2]
        except IndexError:
            raise(PlayerDoesntHaveInfo(url))
        headers = ['Position', 'Matches', 'Goals', 'Assists']

        rows = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            cols = [col.get_text(strip=True) for col in cols]
            rows.append(cols)

        df = pd.DataFrame(rows, columns=headers)
        return df
    
    def get_last_page(self, url):
        data = requests.get(f'{url}/1', headers=request_headers)
        soup = BeautifulSoup(data.content, 'html.parser')
        pager_div = soup.find('div', class_='pager')
        try:
            last_page_li = pager_div.find('li', class_='tm-pagination__list-item tm-pagination__list-item--icon-last-page')
        except AttributeError:
            raise(PlayerDoesntHaveInfo(url))
        if last_page_li:
            last_page_link = last_page_li.find('a', class_='tm-pagination__link')
            if last_page_link:
                last_page = last_page_link['href'].split('/')[-1]
        return int(last_page)
    
    def get_keepers_penalty_data(self, player_name, player_id):
        player_name = self.parse_name(player_name)
        base_url = f'https://www.transfermarkt.com.ar/{player_name}/elfmeterstatistik/spieler/{player_id}/saison_id//wettbewerb_id//plus/1/page'
        last_page = self.get_last_page(base_url)
        columns = ['Seasons', 'Competition', 'Date', 'Final Result', 'Minute', 'Result after the penalty', 'Penalty Kicker']
        df_saved = pd.DataFrame(columns=columns)
        df_conceded = pd.DataFrame(columns=columns)    
        for page in range(1,last_page+1):
            soup = self.transfermarkt_request_to_soup(f'{base_url}/{page}')
            saved = soup.find_all('table', {'class': 'items'})[0]
            conceded = soup.find_all('table', {'class': 'items'})[1]
            for idx, dataframe in enumerate([saved, conceded]):
                data = []
                rows = dataframe.find_all('tr')

                for row in rows[1:]:
                    cols = row.find_all(['td', 'th'])
                    cols = [ele.text.strip() for ele in cols]
                    data.append([ele for ele in cols if ele])

                df = pd.DataFrame(data, columns=columns)
                if idx == 0:
                    df_saved = pd.concat([df_saved, df])
                else:
                    df_conceded = pd.concat([df_conceded, df])
        df_saved = df_saved.drop_duplicates().reset_index(drop=True)
        df_conceded = df_conceded.drop_duplicates().reset_index(drop=True)
        return df_saved, df_conceded
    
    def get_player_played_data(self, player_name, played_id):
        player_name = self.parse_name(player_name)
        url = f'https://www.transfermarkt.com.ar/{player_name}/leistungsdatendetails/spieler/{played_id}/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'
        soup = self.transfermarkt_request_to_soup(url)
        
        table = soup.find_all('table')[1]

        rows = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            row_data = []
            for col in cols:
                if col.find('a'):
                    if 'zentriert' in col.get('class', []) and "hauptlink" not in col.get('class', []):
                        row_data.append(col.get_text(strip=True))
                    else:
                        title = col.find('a').get('title')
                        if title:
                            row_data.append(title)
                        else:
                            row_data.append(col.get_text(strip=True))
                else:
                    row_data.append(col.get_text(strip=True))
            rows.append(row_data)

        rows[0][0], rows[0][1] = 'Total', ''
        total = rows.pop(0)
        rows.append(total)
        try:
            headers = ['Season', '','Competition', 'Club', 'Was in squad', 'Played', 'PPP','Goals', 'Assists', 'Own goals', 'Subbed In', 'Subbed out', 'Yellow Cards', 'Double yellow', 'Red Cards', 'Penalty Kicks', 'Minutes per goal', 'Minutes played']
            df = pd.DataFrame(rows, columns=headers)
        except ValueError:
            headers = ['Season', '','Competition', 'Club', 'Was in squad', 'Played', 'PPP','Goals', 'Own goals', 'Subbed In', 'Subbed out', 'Yellow Cards', 'Double yellow', 'Red Cards', 'Goals Conceded', 'Clean Sheets','Minutes played']
            df = pd.DataFrame(rows, columns=headers)    
        return df
    
    def get_player_market_value(self, player_id):
        response = requests.get(f'https://www.transfermarkt.com.ar/ceapi/marketValueDevelopment/graph/{player_id}', headers=request_headers)
        time.sleep(3)
        values = pd.DataFrame(response.json()['list'])
        values['wappen'] = values['wappen'].apply(lambda x: np.NAN if x == '' else x).ffill()
        player_name = response.json()['details_url'].split('/')[1].replace('-', ' ').title()
        values['player'] = player_name
        return values
        
        
    

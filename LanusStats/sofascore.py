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
    print('Not implemented yet')
    
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
    # Obtén el contenido de la página
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Cierra el webdriver
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
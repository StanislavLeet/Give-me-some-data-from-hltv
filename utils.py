import time
import json
import requests
import pandas as pd
from lxml import html
from tqdm.auto import tqdm



def GimeMeMatchLinks(url):
    """
    Функция возвращающая все ссылки на странице
    url - url адресс страницы
    """
    r = requests.get(url)
    page = r.text
    tree = html.fromstring(page)
    return [k for k in tree.xpath('//a/@href') if 'matches/' in k]


def GiveMeMatches(url):
    """
    Функция возвращает адресса страниц матчей встречи 
    url - адресс встречи
    """
    mapstat = []
    k = 0
    while len(mapstat) == 0:
        mapstat = [k for k in GimeMeMatchLinks(url) if 'mapstatsid' in k]
        time.sleep(10)
        k += 1
        if k == 10:
            return []
        
    return mapstat

def ParseStandardBoxTeam1Side(half_history):
    """
    Функция получения стороны первой команды из round history box
    fhalf_history - набор иконок первой стороны
    """

    for roundCS in half_history:
        if 'ct_win.svg' in roundCS or 'stopwatch.svg' in roundCS:
            return True
        if 'bomb_exploded.svg' in roundCS or 't_win' in roundCS:
            return False


def ParseStandardBox(StandardBox):
    """
    Функция получения данных из round history box
    StandardBox - round history box
    """
    # 1. Нам достаточно только результатов одной из команд 
    first_team_history = StandardBox.split('round-history-team-row')[1]
    
    # 2. Получением набора иконок
    fhalf_history = first_team_history.split('round-history-half')[1].split('round-history-outcome')
    shalf_history = first_team_history.split('round-history-half')[2].split('round-history-outcome')
    
    
    # 3. Итерируемся по картинками
    
    T_score = 0
    CT_score = 0
    side_score = []
    
    
    for roundCS in fhalf_history:
        if CT_score + T_score < 15:
            if 'emptyHistory.svg' in roundCS:
                side_score += ['S']
                T_score += 1
            else:
                CT_score += 1
                side_score += ['F']
    
    for roundCS in shalf_history:
        if CT_score <= 15 and T_score <= 15:
            if 'emptyHistory.svg' in roundCS:
                T_score += 1
                side_score += ['S(R)']
            else:
                CT_score += 1
                side_score += ['F(R)']
    
    return CT_score, T_score, ParseStandardBoxTeam1Side(fhalf_history), side_score


def GiveMeMap(page):
    """
    Функция возвращающая карту встречи
    page - текст страницы
    """
    
    maps = {'Vertigo' : 0, 'Mirage' : 0, 'Train' : 0, 'Inferno' : 0, 'Overpass' : 0, 'Nuke' : 0,  'Dust2': 0}
    
    for mapid in maps.keys():
        maps[mapid] = page.count(mapid)
    
    max_el = max([maps[key] for key in maps.keys()])
    
    for key in maps.keys():
        if maps[key] == max_el:
            return key


def GivePage(url):
    """
    Получение текста страницы
    url - url страницы
    """
    
    try:
        r = requests.get(url)
        page = r.text
    except:
        page = ''
       
    k = 0
    while len(page) < 5000:
        
        try:
            r = requests.get(url)
            page = r.text
        except:
            page = ''
            
            
        time.sleep(15)
        k += 1
        if k > 10:
            return ''
    
    return page


def GiveInfoFromMatch(url, stat):
    """
    Получение информации из страницы
    url - url матча
    """
    page = GivePage(url)
    
    if page == '':
        return dict()
            
    page_with_score = page.split('standard-box round-history-con')[1]
    T1, T2, firstCT, side_score = ParseStandardBox(page_with_score)
        
        
    inf_dict = dict()
    inf_dict['Team 1'] = stat.split('/')[-1].split('vs')[0][:-1]
    inf_dict['Team 2'] = stat.split('/')[-1].split('vs')[1][1:]
    inf_dict['Team 1 score'] = T1
    inf_dict['Team 2 score'] = T2
    inf_dict['First CT'] = firstCT
    inf_dict['map'] = GiveMeMap(page)
    inf_dict['side dynamic'] = side_score
        
    return inf_dict
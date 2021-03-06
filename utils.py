import time
import json
import requests
import pandas as pd
from lxml import html
from tqdm.auto import tqdm



def get_match_links(url, driver):
    """Функция возвращающая все ссылки на странице
    url - url адресс страницы"""


    driver.get(url)
    page = driver.page_source
    tree = html.fromstring(page)
    return [k for k in tree.xpath('//a/@href') if 'matches/' in k]


def get_matches(url, driver):
    """Функция возвращает адресса страниц матчей встречи 
    url - адресс встречи
    """

    mapstat = []
    k = 0
    while len(mapstat) == 0:
        mapstat = [k for k in get_match_links(url, driver) if 'mapstatsid' in k]
        time.sleep(10)
        k += 1
        if k == 10:
            return []
        
    return mapstat

def parse_StandardBox_team1_Side(half_history):
    """Функция получения стороны первой команды из round history box
    fhalf_history - набор иконок первой стороны
    """

    for roundCS in half_history:
        if 'ct_win.svg' in roundCS or 'stopwatch.svg' in roundCS:
            return True
        if 'bomb_exploded.svg' in roundCS or 't_win' in roundCS:
            return False


def parse_StandardBox(StandardBox):
    """Функция получения данных из round history box
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
    
    return CT_score, T_score, parse_StandardBox_team1_Side(fhalf_history), side_score


def get_map(page):
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


def get_page(url, driver):
    """
    Получение текста страницы
    url - url страницы
    """
    
    try:
        driver.get(url)
        page = driver.page_source
    except:
        page = ''
       
    k = 0
    while len(page) < 5000:
        
        try:
            driver.get(url)
            page = driver.page_source
        except:
            page = ''
            
            
        time.sleep(15)
        k += 1
        if k > 10:
            return ''
    
    return page


def get_info_from_match(url, stat, driver):
    """Получение информации из страницы матча:
    наименование команд, счет игры, карта, 
    последовательность выигранных раундов
    url - url матча
    stat - ссылка с главной страницы
    """
    page = get_page(url, driver)
    
    if page == '':
        return dict()
            
    page_with_score = page.split('standard-box round-history-con')[1]
    T1, T2, firstCT, side_score = parse_StandardBox(page_with_score)
        
        
    inf_dict = dict()
    inf_dict['Team 1'] = stat.split('/')[-1].split('vs')[0][:-1]
    inf_dict['Team 2'] = stat.split('/')[-1].split('vs')[1][1:]
    inf_dict['Team 1 score'] = T1
    inf_dict['Team 2 score'] = T2
    inf_dict['First CT'] = firstCT
    inf_dict['map'] = get_map(page)
    inf_dict['side dynamic'] = side_score
        
    return inf_dict

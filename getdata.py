import time
import json
import requests
import pandas as pd
from lxml import html
from tqdm.auto import tqdm
import utils
from selenium import webdriver


DRIVER_PATH = '/usr/lib/chromium-browser/chromedriver'
option = webdriver.ChromeOptions()
option.add_argument("--incognito")
option.add_argument('--headless')
option.add_argument('--no-sandbox')
option.add_argument('--disable-dev-shm-usage', chrome_options = option)
driver = webdriver.Chrome(executable_path=DRIVER_PATH)


links_to_matches = []
for i in tqdm(range(164)):
    url = 'https://www.hltv.org/results?offset={}&startDate=2018-04-05&endDate=2020-08-21&matchType=Online'.format(i*100)
    links_to_matches += utils.get_match_links(url, driver)


data = dict()
count = 0
for link in tqdm(links_to_matches):
    url = 'https://www.hltv.org{}'.format(link)
    mapstat = utils.get_matches(url, driver)
    
    if len(mapstat) == 0:
        continue
        
    for stat in mapstat:
        url = 'https://www.hltv.org{}'.format(stat)
        try:
            OneMatch = utils.get_info_from_match(url, stat, driver)
            match_id = stat.split('/')[-2]

            if len(OneMatch.keys()) > 1:
                data[match_id] = dict()
                data[match_id]['url'] = url
                for key in OneMatch:
                    data[match_id][key] = OneMatch[key]
        except:
            pass
            
    if count % 200 == 0 and count > 0:
        with open('CSjson.json', 'w') as f:
            f.write(json.dumps(data))

    count += 1

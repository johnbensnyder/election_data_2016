# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 21:57:09 2016

@author: johnsnyder
"""

import time
from bs4 import BeautifulSoup
import os
import requests
import pandas as pd


states_list = ['alaska','arkansas','arizona','california','colorado','connecticut', \
                'delaware','district-of-columbia','florida','georgia','hawaii','idaho', \
                'illinois','indiana','iowa','kansas','kentucky','louisiana','maine', \
                'maryland','massachusetts','michigan','minnesota','mississippi','missouri', \]

url = 'http://www.politico.com/2016-election/results/map/president/kansas/'
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"

headers = { 'User-Agent' : user_agent }
response = requests.get(url, headers=headers)
html = response.text.encode('utf-8')
soup = BeautifulSoup(html,"lxml")


prez_results = soup.findAll('article',{'class':'results-group'})

for i in prez_results:
    if i.find('div',{'class':'title'}).string:
        print(i.find('div',{'class':'title'}).string.split(' ')[0].upper())
    
prez_results[1].find('table',{'class':'results-table'})
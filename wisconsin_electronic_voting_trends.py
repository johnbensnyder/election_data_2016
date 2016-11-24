# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 22:14:57 2016

@author: johnsnyder
"""

import pandas as pd

voting_machines_wisconsin = pd.read_excel('http://elections.wi.gov/sites/default/files/page/179/voting_equipment_by_municipality_09_2016_xlsx_78114.xlsx')

voting_machines_wisconsin['dominion'] = [1 if 'Dominion' in i else 0 for i in voting_machines_wisconsin['Accessible Voting Equipment Vendor/Dealer-Model']]

voting_machines_wisconsin['county'] = [i.split()[0] for i in voting_machines_wisconsin['County']]

dominion_machines = voting_machines_wisconsin[['county','dominion']]

dominion_machines = dominion_machines.groupby('county').max().reset_index()

wisconsin_2012 = pd.read_excel('http://elections.wi.gov/sites/default/files/County%20by%20County_11.6.12.xls',sheetname = 1, skiprows = 6, headers = False)

column_names = list(wisconsin_2012.columns)

column_names[0] = 'county'

column_names[2] = 'total_2012'

column_names[3] = 'gop_2012'

column_names[4] = 'dem_2012'

wisconsin_2012.columns = column_names

wisconsin_2012 = wisconsin_2012[['county','total_2012','gop_2012','dem_2012']]

wisconsin_2012['dem_percent'] = wisconsin_2012['dem_2012']/wisconsin_2012['total_2012']*100

wisconsin_2012['county'] = [i.strip() for i in wisconsin_2012['county']]


import time
from bs4 import BeautifulSoup
import os
import requests
import pandas as pd


url = 'http://wisconsinvote.org/election-results-by-county'
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"

headers = { 'User-Agent' : user_agent }
response = requests.get(url, headers=headers)
html = response.text.encode('utf-8')
soup = BeautifulSoup(html,"lxml")

county_names = [i.string.split(' ')[1] for i in soup.findAll('div',{'class':'view-grouping-header'})]
all_data = soup.findAll('div',{'class':'view-grouping-content'})

'''
election_data = soup.findAll('table',{'class':'views-table cols-3'})

prez_data = []
for i in election_data:
    if i.find('a',{'href':'/results/president-general'}):
        prez_data.append(i)
'''
#all_data[0].findAll('table',{'class':'views-table cols-3'})[1]

#all_data[0].findAll('td',{'class':'views-field views-field-field-candidates'})[0].find('a',href=True).string

prez_results = all_data[2].findAll('table',{'class':'views-table cols-3'})

prez_results[0]

def county_data_grabber(a_county, a_name):
    prez_results = a_county.findAll('table',{'class':'views-table cols-3'})[1]
    names = [i.find('a',href=True).string.strip() for i in prez_results.findAll('td',{'class':'views-field views-field-field-candidates'})]
    votes = [int(i.string.strip().replace(',','')) for i in prez_results.findAll('td',{'class':'views-field views-field-field-votes-received'})]
    percent = [float(i.string.strip().replace('%','')) for i in prez_results.findAll('td',{'class':'views-field views-field-field-vote-percentage'})]    
    return pd.DataFrame({'county':a_name.upper(),'names':names,'votes':votes,'percent':percent})
    
county_data_grabber(all_data[10],county_names[10])

def counties_df_builder(county_data,county_names):
    all_data = pd.DataFrame({'county':[],'names':[],'votes':[],'percent':[]})
    for i,j in zip(county_data,county_names):
        try:
            all_data = all_data.append(county_data_grabber(i,j))
        except:
            continue
    return all_data
    
wisconsin_2016 = counties_df_builder(all_data,county_names)

big_ones = ['Hillary Clinton','Donald J. Trump']

wisconsin_2016 = wisconsin_2016[wisconsin_2016['names'].isin(big_ones)]

wisconsin_2016 = wisconsin_2016.pivot(index = 'county', columns = 'names', values = 'percent').reset_index()

wisconsin_2016.columns = ['county', 'gop_2016', 'dem_2016']

dem_data = wisconsin_2016[['county','dem_2016']].merge(wisconsin_2012[['county','dem_percent','total_2012']], \
        left_on = 'county', right_on = 'county')
        
dem_data['change'] = dem_data['dem_2016'] - dem_data['dem_percent']

dem_data = dem_data.merge(dominion_machines,left_on='county', right_on='county')

dem_data['intercept'] = 1






import statsmodels.api as sm

model = sm.OLS(dem_data['change'], dem_data[['dominion','total_2012','intercept']])

results = model.fit()

print(results.summary())

import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from main import create_server_connection
from main import ignite
from main import execute_query

def mainactivity(connection):
    ignite(connection,"storage")
    url = 'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=21&search=Search&searchType=oha&currentSortSettings='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option", attrs={'class': 'formOptionList'})
    names = [item.string for item in results][:-8]
    codes = [item["value"] for item in results][:-8]
    sql = f'CREATE TABLE IF NOT EXISTS MainActivityType(`kwdikos` tinyint PRIMARY KEY,`onoma` varchar(100));'
    execute_query(connection,sql)
    mainactivity=[f"({codes[i]},\"{names[i]}\")" for i in range(len(codes))]
    valu=""
    for item in mainactivity:
        valu += item+",\n"
    sql = f'INSERT INTO MainActivityType' \
          f'(kwdikos,onoma)' \
          f'VALUES' \
          f'{valu[:-2]}'
    execute_query(connection,sql)
    print("done from mainactivity")

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    countries = ['AT','BE','BG','HR','CY','CZ','DK','EE','EU','FI','FR','DE','GR','HU','IS','IE','IT','LV','LI','LT','LU','MT','NL',
                 'XI','NO','PL','PT','RO','SK','SI','ES','SE']
    country = countries[4]
    pageno = 0
    holders = []
    accounts = []
    holdercounter = 1
    accountcounter = 1
    connection=create_server_connection('localhost','root','')
    mainactivity(connection)
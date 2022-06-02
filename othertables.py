import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from utilityfuncs import *

def countriestable(connection):
    url='https://www.iban.com/country-codes'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("td")
    abb2 = [item.string for item in results if (results.index(item)-1)%4==0]
    abb3 = [item.string for item in results if (results.index(item) -2) % 4 == 0]
    ignite(connection,"eu_ets")
    sql='select * from countries'
    cursor = connection.cursor()
    cursor.execute(sql)
    oldcountries = cursor.fetchall()
    oldabbr2=[item[3] for item in oldcountries]
    diff=[item for item in oldabbr2 if item not in abb2]
    revdiff=[item for item in abb2 if item not in oldabbr2]
    print("these exist in the old but non in the new","\n",diff,"\n","the reverse",revdiff)
    newcountries=[]
    for abbr in abb2:
        if abbr=="GB":
            print("weinher")
            continue
        if abbr in oldabbr2:
            tem=oldabbr2.index(abbr)
            temp=oldcountries[tem]
            obj=(temp[0],temp[1],temp[2],temp[3],abb3[abb2.index(abbr)],temp[5],temp[6],temp[7],temp[8])
            newcountries.append(obj)
    print("new",newcountries)
    url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option",attrs={'class':'formOptionListMedium'})
    clima=[item['value'] for item in results if len(item['value'])==2]
    print("discrepancies",[item for item in clima if item not in abb2])
    print(len(newcountries))
    ni = ('XI','Northern Ireland','Βόρεια Ιρλανδία','XI',None, 1,1,0,'Europe')
    eu = ('EU','European Union','Ευρωπαϊκή Ένωση','EU',None,None,None,None,"Europe")
    un = ('UN','United Nations','Ηνωμένα Έθνη','UN',None,None,None,None,None)
    uk = ('UK','United Kingdom','Ηνωμένο Βασίλειο','GB','GBR',1,0,1,'Europe')
    gr = ('EL','Greece','Ελλάδα','GR','GRC',1,1,1,'Europe')
    newcountries=[item for item in newcountries if item[1]!="Greece"]
    final=sorted(newcountries+[eu]+[un]+[ni]+[uk]+[gr],key=lambda x:x[0])
    final=[oldcountries[0]]+final
    print(final)
    ignite(connection,"EUTL")
    for country in final:
        print(country)
        temp=tuple([term if term != None else "Null" for term in country])
        print(temp)
        strtoadd="("
        for elem in temp:
            if isinstance(elem,str) and elem!="Null":
                strtoadd+=f"\"{elem}\","
            else:
                strtoadd+=f"{elem},"
        #strtoadd=f"(\"{temp[0]}\",\"{temp[1]}\",\"{temp[2]}\",\"{temp[3]}\",\"{temp[4]}\",{temp[5]},{temp[6]},{temp[7]},\"{temp[8]}\")"
        strtoadd=strtoadd[:-1]+")"
        print(strtoadd)
        addcountry(connection,strtoadd,"countries","whatevs")
    addcountry(connection,'(\'AV\',\'Avalon\',\'Άβαλον\',\'AV\',\'AVA\',0,0,0,\'Europe\')',"countries","whatevs")


def mainactivity(connection):
    ignite(connection,"EUTL")
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

def trantypes(connection):
    ignite(connection,"EU_ETS")
    query = f'select * from EUTL_TransactionTypes;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    inserts=[]
    for resul in result:
        temp=[]
        for i in resul:
            if i is None:
                temp.append("NULL")
            else: temp.append(i)
        inserts.append(temp)
    print(inserts)
    ignite(connection,"EUTL")
    for insert in inserts:
        strin="\""+insert[0]+"\","+str(insert[1])+","+str(insert[2])+","+insert[3]
        sql = f"""INSERT INTO TransactionTypes (code,transferringType,acquiringType,sholio)
                    VALUES ({strin})"""
        execute_query(connection,sql)

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
    ignite(connection,'EUTL')
    #trantypes(connection)
    #mainactivity(connection)
    countriestable(connection)
    trantypes(connection)
    mainactivity(connection)
    #sql = """
    #insert into Holders(rawCode, holderName,country)
    #values (28000,'Deez Nuts','GR');"""
    #execute_query(connection, sql)
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

def indaccount(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results=soup.find_all("span",attrs={'class':'classictext'})
    temp=[item.string for item in results]
    #temp=[item.string[7:-6] for item in results]
    temp2=[]
    for item in temp:
        item=item.replace('\n', '')
        item=item.replace('\r', '')
        item=item.replace('\t', '')
        item=item.replace('\xa0', '')
        if item!="":temp2.append(item.rstrip())
        else: temp2.append("Null")
    missingboi=soup.find_all("span",attrs={'class':'resultlink'})
    if missingboi!=[]:
        try:
            temp2= temp2[:2]+[missingboi[0].string[7:-6]]+temp2[2:]
        except IndexError:
            temp2=temp2[:2]+[""]+temp2[2:]
    results= soup.find_all("font",attrs={'class':'bordertbheadfont'})
    name=results[0].getText()[31:]
    name=name.replace('\r','')
    name=name.replace('\n','')
    name=name.replace('\xa0','')
    name = name.replace('\t', '').rstrip()
    temp2[1]=abbrs[countries.index(temp2[1])]
    if temp2[6]=="Null":temp2[6]="1941-09-09 00:00:00.0"
    specs= (accountname,fullaccountname,acctype, accstatus,acccountry, accopen,accclose, relatedid)=(name,temp2[10],temp2[0],temp2[4],temp2[1],temp2[5],temp2[6],temp2[2])
    holderspecs = (holdername,coregno,type,legalentity,address1,address2,zipcode,city, country,tel1,tel2,email)=(temp2[3],temp2[7],temp2[8],temp2[10],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18])
    return holderspecs,specs

def accountresults(url):
    # url = 'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes=GR&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
    #                                     'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    # pages = temp[0]['value']

    # temp2 = soup.find_all("td", attrs={'class': 'bgtitlelist'})
    temp3 = soup.find_all("a", attrs={'class': 'listlink'})
    templinks = [startingurl + obj['href'][11:] for obj in temp3]
    #reallinks = [templinks[1 + i] for i in range(len(templinks) - 1) if i % 3 == 0]
    #print(templinks)
    return templinks

def controller(countriestoadd):
    accounts=[]
    holders=[]
    for country in countriestoadd:#countries[21:22]:
        try:
            pageno=0
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&searchType=account&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            #print(url)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                                 'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
            # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
            pages = temp[0]['value']
            print(country, pages)
            for pageno in range(int(pages)):
                #url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&searchType=account&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                holderlinks = accountresults(url)
                #with the links we want to crawl these pages and store the individual information
                for link in holderlinks:
                    result,instresult = indaccount(link)
                    holders.append(result)
                    accounts.append(instresult)
                    #print(result)
        except IndexError:
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
            holderlinks = accountresults(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result,instresult = indaccount(link)
                holders.append(result)
                accounts.append(instresult)
                # print(result)
    return (holders,accounts)

def accountaddition(row):
    (accountname,fullaccountname,acctype, accstatus,acccountry, accopen,accclose, relatedid) = row
    global accountcounter
    global connection
    query = 'select count(*) from accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    # result = int(execute_query(connection,query)[0][0])
    accountcounter = result + 1
    # wanted=[accountcounter]+[row[i] for i in [0,1,8,9,10,12,13,14,17]]
    wanted = [accountcounter] + [row[0], row[1],row[2], row[3], row[4], row[5], row[6],row[7]] +["Null"]
    acc=wanted
    final=f"{acc[0]},\"{acc[1]}\",\"{acc[2]}\",{acc[8]},\"{acc[3]}\",\"{acc[5]}\",\"{acc[6]}\",\"{acc[7]}\",\"{acc[4]}\",\"{acc[9]}\""
    accountcounter += 1
    addaccount(connection, final, "accounts")
    return wanted

def addaccount(connection,attributes,table):
    sql = f"""
         into {table}(rawCode,nickname, holderName, accountid,acctype, registry,firstyear, finalyear, status, mainactivity)
        values ({attributes})
        """
    execute_query(connection, sql)

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                 'LV', 'LI', 'LT', 'LU', 'MT', 'NL',
                 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
    country = countries[4]
    pageno = 0
    holdercounter = 1
    accountcounter = 1
    connection=create_server_connection('localhost','root','')
    ignite(connection,"storage")
    sql="select eu_abbr2L,name from countries;"
    cursor = connection.cursor()
    cursor.execute(sql)
    countryindex = cursor.fetchall()
    abbrs = [item[0] for item in countryindex]
    print(abbrs)
    countries = [item[1] for item in countryindex]
    countries[abbrs.index("EU")]="European Commission"
    triedandtrue=[]
    #for abb in abbrs:
    #    url=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={abb}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
    """response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                         'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")"""
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    """try:
        pages = temp[0]['value']
    except IndexError:
        pages=0"""
    couli=['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB','GR']
    print(len(couli))
    """url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option",attrs={'class':'formOptionListMedium'})
    clima=[item['value'] for item in results if len(item['value'])==2]"""
    holders,accounts=controller(['IS'])
    #print(len(accounts))
    #print(accounts[0])
    for account in accounts:
        accountaddition(account)
    #row="('20 - Centrale énergétique (Dupont de Nemours)', 'Account holder', 'Former Operator Holding Account', 'closed', 'Luxembourg', '2006-06-08 00:00:00.0', '2014-06-30 10:41:05.0', '')"

    #sent = re.sub(r'FC{1}', '', sent)
    #sent = re.sub(r'FC|', '', sent)

    #print(re.sub(regex, r"\g<1>", sent))


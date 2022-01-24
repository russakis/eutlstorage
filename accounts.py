import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from main import ignite,execute_query,create_server_connection,createcountrydic

def exploration():
    startingurl='https://ec.europa.eu/clima/ets'
    url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option", attrs={'class': 'formOptionListMedium'})
    values=[item["value"] for item in results[32:]]
    for value in values:
        try:
            newurl=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.accountFullTypeCodes={value}&accountHolder=&search=Search&searchType=account&currentSortSettings='
            response = requests.get(newurl)
            soup = BeautifulSoup(response.text, 'html.parser')
            newresults = soup.find_all("a", attrs={'class': 'listlink'})
            extraurl=startingurl + newresults[0]["href"][11:]
            response = requests.get(extraurl)
            soup = BeautifulSoup(response.text, 'html.parser')
            pageres = soup.find_all("span", attrs={'class': 'classictext'})
            temp3 = soup.find_all("a", attrs={'class': 'listlink'})
            print([i.string for i in results[32:]][values.index(value)],len(pageres)+len(temp3))
        except IndexError:
            print([i.string for i in results[32:]][values.index(value)], "no shit found")


def indaccount(url):
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results=soup.find_all("span",attrs={'class':'classictext'})
            temp=[item.string for item in results]
            #temp=[item.string[7:-6] for item in results]
            temp2=[]
        except:
            print("found an exception")
            continue
        break
    for item in temp:
        item=item.replace('\n', '')
        item=item.replace('\r', '')
        item=item.replace('\t', '')
        item=item.replace('\xa0', '')
        item = item.replace('\"','\'')
        item = item.lstrip()
        if item!="":temp2.append(item.rstrip())
        else: temp2.append("NULL")
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
    #temp2[1]=abbrs[countries.index(temp2[1])]
    if temp2[6]=="Null":temp2[6]="1941-09-09 00:00:00.0"
    print(temp2)
    if temp2[0]=="Aircraft Operator Account":
        specs = (nickname,accname,id,acctype,country,accstatus,accopening,accclosing)=(name,temp2[9],temp2[2],temp2[0],temp2[1],temp2[4],temp2[5],temp2[6])
        holderspecs = (holdername,compno,holdertype,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[7],temp2[9],temp2[10],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18])
    else:
        specs = (nickname, accname,id, acctype, country, accstatus, accopening, accclosing) = (name, temp2[10],temp2[2], temp2[0], temp2[1], temp2[4], temp2[5], temp2[6])
        holderspecs = (holdername,compno,holdertype,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[7],temp2[9],temp2[10],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18])
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
    wantedstr = ""
    for element in wanted:
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\"" + element + "\","
    wantedstr = "(" + wantedstr[:-1] + ")"

    accountcounter += 1

    addaccount(connection,wantedstr)
    return wanted

def addholder(connection,attributes):
    sql = f"""
        INSERT INTO Holders
        (rawCode,holdername,companyno,legalid,address,address2,zipcode,city,country,tel,tel2,email)
        VALUES {attributes}"""
    execute_query(connection, sql)

def addaccount(connection,attributes):
    sql = f"""
            INSERT INTO Accounts
            (rawCode,holdercode, nickname,typeofaccount, installationname,installationID,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
            VALUES {attributes}
            ON DUPLICATE KEY UPDATE
            nickname     = VALUES(nickname)"""
    execute_query(connection, sql)

def addaircraft(connection,attributes):
    sql = f"""
        INSERT INTO Aircrafts
        (rawCode,holderName,holdercode,aircraftid,eccode,monitoringplan,monitoringfirstyear,monitoringfinalyear,subsidiary,parent,eprtr,callsign,firstyear,finalyear,address1,address2,zipcode,city,country,latitude,longitude,mainactivity,status)
        VALUES {attributes}
        ON DUPLICATE KEY UPDATE
        nickname     = VALUES(nickname)"""
    execute_query(connection, sql)

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    pageno = 0
    holdercounter = 1
    accountcounter = 1
    connection=create_server_connection('localhost','root','')
    ignite(connection,"storage")
    countrydic=createcountrydic(connection)
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
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE','GB']
    """url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option",attrs={'class':'formOptionListMedium'})
    clima=[item['value'] for item in results if len(item['value'])==2]"""
    #url='https://ec.europa.eu/clima/ets/singleAccount.do?accountID=14631&action=details&languageCode=en&returnURL=accountHolder%3D%26search%3DSearch%26account.registryCodes%3DGR%26languageCode%3Den%26searchType%3Daccount%26currentSortSettings%3D&registryCode=GR'
    #url='https://ec.europa.eu/clima/ets/singleAccount.do?accountID=90686&action=details&languageCode=en&returnURL=resultList.currentPageNumber%3D10%26accountHolder%3D%26nextList%3DNext%26searchType%3Daccount%26currentSortSettings%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR'
    #one,two=indaccount(url)
    exploration()
    #print(len(accounts))
    #print(accounts[0])
    #row="('20 - Centrale énergétique (Dupont de Nemours)', 'Account holder', 'Former Operator Holding Account', 'closed', 'Luxembourg', '2006-06-08 00:00:00.0', '2014-06-30 10:41:05.0', '')"
    #print(re.sub(regex, r"\g<1>", sent))


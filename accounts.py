import requests
import urllib.request
from bs4 import BeautifulSoup
import re
from main import ignite,execute_query,create_server_connection,cleanitem,holderaddition,accountaddition
import time
from utilityfuncs import *

def indaccount(url):
    while True:#catching exceptions during execution
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results=soup.find_all("span",attrs={'class':'classictext'})
            fields=[item.string for item in results]
            information=[]
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("found an exception")
            continue
        break
    for item in fields:
        item=cleanitem(item)
        information.append(item if item!="" else "NULL")
    thirdcolumn=soup.find_all("span",attrs={'class':'resultlink'})#check if there is hyperlink in third field
    if thirdcolumn!=[]:#if there is a hyperlink here it belongs in the operator holding accounts
        try:
            information= information[:2]+[thirdcolumn[0].string[7:-6]]+information[2:]
        except IndexError:
            information=information[:2]+[""]+information[2:]
    results= soup.find_all("font",attrs={'class':'bordertbheadfont'})
    alias=cleanitem(results[0].getText()[31:])
    if information[6]=="Null":information[6]="1941-09-09 00:00:00.0" #assigning a "random" date to null dates
    someresults = soup.find_all("span", attrs={'class': 'titlelist'})
    try: #two letter identifier for country, and Avalon if the country isn't in the dic
        if len(someresults) == 20:
                information[16]=countrydic[information[16]]#turning country names to two character identifiers
        else: information[15]=countrydic[information[15]]
    except:
        if len(someresults) == 20:
            information[16]="AV"#stands for avalon, the placeholder for uknown country
        else:
            information[15]="AV"
    if len(someresults)==20:
        specs =(alias,information[10],information[2],information[0],countrydic[information[1]],information[4],information[5],information[6],information[7]) #(nickname,accname,id,acctype,country,accstatus,accopening,accclosing,commitment)
        holderspecs =(information[3],information[8],information[11],information[12],information[13],information[14],information[15],information[16],information[17],information[18],information[19])#(holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)
        specdic=dict(zip(["alias","accname","id","typeofaccount","country","status","accopening","accclosing","commitmentperiod"],list(specs)))
        holderdic=dict(zip(["holderName","companyno","legalid","address","address2","zipcode","city","country","tel","tel2","email"],list(holderspecs)))
    else:
        specs  = (alias, information[9],information[2], information[0], countrydic[information[1]], information[4], information[5], information[6],"NULL") #(nickname, accname,id, acctype, country, accstatus, accopening, accclosing,commitment)
        holderspecs =(information[3],information[7],information[10],information[11],information[12],information[13],information[14],information[15],information[16],information[17],information[18])#(holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)
        specdic = dict(zip(["alias", "accname", "id", "typeofaccount", "country", "status", "accopening", "accclosing","commitmentperiod"], list(specs)))
        holderdic = dict(zip(["holderName", "companyno", "legalid", "address", "address2", "zipcode", "city", "country", "tel","tel2", "email"], list(holderspecs)))
    return holderdic,specdic,information[0]#returning the holder information the account information and the account type

def accountresults(url):
    # url = 'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes=GR&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("found an exception")
            continue
        break
    temp3 = soup.find_all("a", attrs={'class': 'listlink'})
    #templinks = [startingurl + obj['href'][11:] for obj in temp3]
    templinks = [obj['href'] for obj in temp3]
    #reallinks = [templinks[1 + i] for i in range(len(templinks) - 1) if i % 3 == 0]
    return templinks

def controller(countries,pagestosearch):
    accounts=[]
    holders=[]
    for country in countries:#countries[21:22]:
        try:
            pageno=0
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&searchType=account&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                                 'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
            # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
            pages = temp[0]['value']
            print(country, pages)
            pages = [i for i in range(int(pages))]
            if pagestosearch != [] and len(pagestosearch) < len(pages):
                pages = pagestosearch
            for pageno in pages:
                print(pageno+1,"/",pages[-1]+1)
                url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&searchType=account&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                holderlinks = accountresults(url)
                #with the links we want to crawl these pages and store the individual information
                for link in holderlinks:
                    result, instresult, acctype = indaccount(link)
                    code = holderaddition(connection,result)
                    accountaddition(connection,list(instresult.keys()),list(instresult.values()), code)
        except IndexError:
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
            holderlinks = accountresults(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result, instresult, acctype = indaccount(link)
                code = holderaddition(connection, result)
                accountaddition(connection,list(instresult.keys()), list(instresult.values()), code)
    return (holders,accounts)

def operatingupdate(row,code):
    (nickname, accname, id, acctype, country, accstatus, accopening, accclosing)=row
    global connection
    sql = f"""UPDATE Accounts
            SET alias = \"{nickname}\"
            WHERE (installationid = {id} AND country = \"{country}\");"""
    execute_query(connection, sql)

def addholder(connection,columns,attributes,holdername):
    sql = f"""
        INSERT INTO Holders
        ({','.join(columns)})
        VALUES ({','.join(attributes)});"""
    execute_query(connection, sql)

def allaccounts(start=0,end=33):
    for country in countries[start:end]:
        start = time.time()
        print("COUNTRY", country)
        controller([country], [])
        thistime = time.time()
        print(f"The country {country} took ", thistime - start, " seconds")

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    pageno = 0
    holdercounter = 1
    accountcounter = 1
    connection=create_server_connection('localhost','root','')
    ignite(connection,"EUTL")
    countrydic=createcountrydic(connection)
    triedandtrue=[]
    #for abb in abbrs:
    #    url=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={abb}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE','GB']
    allaccounts(32,33)
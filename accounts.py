import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from main import ignite,execute_query,create_server_connection,createcountrydic,cleanitem
import time

def exploration():
    startingurl='https://ec.europa.eu/clima/ets'
    url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option", attrs={'class': 'formOptionListMedium'})
    values=[item["value"] for item in results[32:]]
    urls=[]
    for value in values:
        try:
            newurl=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.accountFullTypeCodes={value}&accountHolder=&search=Search&searchType=account&currentSortSettings='
            response = requests.get(newurl)
            soup = BeautifulSoup(response.text, 'html.parser')
            newresults = soup.find_all("a", attrs={'class': 'listlink'})
            extraurl=startingurl + newresults[0]["href"][11:]
            urls.append(extraurl)
            response = requests.get(extraurl)
            soup = BeautifulSoup(response.text, 'html.parser')
            pageres = soup.find_all("span", attrs={'class': 'classictext'})
            temp3 = soup.find_all("a", attrs={'class': 'listlink'})
            print([i.string for i in results[32:]][values.index(value)],len(pageres)+len(temp3))
        except IndexError:
            print([i.string for i in results[32:]][values.index(value)], "no shit found")
    temp=[]
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all("span", attrs={'class': 'titlelist'})
        categories = [item.string for item in results]
        l = []
        for item in categories:
            item=cleanitem(item)
            # if item == '': print(newarr.index(tempitem))
            if item != '': l.append(item)
        temp.append(l)
    for li in temp:
        print(values[temp.index(li)])
        print(list(set(temp[1])-set(li)))
        print(list(set(li)-set(temp[1])))
        print(temp[1]==li)


def indaccount(url):
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results=soup.find_all("span",attrs={'class':'classictext'})
            temp=[item.string for item in results]
            #temp=[item.string[7:-6] for item in results]
            temp2=[]
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("found an exception")
            continue
        break
    for item in temp:
        item=cleanitem(item)
        if item!="":temp2.append(item)
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
    someresults = soup.find_all("span", attrs={'class': 'titlelist'})
    try:
        if len(someresults) == 20:
            temp2[16]=countrydic[temp2[16]]#turning country names to two character identifiers
        else: temp2[15]=countrydic[temp2[15]]
    except:
        if len(someresults) == 20:
            print(temp2[15],temp2[16])
            temp2[16]="AV"
        else:
            print(temp2[14],temp2[15])
            temp2[15]="AV"
    if len(someresults)==20:
        specs = (nickname,accname,id,acctype,country,accstatus,accopening,accclosing,commitment)=(name,temp2[10],temp2[2],temp2[0],countrydic[temp2[1]],temp2[4],temp2[5],temp2[6],temp2[7])
        holderspecs = (holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[8],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18],temp2[19])
    else:
        specs = (nickname, accname,id, acctype, country, accstatus, accopening, accclosing,commitment) = (name, temp2[9],temp2[2], temp2[0], countrydic[temp2[1]], temp2[4], temp2[5], temp2[6],"NULL")
        holderspecs = (holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[7],temp2[10],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18])
    return holderspecs,specs,acctype

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
    templinks = [startingurl + obj['href'][11:] for obj in temp3]
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
                    code = holderaddition(result)
                    accountaddition(instresult, code)
        except IndexError:
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            url = f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={country}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
            holderlinks = accountresults(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result, instresult, acctype = indaccount(link)
                code = holderaddition(result)
                accountaddition(instresult, code)
    return (holders,accounts)

def operatingupdate(row,code):
    (nickname, accname, id, acctype, country, accstatus, accopening, accclosing)=row
    global connection
    sql = f"""UPDATE Accounts
            SET alias = \"{nickname}\"
            WHERE (installationid = {id} AND country = \"{country}\");"""
    execute_query(connection, sql)

def aircraftupdate(row,code):
    (nickname, accname,id, acctype, country, accstatus, accopening, accclosing)=row
    global connection
    sql=f"""UPDATE Aircrafts
        SET alias = \"{nickname}\"
        WHERE (aircraftid = {id} AND country = \"{country}\");"""
    execute_query(connection,sql)

def holderaddition(row):
    (holdername, compno, legalid, address, address2, zipcode, city, country, tel1, tel2, email) = row
    global connection
    query = 'SELECT COUNT(*) FROM Holders;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    rawCode = result + 1
    query = f'SELECT rawCode FROM HOLDERS WHERE holdername = \"{holdername}\"'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if result == []:  # if there exists no entry for that company number we move to create one
        wanted = [f"{rawCode}"] + [row[i] for i in range(11)]
        wantedstr = ""
        for element in wanted:
            if element == "NULL":
                wantedstr += f"{element},"
            else:
                wantedstr += "\"" + element + "\","
        wantedstr = "(" + wantedstr[:-1] + ")"
        # wantedstr = f"({wanted[0]},\"{wanted[1]}\",\"{wanted[2]}\",\"{wanted[3]}\",\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
        #            f",\"{wanted[11]}\")"
        addholder(connection, wantedstr)
        return rawCode
    else:  # otherwise return the rawCode so as to insert new account/aircraft
        return result[0][0]

def accountaddition(row,code):
    (alias, accname, id, acctype, country, accstatus, accopening, accclosing,commitmentperiod)=row
    global connection
    query = 'SELECT COUNT(*) FROM Accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    # result = int(execute_query(connection,query)[0][0])
    accountcounter = result + 1
    wanted = [f"{accountcounter}", f"{code}"] + [row[i] for i in range(len(row))]
    if wanted[4]=="NULL":
        wanted[4]="no ID"
    # for i in [7, 8]: #due to issues with inserting null into date field, i've chosen to insert a seemingly random date instead
    #    if wanted[i] == "NULL":
    #        wanted[i] = "1941-09-09"
    wantedstr = ""
    for element in wanted:
        element=element.replace("\"","\\\"")
        element=element.replace("\'","\\\'")

        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\'" + element + "\',"
    wantedstr = "(" + wantedstr[:-1] + ")"
    extra=[]
    for i in [2,10,8,9]:
        element=wanted[i].replace("\"","\\\"")
        extra.append(element.replace("\'","\\\'"))
    # wantedstr = f"({wanted[0]},{wanted[1]},\"{wanted[2]}\",\"{wanted[3]}\",\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
    #            f",\"{wanted[11]}\",{wanted[12]},{wanted[13]},\"{wanted[14]}\",\"{wanted[15]}\",\"{wanted[16]}\",\"{wanted[17]}\",\"{wanted[18]}\",\"{wanted[19]}\",\"{wanted[20]}\"," \
    #            f"{wanted[21]},\"{wanted[22]}\")"
    # insert into Accounts (rawCode,holdercode, nickname,typeofaccount, installationname,installationID,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
    addaccount(connection, wantedstr,extra)
    return wanted

def aircraftaddition(row,holdercode):
    (airname, airid, eccode, monitoringplan, monfirstyear, monfinalyear, subsidiary, parent,
     eprtr, callsign, firstyear,lastyear, address, address2, zipcode, city, country, latitude, longitude, mainactivityholder,status)=row
    global connection
    query='select count(*) from Accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result=cursor.fetchall()[0][0]
    #result = int(execute_query(connection,query)[0][0])
    accountcounter=result+1
    wanted=[f"{accountcounter}"]+[row[0],f"{holdercode}"]+ [row[i] for i in range(1,21)]
    if wanted[3][0]==0:
        print("WE WOULD LIKE TO INFORM YOU YOU DONE FUCKED UP")
    #for i in [6,7]:
    #    if wanted[i]=="NULL":
    #        wanted[i]="1941-09-09"
    wantedstr = ""
    for element in wanted:
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\'" + element + "\',"
    wantedstr = "(" + wantedstr[:-1] + ")"
    #wantedstr=f"({wanted[0]},\"{wanted[1]}\",{wanted[2]},{wanted[3]},\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
    #          f",\"{wanted[11]}\",{wanted[12]},{wanted[13]},\"{wanted[14]}\",\"{wanted[15]}\",\"{wanted[16]}\",\"{wanted[17]}\",\"{wanted[18]}\",\"{wanted[19]}\",\"{wanted[20]}\"," \
    #             f"{wanted[21]},\"{wanted[22]}\")"
    addaircraft(connection,wantedstr)
    return wanted

def addholder(connection,attributes):
    sql = f"""
        INSERT INTO Holders
        (rawCode,holdername,companyno,legalid,address,address2,zipcode,city,country,tel,tel2,email)
        VALUES {attributes}"""
    execute_query(connection, sql)

def addaccount(connection,attributes,extra):
    for i in range(len(extra)):
        if extra[i]!="NULL":extra[i]=f"\'{extra[i]}\'"
    sql = f"""
        INSERT INTO Accounts
        (rawCode,holdercode, alias, accname, id, typeofaccount, country, status, accopening, accclosing,commitmentperiod)
        VALUES {attributes}
        ON DUPLICATE KEY UPDATE
        alias={extra[0]},
        commitmentperiod={extra[1]},
        accopening ={extra[2]},
        accclosing = {extra[3]};"""
    execute_query(connection, sql)

def addaircraft(connection,attributes):
    sql = f"""
        INSERT INTO Accounts
        (rawCode,holderName,holdercode,id,eccode,monitoringplan,monitoringfirstyear,monitoringfinalyear,subsidiary,parent,eprtr,callsign,firstyear,finalyear,address1,address2,zipcode,city,country,latitude,longitude,mainactivity,status)
        VALUES {attributes}
        ON DUPLICATE KEY UPDATE
        alias     = VALUES(alias)"""
    execute_query(connection, sql)


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
    """url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option",attrs={'class':'formOptionListMedium'})
    clima=[item['value'] for item in results if len(item['value'])==2]"""
    """    attributes="(\"one\",\"two\",\"three\")"
    print(attributes.split(",")[-1][:-1])
    url='https://ec.europa.eu/clima/ets/singleAccount.do?accountID=90554&action=details&languageCode=en&returnURL=resultList.currentPageNumber%3D9%26accountHolder%3D%26nextList%3DNext%26searchType%3Daccount%26currentSortSettings%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR'
    one,two,three=indaccount(url)
    wanted=two
    wantedstr = ""
    for element in wanted:
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\"" + element + "\","
    wantedstr = "(" + wantedstr[:-1] + ")"
    print(wantedstr.split(",")[-1][:-1])"""
    # countries.remove("BG")
    """    url='https://ec.europa.eu/clima/ets/singleAccount.do?accountID=96351&action=details&languageCode=en&returnURL=resultList.currentPageNumber%3D1%26accountHolder%3D%26search%3DSearch%26searchType%3Daccount%26currentSortSettings%3D%26account.registryCodes%3DMT%26languageCode%3Den&registryCode=MT'
    one,two,_=indaccount(url)
    code=holderaddition(one)
    want=accountaddition(two,code)
    print(want)"""
    for country in countries[9:15]:
        start = time.time()
        print("COUNTRY", country)
        controller([country], [])
        thistime = time.time()
        print(f"The country {country} took ", thistime - start, " seconds")
    #print(len(accounts))
    #print(accounts[0])
    #row="('20 - Centrale énergétique (Dupont de Nemours)', 'Account holder', 'Former Operator Holding Account', 'closed', 'Luxembourg', '2006-06-08 00:00:00.0', '2014-06-30 10:41:05.0', '')"
    #print(re.sub(regex, r"\g<1>", sent))



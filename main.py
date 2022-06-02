import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
#import urllib.request
from bs4 import BeautifulSoup
#import re
import time
from utilityfuncs import *
#from compliance import liststringsum


def indholder(url): #function to handle the individual holder information plus the account of the operating account holder page
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find_all("span", attrs={'class': 'bordertbheadfont'})
            titles = [item.string for item in title]
            temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break
    noiseinformation = [item.string for item in temp]
    information = []
    noiseinformation= noiseinformation[:40]
    for item in noiseinformation:
        item=cleanitem(item)
        #if item == '': print(noiseinformation.index(tempitem))
        if item != '': information.append(item)
        else: information.append("NULL")
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        information[35]=information[35].split('-')[0]#turning mainactivity to two character identifier
    else: information[34]=information[34].split('-')[0]#turning mainactivity to two character identifier
    information[0]=countrydic[information[0]]
    try:
        information[13]=countrydic[information[13]]#turning country names to two character identifiers
    except:
        print(information[13],information[12])
        information[13]="AV"
    holder =tuple([information[i] for i in [2,4,8,9,10,11,12,13,14,15,16]])#= (holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email)
    holderdic = dict(zip(["holderName","companyno","legalid","address","address2","zipcode","city","country","tel","tel2","email"],holder))
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        installation = tuple([information[i] for i in [2,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,35,5]])#= (airname, airid, eccode, monitoringplan, monfirstyear,monfinalyear, subsidiary,parent,eprtr,callsign,firstyear,lastyear,address,address2,zipcode,city,country,latitude,longitude,mainactivityholder,status)
        specdic = dict(zip(["accname", "id", "eccode", "monitoringplan", "monitoringfirstyear","monitoringfinalyear"," subsidiary","parent","eprtr","callsign","firstyear","finalyear","address","address2","zipcode","city","country","latitude","longitude","mainactivity","status"],installation))
    else:
        installation  = tuple([information[i] for i in [18,17,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,5]])#= (instname,instid, permitid,permitentrydate,permitexpirationdate,subsidiaryundertaking,parentundertaking,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude,longitude,mainactivity,status) \
        specdic = dict(zip(["accname","id", "permitid","permitentry","permitexpiry","subsidiary","parent","eprtr","firstyear","finalyear","address","address2","zipcode","city","country","latitude","longitude","mainactivity","status"],installation))
    titles = soup.find_all("span", attrs={'class': 'titlelist'})
    for title in titles:#signify the start of the compliance part
        if cleanitem(title.text) == "EU ETS Phase":
            startingpoint = titles.index(title)
            break
    trials = soup.find_all('td', attrs={'class': 'bgcelllist'})
    trials = trials[startingpoint:]
    children = []
    for trial in trials:
        child = trial.findChildren()
        if len(child) > 1:
            children.append(liststringsum([cleanitem(item.text) for item in child if cleanitem(item.text) != 'NULL']))
        else:
            children.append(cleanitem(child[0].text))
    yearutil = [[f"2005-2007", f"{year}"] for year in range(2005, 2008)] + [[f"2008-2012", f"{year}"] for year in
                                                                            range(2008, 2013)] + [
                   [f"2013-2020", f"{year}"] for year in range(2013, 2020)] + [[f"2020-2030", f"{year}"] for year in
                                                                               range(2020, 2031)]
    complianceres = [children[x:x + 6] for x in range(0, len(children), 6)]
    # correct = list(zip(yearutil,complianceres[26]))
    compl = map(list.__add__, yearutil, complianceres)
    return(holderdic,specdic,len(installation)==21,compl)
    #return (holder,installation,len(installation)==21,compl)#returns holder, installation, a boolean for isAircraft

def holderspage(url):
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break
    temp3 = soup.find_all("a", attrs={'class': 'listlink'})
    templinks = [obj['href'] for obj in temp3]
    #templinks = [startingurl + obj['href'][11:] for obj in temp3]
    reallinks = [templinks[1+i] for i in range(len(templinks)-1) if i%3==0]
    return reallinks

def holdercontroller(countries,pagestosearch):#countries in list form, pagestosearch in list form unless you want them all
    accounts=[]
    holders=[]
    global connection
    for country in countries:#countries[21:22]:
        try:
            pageno=0
            url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                                 'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
            # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
            pages = temp[0]['value']
            print(country,pages)
            pages=[i for i in range(int(pages))]
            if pagestosearch!=[] and len(pagestosearch)<len(pages):
                pages=pagestosearch
            for pageno in pages:
                print(pageno+1,"/",pages[-1]+1, country)
                url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                holderlinks = holderspage(url)
                #with the links we want to crawl these pages and store the individual information
                for link in holderlinks:
                    result, instresult, isAircraft,compl = indholder(link)
                    code = holderaddition(connection,result)
                    if isAircraft:
                        #_, acckey = aircraftaddition(instresult, code)
                        _, acckey = accountaddition(connection, list(instresult.keys()),list(instresult.values()), code)
                        #complianceaddition(compl, [f"{instresult[1]}", f"{instresult[16]}", f"{acckey}"])
                    else:
                        _, acckey = accountaddition(connection, list(instresult.keys()),list(instresult.values()), code)
                        #complianceaddition(compl, [f"{instresult[1]}", f"{instresult[14]}", f"{acckey}"])
        except IndexError:
            url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            holderlinks = holderspage(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result,instresult,isAircraft,compl = indholder(link)
                code = holderaddition(connection,result)
                if isAircraft:
                    #_, acckey = aircraftaddition(instresult, code)
                    _, acckey = accountaddition(connection, list(instresult.keys()), list(instresult.values()), code)
                    #complianceaddition(compl, [f"{instresult[1]}", f"{instresult[16]}", f"{acckey}"])

                else:
                    _, acckey = accountaddition(connection, list(instresult.keys()), list(instresult.values()), code)
                    #complianceaddition(compl, [f"{instresult[1]}", f"{instresult[14]}", f"{acckey}"])

def holderaddition(connection,dic):
    columns = list(dic.keys())
    row = list(dic.values())
    #(holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email) = row
    # global connection
    query = 'SELECT COUNT(*) FROM Holders;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    rawCode = result + 1
    query = f'SELECT rawCode FROM Holders WHERE holderName = \"{dic["holderName"]}\"'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    wanted = [f"{rawCode}"] + [row[i] for i in range(len(row))]
    columns = ["rawCode"] + [columns[i] for i in range(len(columns))]
    if result==[]:  #if there exists no entry for that company number we move to create one
        addholder2(connection,columns,wanted)
        return rawCode
    else: #otherwise return the rawCode so as to insert new account/aircraft
        print("Holder already exists, no action performed")
        #addholder2(connection,columns,wanted)
        return result[0][0]

def accountaddition(connection,columns,row,code):
    query = 'SELECT COUNT(*) FROM Accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    # result = int(execute_query(connection,query)[0][0])
    accountcounter = result + 1
    if len(row)>20 : #if it is an aircraft account
        wanted = [f"{accountcounter}",f"{code}","no alias","Aircraft Operator Account"] + [row[i] for i in range(len(row))]
        columns = ["rawCode","holdercode","alias","typeofaccount"] + [columns[i] for i in range(len(columns))]
    elif len(row)>14 : # if it is an operator account
        wanted = [f"{accountcounter}", f"{code}", "no alias", "Operator Holding Account"] + [row[i] for i in range(len(row))]
        columns = ["rawCode","holdercode","alias","typeofaccount"] + [columns[i] for i in range(len(columns))]
    else: # if it is any account of the account page
        wanted=[f"{accountcounter}",f"{code}"] + [row[i] for i in range(len(row))]
        columns = ["rawCode","holdercode"] + [columns[i] for i in range(len(columns))]
    addaccount(connection,columns,wanted)
    return wanted, 5

def complianceaddition(row,code):
    global connection
    wantedstr = ""
    for lis in row:
        wanted=code + [lis[i] for i in range(0,len(lis))]
        wantedstr+="("
        for element in wanted:
            if element == "NULL" or element.isnumeric():
                wantedstr += f"{element},"
            else:
                wantedstr += "\"" + element + "\","
        wantedstr = wantedstr[:-1] + "),\n"
    wantedstr=wantedstr[:-2]+";"
    addcompliance(connection,wantedstr)

def alloperators(starting=0,ending=33):
    for country in countries[starting:ending]:
        start = time.time()
        print("COUNTRY", country)
        holdercontroller([country], [])
        thistime = time.time()
        print(f"The country {country} took ", thistime - start, " seconds")

def complianceexperimentation():
    response = requests.get(
        "https://ec.europa.eu/clima/ets/ohaDetails.do?returnURL=&languageCode=en&accountID=&registryCode=&buttonAction=all&action=&account.registryCode=&accountType=&identifierInReg=&accountHolder=&primaryAuthRep=&installationIdentifier=&installationName=&accountStatus=&permitIdentifier=&complianceStatus=&mainActivityType=-1&searchType=oha&account.registryCodes=GR&account.complianceStatusArray=C&resultList.currentPageNumber=47&nextList=Next%C2%A0%3E&selectedPeriods=")
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find_all("span", attrs={'class': 'bordertbheadfont'})
    titles = [item.string for item in title]
    titles = soup.find_all("span", attrs={'class': 'titlelist'})
    for title in titles:  # signify the start of the compliance part
        print(cleanitem(title.text))
        if cleanitem(title.text) == "EU ETS Phase":
            startingpoint = titles.index(title)
            break
    trials = soup.find_all('td', attrs={'class': 'bgcelllist'})
    trials = trials[startingpoint:]
    children = []
    lastborn = []
    for trial in trials:
        child = trial.findChildren()
        # print("child",child)
        if len(child) > 1:
            for l in child:
                lastborn.append(l)
            # children.append(sum([int(cleanitem(item).text) for item in child]))
            children.append(liststringsum([cleanitem(item.text) for item in child if cleanitem(item.text) != 'NULL']))
        else:
            lastborn.append('NULL')
            children.append(cleanitem(child[0].text))
    yearutil = [[f"2005-2007", f"{year}"] for year in range(2005, 2008)] + [[f"2008-2012", f"{year}"] for year in
                                                                            range(2008, 2013)] + [
                   [f"2013-2020", f"{year}"] for year in range(2013, 2020)] + [[f"2020-2030", f"{year}"] for year in
                                                                               range(2020, 2031)]
    complianceres = [children[x:x + 6] for x in range(0, len(children), 6)]
    # correct = list(zip(yearutil,complianceres[26]))
    compl = map(list.__add__, yearutil, complianceres)
    result = list(compl)
    # for res in result:
    #    print(res)
    print("trial")
    last = []
    for l in lastborn:
        if l != 'NULL':
            last.append(cleanitem(l.text))
        else:
            last.append(l)
    print(last)
    final = []  # [item for sublist in [[int(s) for s in txt.split() if s.isdigit()] for txt in last] for item in sublist ]
    for thing in last:
        newthing = thing.replace('*', '')
        print(newthing)
        if newthing.isdigit():
            final.append(newthing)
    hello = []
    print(complianceres)
    finalclean = []
    withasterisks = []
    for i in result[:20]:
        boo = False
        allcompls = i[:2]
        asteriskones = i[:2]
        for j in i[2:7]:
            if '*' in j:
                boo = True
                asterisks = j
                arr = asterisks.replace("*", "").split(",")
                arr.remove("")
                s = sum(list(map(int, arr)))
                print(arr, s)
                allcompls.append(s)
                asteriskones.append(int(arr[-1]))
            else:
                allcompls.append(j)
                asteriskones.append(j)
        if boo:
            withasterisks.append(asteriskones)
        finalclean.append(allcompls)

    print(result)
    print(len(withasterisks))
    print(finalclean)

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE','GB']
    country = countries[4]
    pageno = 0
    holders = []
    accounts = []
    holdercounter = 1
    accountcounter = 1
    connection=create_server_connection('localhost','root','')
    ignite(connection,"EUTL")
    countrydic=createcountrydic(connection)
    #alloperators(25,33)


        #print(i)
    print(int('4')+int('748'))
    #for trial in trials:
    #    print(cleanitem(trial.text))
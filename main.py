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

def getcountries(connection):
    cursor = connection.cursor()
    sql = "select abbr2L,name from countries"
    cursor.execute(sql)
    result = cursor.fetchall()
    return dict((y,x) for x,y in result)

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
    newarr = [item.string for item in temp]
    thisnew = []
    newarr= newarr[:40]
    for item in newarr:
        item=cleanitem(item)
        #if item == '': print(newarr.index(tempitem))
        if item != '': thisnew.append(item)
        else: thisnew.append("NULL")
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        thisnew[35]=thisnew[35].split('-')[0]#turning mainactivity to two character identifier
    else: thisnew[34]=thisnew[34].split('-')[0]#turning mainactivity to two character identifier
    thisnew[0]=countrydic[thisnew[0]]
    try:
        thisnew[13]=countrydic[thisnew[13]]#turning country names to two character identifiers
    except:
        print(thisnew[13],thisnew[12])
        thisnew[13]="AV"
    holder =(holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email)=tuple([thisnew[i] for i in [2,4,8,9,10,11,12,13,14,15,16]])
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        installation = (airname, airid, eccode, monitoringplan, monfirstyear,monfinalyear, subsidiary,parent,eprtr,callsign,firstyear,lastyear,address,address2,zipcode,city,country,latitude,longitude,mainactivityholder,status) \
            = tuple([thisnew[i] for i in [2,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,35,5]])
    else:
        installation = (instname,instid, permitid,permitentrydate,permitexpirationdate,subsidiaryundertaking,parentundertaking,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude,longitude,mainactivity,status) \
            = tuple([thisnew[i] for i in [18,17,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,5]])
    titles = soup.find_all("span", attrs={'class': 'titlelist'})
    for title in titles:
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
    return (holder,installation,len(installation)==21,compl)#returns holder, installation, a boolean for isAircraft

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
    templinks = [startingurl + obj['href'][11:] for obj in temp3]
    reallinks = [templinks[1+i] for i in range(len(templinks)-1) if i%3==0]
    return reallinks

def holdercontroller(countries,pagestosearch):#countries in list form, pagestosearch in list form unless you want them all
    accounts=[]
    holders=[]
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
                print(pageno+1,"/",pages[-1]+1)
                url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                holderlinks = holderspage(url)
                #with the links we want to crawl these pages and store the individual information
                for link in holderlinks:
                    result, instresult, isAircraft,compl = indholder(link)
                    code = holderaddition(result)
                    if isAircraft:
                        _, acckey = aircraftaddition(instresult, code)
                        complianceaddition(compl, [f"{instresult[1]}", f"{instresult[16]}", f"{acckey}"])
                    else:
                        _, acckey = accountaddition(instresult, code)
                        complianceaddition(compl, [f"{instresult[1]}", f"{instresult[14]}", f"{acckey}"])
        except IndexError:
            url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            holderlinks = holderspage(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result,instresult,isAircraft,compl = indholder(link)
                code = holderaddition(result)
                if isAircraft:
                    _, acckey = aircraftaddition(instresult, code)
                    complianceaddition(compl, [f"{instresult[1]}", f"{instresult[16]}", f"{acckey}"])

                else:
                    _, acckey = accountaddition(instresult, code)
                    complianceaddition(compl, [f"{instresult[1]}", f"{instresult[14]}", f"{acckey}"])

def holderaddition(row):
    (holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email) = row
    global connection
    query = 'select count(*) from holders;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    rawCode = result + 1
    query = f'select rawCode from holders where holderName = \"{holdername}\"'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if result==[]:  #if there exists no entry for that company number we move to create one
        wanted = [f"{rawCode}"] + [row[i] for i in range(11)]
        wantedstr = ""
        for element in wanted:
            if element == "NULL":
                wantedstr += f"{element},"
            else:
                wantedstr += "\"" + element + "\","
        wantedstr = "(" + wantedstr[:-1] + ")"
        #wantedstr = f"({wanted[0]},\"{wanted[1]}\",\"{wanted[2]}\",\"{wanted[3]}\",\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
        #            f",\"{wanted[11]}\")"
        addholder(connection,wantedstr)
        return rawCode
    else: #otherwise return the rawCode so as to insert new account/aircraft
        return result[0][0]

def accountaddition(row,code):
    (instname, instid, permitid, permitentrydate, permitexpirationdate, subsidiaryundertaking, parentundertaking, eprtr,
     firstyear, finalyear, address, address2, zipcode, city, country, latitude, longitude, mainactivity, status)=row
    global connection
    query='SELECT COUNT(*) FROM Accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result=cursor.fetchall()[0][0]
    #result = int(execute_query(connection,query)[0][0])
    accountcounter=result+1
    wanted=[f"{accountcounter}",f"{code}","no alias","Operator Holding Account"]+[row[i] for i in range(19)]
    wantedstr = ""
    for element in wanted:
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\"" + element + "\","
    wantedstr = "(" + wantedstr[:-1] + ")"
    #insert into Accounts (rawCode,holdercode, nickname,typeofaccount, installationname,installationID,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
    co=addaccount(connection,wantedstr)
    if co=="ERROR":
        return wanted,accountcounter-1
    else: return wanted,accountcounter

def aircraftaddition(row,holdercode):
    (airname, airid, eccode, monitoringplan, monfirstyear, monfinalyear, subsidiary, parent,
     eprtr, callsign, firstyear,lastyear, address, address2, zipcode, city, country, latitude, longitude, mainactivityholder,status)=row
    global connection
    query='SELECT COUNT(*) FROM Accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result=cursor.fetchall()[0][0]
    accountcounter=result+1
    wanted=[f"{accountcounter}"]+[row[0],"no alias",f"{holdercode}","Aircraft Operator Account"]+ [row[i] for i in range(1,21)]
    if wanted[3][0]==0:
        print("WE WOULD LIKE TO INFORM YOU YOU DONE FUCKED UP")
    wantedstr = ""
    for element in wanted:
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\"" + element + "\","
    wantedstr = "(" + wantedstr[:-1] + ")"
    co = addaircraft(connection, wantedstr)
    if co == "ERROR":
        return wanted, accountcounter - 1
    else:
        return wanted, accountcounter

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

def createcountrydic(connection):
    countrydic = getcountries(connection)
    countrydic['Korea, Republic Of'] = countrydic['Korea, Republic of']
    countrydic['Moldova, Republic Of'] = countrydic['Moldova, Republic of']
    countrydic['European Commission'] = countrydic['European Union']
    countrydic['Virgin Islands, British'] = countrydic['British Virgin Islands']
    countrydic['Libyan Arab Jamahiriya'] = countrydic['Libya']
    countrydic['Virgin Islands, U.S.'] = countrydic['US Virgin Islands']
    countrydic['Viet Nam'] = countrydic['Vietnam']
    countrydic['Iran, Islamic Republic Of'] = countrydic['Iran, Islamic Republic of']
    countrydic['Taiwan, Province Of China'] = countrydic['Taiwan']
    countrydic['JERSEY'] = countrydic['Jersey']
    countrydic['Saint Kitts And Nevis']= countrydic['Saint Kitts and Nevis']
    return countrydic

def countriestable(connection):
    url='https://www.iban.com/country-codes'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("td")
    names = [item.string for item in results if results.index(item)%4==0]
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
    clima2=[item.string for item in results if len(item['value'])==2]
    print("discrepancies",[item for item in clima if item not in abb2])
    nonstarters=[item for item in clima if item not in [item2[3] for item2 in newcountries]]
    print(len(newcountries))
    ni = ('XI','Northern Ireland','Βόρεια Ιρλανδία','XI',None, 1,1,0,'Europe')
    eu = ('EU','European Union','Ευρωπαϊκή Ένωση','EU',None,None,None,None,"Europe")
    un = ('UN','United Nations','Ηνωμένα Έθνη','UN',None,None,None,None,None)
    uk = ('UK','United Kingdom','Ηνωμένο Βασίλειο','GB','GBR',1,0,1,'Europe')
    gr = ('EL','Greece','Ελλάδα','GR','GRC',1,1,1,'Europe')
    one=sorted(oldcountries[1:], key=lambda x: x[0])
    two = sorted(oldcountries[1:], key=lambda x: x[3])
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



# Press the green button in the gutter to run the script.
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
    #holderurl = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={pageno}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
    #countries.remove("GR")
    #countries.remove("BG")
    #url='https://ec.europa.eu/clima/ets/ohaDetails.do?accountID=91982&action=all&languageCode=en&returnURL=resultList.currentPageNumber%3D1%26installationName%3D%26accountHolder%3D%26permitIdentifier%3D%26nextList%3DNext%26form%3Doha%26searchType%3Doha%26currentSortSettings%3D%26mainActivityType%3D-1%26installationIdentifier%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR'
    """for country in countries[10:15 ]:
        start = time.time()
        print("COUNTRY",country)
        holdercontroller([country],[])
        thistime=time.time()
        print(f"The country {country} took ",thistime-start," seconds")"""
    """_,_,_,compl=indholder('https://ec.europa.eu/clima/ets/ohaDetails.do?accountID=91998&action=all&languageCode=en&returnURL=resultList.currentPageNumber%3D2%26installationName%3D%26accountHolder%3D%26permitIdentifier%3D%26nextList%3DNext%26form%3Doha%26searchType%3Doha%26currentSortSettings%3D%26mainActivityType%3D-1%26installationIdentifier%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR')
    for i in compl:
        print(i)"""
    a,b,c,d= indholder('https://ec.europa.eu/clima/ets/ohaDetails.do?accountID=90733&action=all&languageCode=en&returnURL=installationName%3D%26accountHolder%3D%26search%3DSearch%26permitIdentifier%3D%26form%3Doha%26searchType%3Doha%26currentSortSettings%3D%26mainActivityType%3D-1%26installationIdentifier%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR')
    print(list(d))
    holdercontroller(['AT'],[])
    # #countriestable(connection)
    #for account in accounts:
    #    accountaddition(account)
    #query = 'select count(*) from accounts;'
    #print(len(holders))
    #url='https://ec.europa.eu/clima/ets/ohaDetails.do?accountID=96348&action=all&languageCode=en&returnURL=installationName%3D%26accountHolder%3D%26search%3DSearch%26permitIdentifier%3D%26form%3Doha%26searchType%3Doha%26currentSortSettings%3D%26mainActivityType%3D-1%26installationIdentifier%3D%26account.registryCodes%3DMT%26languageCode%3Den&registryCode=MT'
    #response = requests.get(url)
    #soup = BeautifulSoup(response.text, 'html.parser')
    #title = soup.find_all("span", attrs={'class': 'classictext'})
    #titles = [item.string for item in title]
    #print(str(titles[17])[7:-6])
    # print(len(individual))
    # addrow(connection,individual,'accounts',('g','f','d','s'))
    # quer="create database storage"
    # create_database(connection,quer)

    # create_table(connection)
    # delete_table(connection)



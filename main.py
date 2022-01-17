# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import mysql.connector
from mysql.connector import Error
# import pandas as pd
import requests
#import urllib.request
# import time
from bs4 import BeautifulSoup
#import re


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


def ignite(connection, databasename):  # διαλέγω τη βάση
    sql = (f"USE {databasename}")
    cursor = connection.cursor()
    cursor.execute(sql)
    print(f"connected to {databasename}")


def getcountries(connection):
    cursor = connection.cursor()
    sql = "select eu_abbr2L,name from countries"
    cursor.execute(sql)
    result = cursor.fetchall()
    return dict((y,x) for x,y in result)


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


def create_table(connection, tablename):
    create_table = f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
      id VARCHAR(40) PRIMARY KEY UNIQUE,
      accname VARCHAR(50) NOT NULL,
      name VARCHAR(50),
      status VARCHAR(10) NOT NULL,
      address VARCHAR(40) NOT NULL,
      zipcode VARCHAR(15),
      city VARCHAR(30),
      country VARCHAR(30),
      registry VARCHAR(30),
      typeofacc VARCHAR(50)
      );
     """
    connection = create_db_connection("localhost", "root", "", "storage")  # Connect to the Database
    execute_query(connection, create_table)  # Execute our defined query


def delete_table(connection):
    create_teacher_table = """
    drop table teacher;"""
    connection = create_db_connection("localhost", "root", "", "trial")  # Connect to the Database
    execute_query(connection, create_teacher_table)  # Execute our defined query


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def accounts():
    url = 'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes=GR&accountHolder=&search=Search&searchType=account&currentSortSettings='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                         'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    pages = temp[0]['value']

    temp2 = soup.find_all("td", attrs={'class': 'bgtitlelist'})
    temp3 = soup.find_all("a", attrs={'class': 'listlink'})
    templinks = [startingurl + obj['href'][11:] for obj in temp3]
    print(templinks[0])


def individualaccount():
    url = 'https://ec.europa.eu/clima/ets/singleAccount.do?accountID=14625&action=details&languageCode=en&returnURL=accountHolder%3D%26search%3DSearch%26account.registryCodes%3DGR%26languageCode%3Den%26searchType%3Daccount%26currentSortSettings%3D&registryCode=GR'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    # s = re.sub('\s+', '', s)
    newarr = [item.string for item in temp]
    typeofacc = str(newarr[0])[7:-6]
    registry = str(newarr[1])[7:-6]
    accname = str(newarr[3])[7:-6]
    status = str(newarr[4])[7:-6]
    regno = str(newarr[8])[7:-6]
    name = str(newarr[10])[7:-6]
    address = str(newarr[12])[7:-6]
    zipcode = str(newarr[14])[7:-6]
    city = str(newarr[15])[7:-6]
    country = str(newarr[16])[7:-6]
    # print(str(newarr[12])[7:-6])
    return ((regno, accname, name, status, address, zipcode, city, country, registry, typeofacc))

def indholder(url): #function to handle the individual holder information plus the account of the operating account holder page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find_all("span", attrs={'class': 'bordertbheadfont'})
    titles = [item.string for item in title]
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    newarr = [item.string for item in temp]
    thisnew = []
    newarr= newarr[:40]
    for item in newarr:
        tempitem=item
        item = item.replace('\n', '')
        item = item.replace('\r', '')
        item = item.replace('\t', '')
        item = item.replace('\xa0', '')
        item = item.replace('\"','\'')
        item = item.lstrip()
        #if item == '': print(newarr.index(tempitem))
        if item != '': thisnew.append(item.rstrip())
        else: thisnew.append("NULL")
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        thisnew[35]=thisnew[35].split('-')[0]#turning mainactivity to two character identifier
    else: thisnew[34]=thisnew[34].split('-')[0]#turning mainactivity to two character identifier
    thisnew[0]=countrydic[thisnew[0]]
    try:
        thisnew[13]=countrydic[thisnew[13]]#turning country names to two character identifiers
    except:
        print(thisnew[13],thisnew[12])
        thisnew[13]="dq"
    holder =(holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email)=tuple([thisnew[i] for i in [2,4,8,9,10,11,12,13,14,15,16]])
    if titles[0][7:-7] == "Aircraft Operator Holding Account Information":
        installation = (airname, airid, eccode, monitoringplan, monfirstyear,monfinalyear, subsidiary,parent,eprtr,callsign,firstyear,lastyear,address,address2,zipcode,city,country,latitude,longitude,mainactivityholder,status) \
            = tuple([thisnew[i] for i in [2,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,35,5]])
    else:
        installation = (instname,instid, permitid,permitentrydate,permitexpirationdate,subsidiaryundertaking,parentundertaking,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude,longitude,mainactivity,status) \
            = tuple([thisnew[i] for i in [18,17,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,5]])
    return (holder,installation,len(installation)==21)#returns holder, installation, a boolean for isAircraft

def holderspage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp3 = soup.find_all("a", attrs={'class': 'listlink'})
    templinks = [startingurl + obj['href'][11:] for obj in temp3]
    reallinks = [templinks[1+i] for i in range(len(templinks)-1) if i%3==0]
    return reallinks

def holdercontroller(countries,pagestosearch):#countries in list form, pagestosearch in list form unless you want them all
    accounts=[]
    holders=[]
    for country in countries:#countries[21:22]:
        print(country)
        try:
            pageno=0
            url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                                 'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
            # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
            pages = temp[0]['value']
            pages=[i for i in range(int(pages))]
            if pagestosearch!=[] or len(pagestosearch)<len(pages):
                pages=pagestosearch
            for pageno in pages:
                print(pageno)
                url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                holderlinks = holderspage(url)
                #with the links we want to crawl these pages and store the individual information
                for link in holderlinks:
                    result, instresult, isAircraft = indholder(link)
                    code = holderaddition(result)
                    if isAircraft:
                        aircraftaddition(instresult, code)
                    else:
                        accountaddition(instresult, code)
                    #print(result)
        except IndexError:
            url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            holderlinks = holderspage(url)
            # with the links we want to crawl these pages and store the individual information
            for link in holderlinks:
                result,instresult,isAircraft = indholder(link)
                code = holderaddition(result)
                if isAircraft:
                    aircraftaddition(instresult,code)
                else:
                    accountaddition(instresult,code)
                # print(result)
    return (holders,accounts)
        #for pageno in

def holderaddition(row):
    (holdername,compno,legalid,address,address2,zipcode,city,country,tel1,tel2,email) = row
    global connection
    query = 'select count(*) from holders;'
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    rawCode = result + 1
    query = f'select rawCode from holders where companyno = \'{compno}\''
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if result==[]:
        wanted = [rawCode] + [row[i] for i in range(11)]
        wantedstr = f"({wanted[0]},\"{wanted[1]}\",\"{wanted[2]}\",\"{wanted[3]}\",\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
                    f",\"{wanted[11]}\")"
        addholder(connection,wantedstr)
        return rawCode
    else:
        return result[0][0]


def accountaddition(row,code):
    (instname, instid, permitid, permitentrydate, permitexpirationdate, subsidiaryundertaking, parentundertaking, eprtr,
     firstyear, finalyear, address, address2, zipcode, city, country, latitude, longitude, mainactivity, status)=row
    global accountcounter
    global connection
    query='select count(*) from accounts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result=cursor.fetchall()[0][0]
    #result = int(execute_query(connection,query)[0][0])
    accountcounter=result+1
    wanted=[accountcounter,code,"NULL"]+[row[i] for i in range(19)]
    for i in [6, 7]:
        if wanted[i] == "NULL":
            wanted[i] = "1941-09-09"
    wantedstr = f"({wanted[0]},{wanted[1]},\"{wanted[2]}\",\"{wanted[3]}\",\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
                f",{wanted[11]},{wanted[12]},\"{wanted[13]}\",\"{wanted[14]}\",\"{wanted[15]}\",\"{wanted[16]}\",\"{wanted[17]}\",\"{wanted[18]}\",\"{wanted[19]}\",{wanted[20]}," \
                f"\"{wanted[21]}\")"
    addaccount(connection,wantedstr)
    return wanted

def aircraftaddition(row,holdercode):
    (airname, airid, eccode, monitoringplan, monfirstyear, monfinalyear, subsidiary, parent,
     eprtr, callsign, firstyear,lastyear, address, address2, zipcode, city, country, latitude, longitude, mainactivityholder,status)=row
    #global accountcounter
    global connection
    query='select count(*) from Aircrafts;'
    cursor = connection.cursor()
    cursor.execute(query)
    result=cursor.fetchall()[0][0]
    #result = int(execute_query(connection,query)[0][0])
    accountcounter=result+1
    wanted=[accountcounter]+[row[0],holdercode]+ [row[i] for i in range(1,21)]
    for i in [6,7]:
        if wanted[i]=="NULL":
            wanted[i]="1941-09-09"
    wantedstr=f"({wanted[0]},\"{wanted[1]}\",{wanted[2]},{wanted[3]},\"{wanted[4]}\",\"{wanted[5]}\",\"{wanted[6]}\",\"{wanted[7]}\",\"{wanted[8]}\",\"{wanted[9]}\",\"{wanted[10]}\"" \
              f",\"{wanted[11]}\",{wanted[12]},{wanted[13]},\"{wanted[14]}\",\"{wanted[15]}\",\"{wanted[16]}\",\"{wanted[17]}\",\"{wanted[18]}\",\"{wanted[19]}\",\"{wanted[20]}\"," \
              f"{wanted[21]},\"{wanted[22]}\")"
    addaircraft(connection,wantedstr)
    return wanted

def addaccount(connection,attributes):
    sql = f"""
        insert into Accounts (rawCode,holdercode, nickname,installationname,installationID,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
        values {attributes}
        """
    execute_query(connection, sql)

def addaircraft(connection, attributes):
    #(airname, airid, eccode, monitoringplan, monfirstyear, monfinalyear, subsidiary, parent, eprtr, callsign, firstyear,lastyear, address, address2, zipcode, city, country, latitude, longitude, mainactivityholder)
    sql = f"""
            insert into Aircrafts (rawCode,holderName,holdercode,aircraftid,eccode,monitoringplan,monitoringfirstyear,monitoringfinalyear,subsidiary,parent,eprtr,callsign,firstyear,finalyear,address1,address2,zipcode,city,country,latitude,longitude,mainactivity,status)
            values {attributes}
            """
    execute_query(connection, sql)

def addholder(connection,attributes):
    sql = f"""
            insert into holders (rawCode,holdername,companyno,legalid,address,address2,zipcode,city,country,tel,tel2,email)
            values {attributes}
            """
    execute_query(connection, sql)

def addrow(connection, attributes, table, columns):
    sql = f"""
    insert into {table}(id,accname,name,status,address,zipcode,city,country,registry,typeofacc)
    values {attributes}
    """
    execute_query(connection, sql)

def addcountry(connection, attributes, table, columns):
    sql = f"""
    insert into {table}(eu_abbr2L,name,onoma,abbr2L,abbr3L,EU,euro,EFTA,continent)
    values {attributes}
    """
    execute_query(connection, sql)

def countriestable(connection):
    url='https://www.iban.com/country-codes'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("td")
    names = [item.string for item in results if results.index(item)%4==0]
    abb2 = [item.string for item in results if (results.index(item)-1)%4==0]
    #print(abb2)
    abb3 = [item.string for item in results if (results.index(item) -2) % 4 == 0]
    ignite(connection,"eu_ets")
    sql='select * from countries'
    cursor = connection.cursor()
    cursor.execute(sql)
    oldcountries = cursor.fetchall()
    print("oldcountries",oldcountries)
    print(len(oldcountries))
    oldabbr2=[item[3] for item in oldcountries]
    print("oldabbr2",oldabbr2)
    diff=[item for item in oldabbr2 if item not in abb2]
    revdiff=[item for item in abb2 if item not in oldabbr2]
    print("these exist in the old but non in the new","\n",diff,"\n","the reverse",revdiff)
    newcountries=[]
    for abbr in abb2:
        if abbr=="GB":
            print("weinher")
            continue
        #print(abbr)
        if abbr in oldabbr2:
            #print(abbr)
            tem=oldabbr2.index(abbr)
            temp=oldcountries[tem]
            obj=(temp[0],temp[1],temp[2],temp[3],abb3[abb2.index(abbr)],temp[5],temp[6],temp[7],temp[8])
            newcountries.append(obj)
    print("new",newcountries)
    #print([item for item in [item[0] for item in oldcountries] if item not in abb2])
    url='https://ec.europa.eu/clima/ets/account.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("option",attrs={'class':'formOptionListMedium'})
    clima=[item['value'] for item in results if len(item['value'])==2]
    clima2=[item.string for item in results if len(item['value'])==2]
    print("clima",clima)
    print("clima2", clima2)
    print("discrepancies",[item for item in clima if item not in abb2])
    nonstarters=[item for item in clima if item not in [item2[3] for item2 in newcountries]]
    print(len(newcountries))
    #print(nonstarters)
    ni = ('XI','Northern Ireland','Βόρεια Ιρλανδία','XI',None, 1,1,0,'Europe')
    eu = ('EU','European Union','Ευρωπαϊκή Ένωση','EU',None,None,None,None,"Europe")
    un = ('UN','United Nations','Ηνωμένα Έθνη','UN',None,None,None,None,None)
    uk = ('GB','United Kingdom','Ηνωμένο Βασίλειο','GB','GBR',1,0,1,'Europe')
    gr = ('GR','Greece','Ελλάδα','GR','GRC',1,1,1,'Europe')
    one=sorted(oldcountries[1:], key=lambda x: x[0])
    two = sorted(oldcountries[1:], key=lambda x: x[3])
    #one=oldcountries[1:].sort(key = lambda x: x[0])
    #two=oldcountries[1:].sort(key = lambda x: x[3])
    newcountries=[item for item in newcountries if item[1]!="Greece"]
    final=sorted(newcountries+[eu]+[un]+[ni]+[uk]+[gr],key=lambda x:x[0])
    final=[oldcountries[0]]+final
    print(final)
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
    """url = 'https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("span", class_="monospaced")
    #print([item.string for item in results])
    iso2 = [item.string for item in results if results.index(item) % 3 == 0]
    iso3 = [item.string for item in results if (results.index(item)-1) % 3 == 0]
    #print(len(iso2),len(iso3))
    results = soup.find_all("a",attrs={'href'!=""})
    print(len(results))
    print([item.string for item in results])"""

# Press the green button in the gutter to run the script.
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
    ignite(connection,"storage")
    countrydic = getcountries(connection)
    countrydic['Korea, Republic Of'] = countrydic['Korea, Republic of']
    countrydic['Moldova'] = countrydic['Moldova, Republic of']
    #holderurl = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={pageno}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
    """url = 'https://ec.europa.eu/clima/ets/ohaDetails.do?accountID=91955&action=all&languageCode=en&returnURL=installationName%3D%26accountHolder%3D%26search%3DSearch%26permitIdentifier%3D%26form%3Doha%26searchType%3Doha%26currentSortSettings%3D%26mainActivityType%3D-1%26installationIdentifier%3D%26account.registryCodes%3DGR%26languageCode%3Den&registryCode=GR'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("span",class_ ="classictext")
    print(results[2].text[7:-7])"""
    # print(len(results))
    """response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())
    soup.findAll('a')"""
    #accounts()
    # create_table(connection,"accounts")
    # create_db_connection('localhost', 'root', '', 'storage')
    #holderspage()
    #holders,accounts=holdercontroller()
    #print(accounts)
    #countriestable(connection)
    holdercontroller(['BE'],[i for i in range(27)])
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



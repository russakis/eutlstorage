import requests
#import urllib.request
from bs4 import BeautifulSoup
#import re
from main import ignite,execute_query,create_server_connection,createcountrydic,cleanitem
#from accounts import indaccount,accountaddition,holderaddition,addaccount,addholder
import time
import itertools

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
    if temp2[0]=="NULL":temp2[0]="Undefined Account Type"
    if len(someresults)==20:
        specs = (nickname,accname,id,acctype,country,accstatus,accopening,accclosing,commitment)=(name,temp2[10],temp2[2],temp2[0],countrydic[temp2[1]],temp2[4],temp2[5],temp2[6],temp2[7])
        holderspecs = (holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[8],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18],temp2[19])
    else:
        specs = (nickname, accname,id, acctype, country, accstatus, accopening, accclosing,commitment) = (name, temp2[9],temp2[2], temp2[0], countrydic[temp2[1]], temp2[4], temp2[5], temp2[6],"NULL")
        holderspecs = (holdername,compno,legalid,address,address2,zipcode,city,registry,tel1,tel2,email)=(temp2[3],temp2[7],temp2[10],temp2[11],temp2[12],temp2[13],temp2[14],temp2[15],temp2[16],temp2[17],temp2[18])
    return holderspecs,specs,acctype

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

def addholder(connection,attributes):
    sql = f"""
        INSERT IGNORE INTO Holders
        (rawCode,holdername,companyno,legalid,address,address2,zipcode,city,country,tel,tel2,email)
        VALUES {attributes};"""
    execute_query(connection, sql)

def addaccount(connection,attributes,extra):
    for i in range(len(extra)):
        if extra[i]!="NULL":extra[i]=f"\'{extra[i]}\'"
    sql = f"""
        INSERT IGNORE INTO Accounts
        (rawCode,holdercode, alias, accname, id, typeofaccount, country, status, accopening, accclosing,commitmentperiod)
        VALUES {attributes};"""
    execute_query(connection, sql)

def accountcontroller(url):
    result, instresult, acctype = indaccount(url)
    code=holderaddition(result)
    accountaddition(instresult,code)


def extractaccdetails(url):
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    holdername = [cleanitem(item.text) for item in temp][3]
    return holdername

def transcontroller(countrypairs,pagestosearch):
    accounts=[]
    holders=[]
    for countrypair in countrypairs:#countries[21:22]:
        try:
            pageno=0
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            while True:
                try:
                    url = f'https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry={countrypair[0]}&destinationRegistry={countrypair[1]}&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                    response = requests.get(url)
                except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
                    print("Found an exception")
                    continue
                break
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("input", attrs={'name': 'resultList.lastPageNumber',
                                                 'type': 'text'})  # ,type="text", name= "resultList.lastPageNumber")
            # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
            pages = temp[0]['value']
            print(countrypair, pages)
            pages = [i for i in range(int(pages))]
            if pagestosearch != [] and len(pagestosearch) < len(pages):
                pages = pagestosearch
            for pageno in pages:
                print(pageno+1,"/",pages[-1]+1)
                url = f'https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry={countrypair[0]}&destinationRegistry={countrypair[1]}&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
                transactions(url)
        except IndexError:
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&search=Search&searchType=oha&currentSortSettings='
            url = f'https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry={countrypair[0]}&destinationRegistry={countrypair[1]}&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings='
            transactions(url)
    return (holders,accounts)

def transactions(url):
    starttime=time.time()
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    results = [cleanitem(item.string) for item in temp]
    temp = soup.find_all("a", attrs={'class': 'listlink'})
    if len(temp)!=0:
        links = [startingurl+i["href"][11:] for i in temp][1:]
        for i in range(len(results)):
            if i%15==4 or i%15==9:
                results[i]=countrydic[results[i]]
        transactions=[]
        for i in range(len(results)//15):
            rowlen=15#len(results)//20
            transactions.append([results[rowlen*i+j] for j in range(rowlen)])
        transrows=[]
        transdetails=[]
        for row in range(len(transactions)):
            details,acclinks,aliases = transactiondetails(links[row])
            transdetails.append(details)
            if transactions[row][6]=="NULL":
                transactions[row][6]=aliases[0]
                transactions[row][8]=extractaccdetails(acclinks[0])
            if transactions[row][11]=="NULL":
                transactions[row][11]=aliases[1]
                transactions[row][13]=extractaccdetails(acclinks[1])
            wanted = transactions[row]
            wantedstr = ""
            for element in wanted:
                element=element.replace("\"","\\\"")
                element=element.replace("\'","\\\'")
                if element == "NULL" or element.isnumeric():
                    wantedstr += f"{element},"
                else:
                    wantedstr += "\'" + element + "\',"
            wantedstr = "(" + wantedstr[:-1] + ")"
            if wantedstr!="()":
                "dsf"
                #print(wantedstr)
            transrows.append(wantedstr)
        for i in range(len(transrows)):
            row = transactions[i]
            if row[6]=='NULL':
                print("youse an idiot")
            addtransaction(transrows[i])
            #transactiondetails(links[i])
        for details in transdetails:
            for detail in details:
                adddetails(detail)
    print(time.time()-starttime)
    return transactions

def transactiondetails(url):
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break
    temp = soup.find_all("span", attrs={'class': 'classictext'})
    normalfields=[cleanitem(item.string) for item in temp]
    temp2 = soup.find_all("span", attrs={'class': 'resultlink'})
    linkfields = [cleanitem(item.string) for item in temp2]
    temp22 = soup.find_all("a", attrs={'class': 'resultlink'})
    links = [item["href"] for item in temp22]
    urls=[startingurl + item[11:] for item in links[:2]]
    for url in urls:
        accountcontroller(url)
    temp3 = soup.find_all("input", attrs={'class': 'formTextboxDisabled'})
    upperfields = [item["value"] for item in temp3]
    rows=[]
    for i in range((len(temp)+len(temp2))//12):
        rows.append(upperfields+[normalfields[j] for j in range(10*i,10*i+4)]+[linkfields[i*2]]+[normalfields[i*10 +4]]+[linkfields[i*2+1]]+[normalfields[j] for j in range(10*i+5,10*i+10)])
    return rows,[startingurl+ item[11:] for item in links[:2]],linkfields[:2]
    for row in rows:
        adddetails(row)

def adddetails(row):
    wanted = row
    wantedstr = ""
    for element in wanted:
        element=element.replace("\"","\\\"")
        element=element.replace("\'","\\\'")
        if element == "NULL" or element.isnumeric():
            wantedstr += f"{element},"
        else:
            wantedstr += "\'" + element + "\',"
    wantedstr = "(" + wantedstr[:-1] + ")"
    sql=f"""INSERT INTO TransactionDetails (transid,transdate,transtype,status,originatingregistry,unittype,nbofunits,originalcommitment,transferringaccount,transferringid,acquiringaccount,acquiringid,lulucf,projectid,track,expirydate)
            VALUES {wantedstr}
            """
    execute_query(connection,sql)

def addtransaction(row):
    #(transid,trantype,transdate,status,transferringregistry,transferringacctype,transferringaccname,transferringid,transferringaccholder,acquiringregistry,acquiringtype,acquiringaccname,acquiringid,acquiringaccholder,nbofunits)=row
    global connection
    attributes=row
    """attributes = ""
    for element in row:
        if element == "NULL" or element.isnumeric():
            attributes += f"{element},"
        else:
            attributes += "\"" + element + "\","
    attributes = "(" + attributes[:-1] + ")"
    """
    sql = f"""
                INSERT INTO Transactions (transid,trantype,transdate,status,transferringregistry,transferringacctype,transferringaccname,transferringid,transferringaccholder,acquiringregistry,acquiringtype,acquiringaccname,acquiringid,acquiringaccholder,nbofunits)
                VALUES {attributes};
                """
    execute_query(connection, sql)
    return attributes

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    pageno = 0
    holdercounter = 1
    accountcounter = 1
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "EUTL")
    countrydic = createcountrydic(connection)
    triedandtrue = []
    # for abb in abbrs:
    #    url=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={abb}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB']
    combs = list(itertools.product(*[countries,countries]))
    print(combs)
    #transcontroller([combs[170]],[i for i in range(350,687)])
    """for comb in combs:
        print("combination pair",comb)
        start=time.time()
        transcontroller([comb],[])
        end=time.time()-start
        print(end, " seconds")"""
    transcontroller([combs[13]], [])
    #url='https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=GR&destinationRegistry=GR&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber=232&nextList=Next%3E'
    #transactions(url)


import requests
#import urllib.request
from bs4 import BeautifulSoup
#import re
#from accounts import indaccount,accountaddition,holderaddition,addaccount,addholder
import time
import itertools
from utilityfuncs import *
from accounts import addaccount,addholder,indaccount,holderaddition,accountaddition


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
        #links = [startingurl+i["href"][11:] for i in temp][1:] #the hyperlinks for the transaction details
        links = [i["href"] for i in temp[1:]]
        for i in range(len(results)):#here we changing the countries to their 2letter-abbreviation
            if i%15==4 or i%15==9:
                results[i]=countrydic[results[i]]
        transactions=[] #we store the transactions found in the page we explore
        for i in range(len(results)//15):
            rowlen=15#len(results)//20
            transactions.append([results[rowlen*i+j] for j in range(rowlen)]) #they are stored
        transrows=[]
        transdetails=[]
        alllinks=[]
        for row in range(len(transactions)):
            details,acclinks,aliases = transactiondetails(links[row])
            transdetails.append(details)
            alllinks.append(acclinks)
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
            addtransaction(transrows[i],alllinks[i])
            #transactiondetails(links[i])
        for details in transdetails:
            for detail in details:
                "asdf"
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
    linkfields = [cleanitem(item.string) for item in temp2]#the names of the accounts
    temp22 = soup.find_all("a", attrs={'class': 'resultlink'})
    links = [item["href"] for item in temp22]#all the links of the page
    urls=[item for item in links[:2]] #the first two links of the page where the two links we care about are
    #for url in urls:
    #    accountcontroller(url)
    temp3 = soup.find_all("input", attrs={'class': 'formTextboxDisabled'})
    upperfields = [item["value"] for item in temp3]
    rows=[]
    for i in range((len(temp)+len(temp2))//12):
        rows.append(upperfields+[normalfields[j] for j in range(10*i,10*i+4)]+[linkfields[i*2]]+[normalfields[i*10 +4]]+[linkfields[i*2+1]]+[normalfields[j] for j in range(10*i+5,10*i+10)])
    return rows,urls,linkfields[:2]
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

def addtransaction(row,links):
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
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        connection.commit()
        print("Query successful")
    except Error as err:
        er = f'{err}'
        if er.split(":")[0]=="1452 (23000)":
            print("Error 1452: Not registered account, going to register it now and retry")
            for link in links:
                result, instresult, acctype = indaccount(link)
                code = holderaddition(connection,result)
                accountaddition(connection,list(instresult.keys()), list(instresult.values()),code)
            addtransaction(row,links)
        else:
            print(f"Error: '{err}'")
            return "ERROR"
    return attributes

def alltransactions(start,end):
    for comb in combs[start:end]:
        start = time.time()
        print("Combination of Countries", comb)
        transcontroller([comb], [])
        thistime = time.time()
        print(f"The combination {comb} took ", thistime - start, " seconds")

if __name__ == '__main__':
    startingurl = 'https://ec.europa.eu/clima/ets'
    pageno = 0
    holdercounter = 1
    accountcounter = 1
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "EUTL")
    #countrydic = createcountrydic(connection)
    triedandtrue = []
    # for abb in abbrs:
    #    url=f'https://ec.europa.eu/clima/ets/account.do?languageCode=en&account.registryCodes={abb}&accountHolder=&search=Search&searchType=account&currentSortSettings=&resultList.currentPageNumber=1'
    # results = soup.find_all("span",class_ ="resultlinksmall",string= "                         Details - All Phases")
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB']
    combs = list(itertools.product(*[countries,countries]))
    print(len(combs))
    print(combs[1088])
    #transcontroller([combs[1088]],[i for i in range(1055,4311)])
    #alltransactions(1079 ,1089)

import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from main import ignite,execute_query,create_server_connection,createcountrydic,cleanitem
import time

def transcontroller(countrypairs,pagestosearch):
    accounts=[]
    holders=[]
    for countrypair in countrypairs:#countries[21:22]:
        try:
            pageno=0
            #url = f'https://ec.europa.eu/clima/ets/oha.do?form=oha&languageCode=en&account.registryCodes={country}&accountHolder=&installationIdentifier=&installationName=&permitIdentifier=&mainActivityType=-1&searchType=oha&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
            while True:
                try:
                    url = f'https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry={countrypair[0]}&destinationRegistry={countrypair[0]}&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber={pageno}&nextList=Next%3E'
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
    while True:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            temp = soup.find_all("span",
                                 attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
            results = [cleanitem(item.string) for item in temp]
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            print("Found an exception")
            continue
        break

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    results = [cleanitem(item.string) for item in temp]
    print(results)
    temp = soup.find_all("a", attrs={'class': 'listlink'})
    links = [startingurl+i["href"][11:] for i in temp][1:]
    print(links)
    print(len(links))
    for i in range(len(results)):
        if i%15==4 or i%15==9:
            results[i]=countrydic[results[i]]
    transactions=[]
    for i in range(20):
        rowlen=len(results)//20
        transactions.append([results[rowlen*i+j] for j in range(rowlen)])
    for row in transactions:
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
        addtransaction(wantedstr)
    for link in links:
        transactiondetails(link)
    return wantedstr

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
    temp3 = soup.find_all("input", attrs={'class': 'formTextboxDisabled'})
    upperfields = [item["value"] for item in temp3]
    rows=[]
    for i in range((len(temp)+len(temp2))//12):
        rows.append(upperfields+[normalfields[j] for j in range(10*i,10*i+4)]+[linkfields[i*2]]+[normalfields[i*10 +4]]+[linkfields[i*2+1]]+[normalfields[j] for j in range(10*i+5,10*i+10)])
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
    ignite(connection, "storage")
    countrydic = createcountrydic(connection)
    triedandtrue = []
    # for abb in abbrs:
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
    countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'EU', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                 'LV', 'LI', 'LT', 'LU', 'MT', 'NL', 'XI', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB']

    #transactions()
    """url='https://ec.europa.eu/clima/ets/transaction.do?languageCode=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("option", attrs={'class':'formOptionList'})
    print(len(temp))
    print([item.string for item in temp][14:24])
    primtransvalues=[item["value"] for item in temp[14:24]]
    print([item.string for item in temp][24:89])
    suptransvalues=[item["value"] for item in temp[24:89]]
"""
    url = 'https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=GR&destinationRegistry=GR&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&currentSortSettings=&resultList.currentPageNumber=0&nextList=Next%3E'
    start=time.time()
    transcontroller([["GR","GR"]],[i for i in range(113,233)])
    end=start-time.time()
    print(end, " seconds")
    #url='https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=AT&destinationRegistry=BE&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings=&resultList.currentPageNumber=1'
    #transactions(url)
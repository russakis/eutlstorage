import requests
import urllib.request
# import time
from bs4 import BeautifulSoup
import re
from main import ignite,execute_query,create_server_connection,createcountrydic,cleanitem
import time

def transactions():
    url='https://ec.europa.eu/clima/ets/transaction.do?languageCode=en&startDate=&endDate=&transactionStatus=4&fromCompletionDate=&toCompletionDate=&transactionID=&transactionType=-1&suppTransactionType=-1&originatingRegistry=EE&destinationRegistry=AT&originatingAccountType=-1&destinationAccountType=-1&originatingAccountIdentifier=&destinationAccountIdentifier=&originatingAccountHolder=&destinationAccountHolder=&search=Search&currentSortSettings='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    temp = soup.find_all("span", attrs={'class': 'classictext'})  # ,type="text", name= "resultList.lastPageNumber")
    results = [cleanitem(item.string) for item in temp]
    for i in range(len(results)):
        if i%15==4 or i%15==9:
            results[i]=countrydic[results[i]]
    transactions=[]
    print(len(results))
    for i in range(20):
        rowlen=len(results)//20
        transactions.append([results[rowlen*i+j] for j in range(rowlen)])
        print(transactions[i])
    for transaction in transactions:
        addtransaction(transaction)

def addtransaction(row):
    (transid,trantype,transdate,status,transferringregistry,transferringacctype,transferringaccname,transferringid,transferringaccholder,acquiringregistry,acquiringtype,acquiringaccname,acquiringid,acquiringaccholder,nbofunits)=row
    global connection

    attributes = ""
    for element in row:
        if element == "NULL" or element.isnumeric():
            attributes += f"{element},"
        else:
            attributes += "\"" + element + "\","
    attributes = "(" + attributes[:-1] + ")"
    sql = f"""
                INSERT INTO Transactions (transid,trantype,transdate,status,transferringregistry,transferringacctype,transferringaccname,transferringid,transferringaccholder,acquiringregistry,acquiringtype,acquiringaccname,acquiringid,acquiringaccholder,nbofunits)
                VALUES {attributes}
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
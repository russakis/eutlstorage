import mysql.connector
from mysql.connector import Error



def cleanitem(item):
    item = item.replace('\n', '')
    item = item.replace('\r', '')
    item = item.replace('\t', '')
    item = item.replace('\xa0', '')
    item = item.replace('\"', '\'')
    item = item.lstrip()
    if item != '':
        return item.rstrip()
    else:
        return "NULL"

def liststringsum(listyboi):
    result=""
    for element in listyboi:
        result+=str(element)+','
    return result[:-1]

def ignite(connection, databasename):  # διαλέγω τη βάση
    sql = (f"USE {databasename}")
    cursor = connection.cursor()
    cursor.execute(sql)
    print(f"connected to {databasename}")

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

def delete_table(connection):
    create_teacher_table = """
    drop table teacher;"""
    connection = create_db_connection("localhost", "root", "", "trial")  # Connect to the Database
    execute_query(connection, create_teacher_table)  # Execute our defined query


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
        return "ERROR"

def addrow(connection,table,columns,attributes):

    sql = f"""
    INSERT INTO {table}({','.join(columns)})
    VALUES ({','.join(attributes)});
    """
    print("sql",sql)
    #execute_query(connection, sql)

def addholder2(connection,columns,attributes):
    wanted = []
    for elem in attributes:
        if elem.isdigit():
            wanted.append(elem)
        else:
            elem = elem.replace("\"", "\\\"")
            elem = elem.replace("\'", "\\\'")
            wanted.append("\'" + elem + "\'")
    sql = f"""
        INSERT INTO Holders
        ({','.join(columns)})
        VALUES ({','.join(wanted)});"""
    execute_query(connection, sql)

def addcompliance(connection,attributes):
    sql= f"""
        INSERT INTO Compliance (id,country,accountkey,phase,year,allocation,verifiedemissions,surrendered,cumsurrendered,cumverifiedemissions,code)
        VALUES {attributes}"""
    execute_query(connection, sql)

#def addaccount(connection,attributes):
 #   sql = f"""
  #      INSERT INTO Accounts (rawCode,holdercode, alias,typeofaccount, accname,id,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
  #      VALUES {attributes}"""
   # co= execute_query(connection, sql)
  #  return co

def addaccount(connection,columns,attributes):
    if len(attributes)<=12:
        extra=[attributes[i] for i in [2,-1,-3,-2]]
    else:
        extra = ["NULL"]*4
    #for i in range(len(extra)):
    #    if extra[i]!="NULL":extra[i]=f"\'{extra[i]}\'"
    wanted = []
    for elem in attributes:
        if elem.isdigit() or elem=="NULL":
            wanted.append(elem)
        else:
            elem = elem.replace("\"", "\\\"")
            elem = elem.replace("\'", "\\\'")
            wanted.append("\'" + elem + "\'")
    updates=[]
    for elem in extra:
        if elem.isdigit() or elem=="NULL":
            updates.append(elem)
        else:
            elem = elem.replace("\"", "\\\"")
            elem = elem.replace("\'", "\\\'")
            updates.append("\'" + elem + "\'")
    extra = updates
    sql = f"""
        INSERT INTO Accounts
        ({','.join(columns)})
        VALUES ({','.join(wanted)})
        ON DUPLICATE KEY UPDATE
        alias={extra[0]},
        commitmentperiod={extra[1]},
        accopening ={extra[2]},
        accclosing = {extra[3]};"""
    execute_query(connection, sql)

def addaircraft(connection, attributes):
    #(airname, airid, eccode, monitoringplan, monfirstyear, monfinalyear, subsidiary, parent, eprtr, callsign, firstyear,lastyear, address, address2, zipcode, city, country, latitude, longitude, mainactivityholder)
    sql = f"""
        INSERT INTO Accounts (rawCode,accname,alias ,holdercode,typeofaccount,id,eccode,monitoringplan,monitoringfirstyear,monitoringfinalyear,subsidiary,parent,eprtr,callsign,firstyear,finalyear,address,address2,zipcode,city,country,latitude,longitude,mainactivity,status)
        VALUES {attributes}
        """
    co=execute_query(connection, sql)
    return co

def addholder(connection,attributes):
    sql = f"""
        INSERT INTO Holders (rawCode,holdername,companyno,legalid,address,address2,zipcode,city,country,tel,tel2,email)
        VALUES {attributes}
        """
    execute_query(connection, sql)



def addcountry(connection, attributes, table, columns):
    sql = f"""
    insert into {table}(eu_abbr2L,name,onoma,abbr2L,abbr3L,EU,euro,EFTA,continent)
    values {attributes}
    """
    execute_query(connection, sql)

def getcountries(connection):
    cursor = connection.cursor()
    sql = "select abbr2L,name from countries"
    cursor.execute(sql)
    result = cursor.fetchall()
    return dict((y,x) for x,y in result)

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
connection=create_server_connection('localhost','root','')
ignite(connection,"EUTL")
countrydic = createcountrydic(connection)
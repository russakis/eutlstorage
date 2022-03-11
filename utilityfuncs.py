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

def addcompliance(connection,attributes):
    sql= f"""
        INSERT INTO Compliance (id,country,accountkey,phase,year,allocation,verifiedemissions,surrendered,cumsurrendered,cumverifiedemissions,code)
        VALUES {attributes}"""
    execute_query(connection, sql)

def addaccount(connection,attributes):
    sql = f"""
        INSERT INTO Accounts (rawCode,holdercode, alias,typeofaccount, accname,id,permitid,permitentry,permitexpiry,subsidiary,parent,eprtr,firstyear,finalyear,address,address2,zipcode,city,country,latitude, longitude,mainactivity,status)
        VALUES {attributes}"""
    co= execute_query(connection, sql)
    return co

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
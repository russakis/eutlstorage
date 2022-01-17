from main import execute_query,create_server_connection,ignite
def createholders():
    connection=create_server_connection('localhost','root','')
    ignite(connection,"storage")
    sql = """CREATE TABLE `Holders` (
  `rawCode` int PRIMARY KEY,
  `holderName` varchar(255),
  `companyno` varchar(255) UNIQUE,
  `legalid` varchar(30),
  `address` varchar(100),
  `address2` varchar(100),
  `zipcode` varchar(50),
  `city` varchar(100),
  `country` char(2),
  `tel` varchar(20),
  `tel2` varchar(20),
  `email` varchar(50)
);"""
    execute_query(connection,sql)
def createaccounts():
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "storage")
    sql = """CREATE TABLE `Accounts` (
  `rawCode` int PRIMARY KEY,
  `holdercode` int,
  `nickname` varchar(50),
  `installationname` varchar(100),
  `installationid` varchar(20),
  `permitid` varchar(25),
  `permitentry` date,
  `permitexpiry` date,
  `subsidiary` varchar(100),
  `parent` varchar(200),
  `eprtr` varchar(100),
  `firstyear` smallint,
  `finalyear` smallint,
  `address` varchar(100),
  `address2` varchar(100),
  `zipcode` varchar(50),
  `city` varchar(100),
  `country` char(2),
  `latitude` varchar(100),
  `longitude` varchar(100),
  `mainactivity` tinyint,
  `status` enum('open','closed','Closure Pending')
);"""
    execute_query(connection, sql)
def createaircrafts():
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "storage")
    sql = """CREATE TABLE `Aircrafts` (
  `rawCode` int PRIMARY KEY,
  `holderName` varchar(100),
  `holdercode` int,
  `aircraftid` int,
  `eccode` varchar(20),
  `monitoringplan` varchar(100),
  `monitoringfirstyear` date,
  `monitoringfinalyear` date,
  `subsidiary` varchar(100),
  `parent` varchar(100),
  `eprtr` varchar(100),
  `callsign` varchar(20),
  `firstyear` smallint,
  `finalyear` smallint,
  `address1` varchar(100),
  `address2` varchar(100),
  `zipcode` varchar(20),
  `city` varchar(100),
  `country` char(2),
  `latitude` varchar(100),
  `longitude` varchar(100),
  `mainactivity` tinyint,
  `status` enum('open','closed','Closure Pending')
);"""
    execute_query(connection, sql)

def createmainactivity():
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "storage")
    sql = """CREATE TABLE `MainActivityType` (
  `kwdikos` tinyint PRIMARY KEY,
  `onoma` varchar(100)
);"""
    execute_query(connection, sql)

def createcountries():
    connection = create_server_connection('localhost', 'root', '')
    ignite(connection, "storage")
    sql = """CREATE TABLE `Countries` (
  `eu_abbr2L` char(2) PRIMARY KEY,
  `name` varchar(52),
  `onoma` varchar(52),
  `abbr2L` char(2),
  `abbr3l` char(3),
  `EU` tinyint(1),
  `euro` tinyint(1),
  `EFTA` tinyint(1),
  `continent` enum('Europe','Asia','Africa','America','Oceania')
);"""
    execute_query(connection, sql)
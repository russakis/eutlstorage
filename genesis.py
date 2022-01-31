from main import execute_query,create_server_connection,ignite

def createholders():
    sql = """CREATE TABLE `Holders` (
  `rawCode` int PRIMARY KEY,
  `holderName` varchar(255) UNIQUE,
  `companyno` varchar(255),
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
def createaccountspage():
    sql = """CREATE TABLE `AccountsPage` (
  `rawCode` int PRIMARY KEY,
  `holdercode` int,
  `alias` varchar(200),
  `accountname` varchar(100),
  `accountid` varchar(20),
  `acctype` varchar(100),
  `country` char(2),
  `status` enum('open','closed','Closure Pending'),
  `openingdate` date,
  `closingdate` date);
  """
    execute_query(connection,sql)
def createaccounts():
    sql = """CREATE TABLE `Accounts` (
  `rawCode` int PRIMARY KEY,
  `holdercode` int,
  `alias` varchar(200),
  `typeofaccount` varchar(100),
  `accname` varchar(100),
  `id` varchar(20),
  `permitid` varchar(50),
  `permitentry` date,
  `permitexpiry` date,
  `subsidiary` varchar(255),
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
  `status` enum('open','closed','Closure Pending'),
  `accopening` date,
  `accclosing` date,
  `commitmentperiod` varchar(100),
  `eccode` varchar(20),
  `callsign` varchar(20),
  `monitoringplan` varchar(100),
  `monitoringfirstyear` date,
  `monitoringfinalyear` date
  
);"""
    execute_query(connection, sql)
def createaircrafts():
    sql = """CREATE TABLE `Aircrafts` (
  `rawCode` int PRIMARY KEY,
  `aircraftName` varchar(100),
  `alias` varchar(200),
  `holdercode` int,
  `aircraftid` int,
  `eccode` varchar(20),
  `monitoringplan` varchar(100),
  `monitoringfirstyear` date,
  `monitoringfinalyear` date,
  `subsidiary` varchar(200),
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
    sql = """CREATE TABLE `MainActivityType` (
  `kwdikos` tinyint PRIMARY KEY,
  `onoma` varchar(100)
);"""
    execute_query(connection, sql)

def createcountries():
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


def Transactions():
    sql = """CREATE TABLE `Transactions` (
  `transid` varchar(20) PRIMARY KEY,
  `trantype` varchar(20),
  `transdate` date,
  `status` enum('Completed'),
  `transferringregistry` char(2),
  `transferringacctype` varchar(20),
  `transferringaccname` varchar(200),
  `transferringid` int,
  `transferringaccholder` varchar(200),
  `acquiringregistry` char(2),
  `acquiringtype` varchar(20),
  `acquiringaccname` varchar(200),
  `acquiringid` int,
  `acquiringaccholder` varchar(200),
  `nbofunits` int
);"""
    execute_query(connection, sql)


def TransactionTypes():
    sql="""CREATE TABLE `TransactionTypes` (
  `code` varchar(6) PRIMARY KEY,
  `transferringType` smallint,
  `acquiringType` smallint,
  `sholio` text
);
    """
    execute_query(connection,sql)

def TransactionDetails():
    sql="""CREATE TABLE `TransactionDetails` (
  `transid` varchar(20) PRIMARY KEY,
  `transtype` varchar(20),
  `transdate` date,
  `status` varchar(15),
  `originatingregistry` varchar(2),
  `unittype` varchar(100),
  `nbofunits` int,
  `originalcommitment` int,
  `transferringaccount` varchar(200),
  `transferringid` int,
  `acquiringaccount` varchar(200),
  `acquiringid` int,
  `lulucf` varchar(200),
  `projectid` int,
  `track` varchar(200),
  `expirydate` date
);"""
    execute_query(connection,sql)

def alters():
    sql ="""
ALTER TABLE `Accounts` ADD FOREIGN KEY (`holdercode`) REFERENCES `Holders` (`rawCode`);

ALTER TABLE `Accounts` ADD FOREIGN KEY (`mainactivity`) REFERENCES `MainActivityType` (`kwdikos`);

ALTER TABLE `Accounts` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`eu_abbr2L`);

ALTER TABLE `Holders` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`eu_abbr2L`);

ALTER TABLE Accounts ADD CONSTRAINT UniqueInstallation UNIQUE (country, id);

ALTER TABLE Accounts ADD CONSTRAINT UniqueAccount UNIQUE (alias, holdercode, id, typeofaccount);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringregistry`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringregistry`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccholder`) REFERENCES `Holders` (`holderName`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccholder`) REFERENCES `Holders` (`holderName`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`trantype`) REFERENCES `TransactionTypes` (`code`)

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccname`) REFERENCES `Accounts` (`alias`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccname`) REFERENCES `Accounts` (`alias`);

ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transid`) REFERENCES `Transactions` (`transid`);

ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transtype`) REFERENCES `TransactionTypes` (`transferringType`);

;
"""

    sql2="""ALTER TABLE Aircrafts ADD CONSTRAINT uqaircraft UNIQUE KEY(country,aircraftid);

ALTER TABLE AccountsPage ADD CONSTRAINT uqaccount UNIQUE KEY(alias,acctype);

ALTER TABLE `Aircrafts` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`eu_abbr2L`);

ALTER TABLE `Aircrafts` ADD FOREIGN KEY (`holdercode`) REFERENCES `Holders` (`rawCode`);

ALTER TABLE `Aircrafts` ADD FOREIGN KEY (`mainactivity`) REFERENCES `MainActivityType` (`kwdikos`);

ALTER TABLE `AccountsPage` ADD FOREIGN KEY (`holdercode`) REFERENCES `Holders` (`rawCode`);

ALTER TABLE `AccountsPage` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`eu_abbr2L`);


"""
    execute_query(connection, sql)


connection=create_server_connection('localhost','root','')
ignite(connection, "storage")
#createholders()
#createaccounts()
#createaircrafts()
#createaccountspage()
#TransactionTypes()
TransactionDetails()
#Transactions()
#alters()
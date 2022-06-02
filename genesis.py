from main import execute_query,create_server_connection,ignite

def createdb():
    sql="""CREATE DATABASE EUTL;"""
    execute_query(connection,sql)

def createholders():
    sql = """CREATE TABLE `Holders` (
  `rawCode` int PRIMARY KEY AUTO_INCREMENT,
  `holderName` varchar(255) UNIQUE,
  `companyno` varchar(255),
  `legalid` varchar(30),
  `address` varchar(200),
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
    sql = """CREATE TABLE `Accounts` (
  `rawCode` int PRIMARY KEY AUTO_INCREMENT,
  `holdercode` int,
  `alias` varchar(200),
  `typeofaccount` varchar(100),
  `accname` varchar(100),
  `id` varchar(30),
  `permitid` varchar(50),
  `permitentry` date,
  `permitexpiry` date,
  `subsidiary` varchar(300),
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
  `transferringid` bigint,
  `transferringaccholder` varchar(200),
  `acquiringregistry` char(2),
  `acquiringtype` varchar(20),
  `acquiringaccname` varchar(200),
  `acquiringid` bigint,
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

def ComplianceExplanation():
    sql ="""CREATE TABLE `ComplianceExplanation`(
    `code` char(2) PRIMARY KEY,
    `explanation` varchar(200)
    )"""
    execute_query(connection,sql)

def TransactionDetails():
    sql="""CREATE TABLE `TransactionDetails` (
  `transid` varchar(20),
  `transtype` varchar(20),
  `transdate` date,
  `status` varchar(15),
  `originatingregistry` varchar(2),
  `unittype` varchar(200),
  `nbofunits` int,
  `originalcommitment` int,
  `transferringaccount` varchar(200),
  `transferringid` bigint,
  `acquiringaccount` varchar(200),
  `acquiringid` bigint,
  `lulucf` varchar(200),
  `projectid` int,
  `track` varchar(200),
  `expirydate` date
    );"""
    execute_query(connection,sql)

def createcompliance():
    sql="""
    CREATE TABLE `Compliance` (
  `id` int,
  `country` varchar(2),
  `accountkey` int,
  `phase` varchar(20),
  `year` int,
  `allocation` varchar(40),
  `verifiedemissions` varchar(40),
  `surrendered` varchar(40),
  `cumsurrendered` varchar(40),
  `cumverifiedemissions` varchar(40),
  `code` varchar(5)
    );"""
    execute_query(connection,sql)

def createcompliancestar():
    sql = """CREATE TABLE 'ComplianceStar'(
    `id` int,
    `country` varchar(2),
    `accountkey` int,
    `phase` varchar(20),
    `year` int,
    `allocation` varchar(40)
    );"""
    execute_query(connection,sql)

def alters():
    sql ="""ALTER TABLE `Accounts` ADD INDEX `aliasindex` (`alias`);

ALTER TABLE `Accounts` ADD FOREIGN KEY (`holdercode`) REFERENCES `Holders` (`rawCode`);

ALTER TABLE `Accounts` ADD FOREIGN KEY (`mainactivity`) REFERENCES `MainActivityType` (`kwdikos`);

ALTER TABLE `Accounts` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Holders` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringregistry`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringregistry`) REFERENCES `Countries` (`abbr2L`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccholder`) REFERENCES `Holders` (`holderName`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccholder`) REFERENCES `Holders` (`holderName`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`trantype`) REFERENCES `TransactionTypes` (`code`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccname`) REFERENCES `Accounts` (`alias`);

ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccname`) REFERENCES `Accounts` (`alias`);

ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transid`) REFERENCES `Transactions` (`transid`);

ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transtype`) REFERENCES `TransactionTypes` (`code`);

ALTER TABLE `Accounts` ADD CONSTRAINT `Unique_Account` UNIQUE (`typeofaccount`,`accname`, `id`,`alias`);

ALTER TABLE `Compliance` ADD CONSTRAINT `Unique_Compliance` UNIQUE (`id`, `country`, `year`);
"""
    cursor = connection.cursor()
    cursor.execute(sql,multi=True)
    connection.commit()

def testing(indices):
    sql = [ "ALTER TABLE `Countries` ADD INDEX `country` (`abbr2L`);",
            "ALTER TABLE `Accounts` ADD CONSTRAINT `Unique_Account` UNIQUE (`typeofaccount`,`accname`,`alias`);",
            "ALTER TABLE `Accounts` ADD FOREIGN KEY (`holdercode`) REFERENCES `Holders` (`rawCode`);",
            "ALTER TABLE `Accounts` ADD FOREIGN KEY (`mainactivity`) REFERENCES `MainActivityType` (`kwdikos`);",
            "ALTER TABLE `Accounts` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`abbr2L`);",
            "ALTER TABLE `Accounts` ADD INDEX `aliasindex` (`alias`);",
            "ALTER TABLE `Holders` ADD FOREIGN KEY (`country`) REFERENCES `Countries` (`abbr2L`);",
            "ALTER TABLE `Holders` ADD CONSTRAINT `Unique_Holder` UNIQUE (`holderName`);",
            "ALTER TABLE `Compliance` ADD CONSTRAINT `Unique_Compliance` UNIQUE (`id`, `country`, `year`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringregistry`) REFERENCES `Countries` (`abbr2L`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringregistry`) REFERENCES `Countries` (`abbr2L`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccholder`) REFERENCES `Holders` (`holderName`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccholder`) REFERENCES `Holders` (`holderName`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`trantype`) REFERENCES `TransactionTypes` (`code`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`transferringaccname`) REFERENCES `Accounts` (`alias`);",
           "ALTER TABLE `Transactions` ADD FOREIGN KEY (`acquiringaccname`) REFERENCES `Accounts` (`alias`);",
           "ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transid`) REFERENCES `Transactions` (`transid`);",
           "ALTER TABLE `TransactionDetails` ADD FOREIGN KEY (`transtype`) REFERENCES `TransactionTypes` (`code`);"
          ]
    if indices=="":
        for query in sql:
            execute_query(connection, query)
    else:
        for query in sql[indices[0]:indices[1]]:
            execute_query(connection,query)

def lettherebelight():
    createdb()
    ignite(connection,"EUTL")
    createaccounts()
    createholders()
    createcompliance()
    #createcompliancestar()
    createmainactivity()
    createcountries()
    Transactions()
    TransactionDetails()
    TransactionTypes()

connection=create_server_connection('localhost','root','')
"""ignite(connection, "storage")
#createholders()
#createaccounts()
TransactionTypes()
TransactionDetails()
Transactions()
#createcompliance()
#alters()
testing([5,14])
"""
lettherebelight()
ignite(connection, "EUTL")

testing("")
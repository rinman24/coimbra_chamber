"""Docstring."""

import os
import mysql.connector as conn
from mysql.connector import errorcode

def connect_sqldb():
    """Use connect constructor to connect to a MySQL server.

    Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and MySqlDataBase to
    connect to a MySQL server. The function returns both the connection object as well as the cursor
    object. If these variables are not already available use, for example: 
    
    $ export MySqlUserName=user
    
    in the shell.

    Returns
    -------
    cnx : MySQLConnection
    Returns the MySQL connection object
    """
    config = {'user': os.environ['MySqlUserName'],
              'password': os.environ['MySqlCredentials'],
              'host': os.environ['MySqlHost'],
              'database': os.environ['MySqlDataBase']}
    try:
        cnx = conn.connect(**config)
    except conn.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return cnx

def create_tables(cur, tables):
    """Use a MySQL cursor object and a list names and DDL queries to create tables in the database.

    Uses a list of tuples where the 0 index is the name of the table and the 1 index is a string of
    MySQL DDL used to create the table. A list is required so that the DDL can be executed in order
    so that foreign key constraint errors do not occur.
    
    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    tables : list
        List of table names and DDL query language. For example:
        [('UnitTest',
            "CREATE TABLE UnitTest ("
            "    UnitTestID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
            "    Number DECIMAL(5,2) NULL,"
            "    String VARCHAR(30) NULL,"
            "  PRIMARY KEY (`UnitTestID`)"
            ");"))]
    """
    for table in tables:
        name, ddl = table
        try:
            #print('\tCreating table {}: '.format(name), end='')
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('already exists.')
            else:
                print(err.msg)
        else:
            print("OK")

def insert_dml(table, row_data):
    """Use a table name and dictionay to return a MySQL insert DML query.

    Use the name of the table and a dictionary called row_data, where the keys are attribute names
    and the values are row data, to build and return a MySQL DML INSERT query. Please note that all
    the values in the row_data dictionary should be string types.

    Parameters
    ----------
    table : string
        Name of the MySQL database table to insert into.
    row_data : dict of strings
        Set of values to insert into the table. Keys should be column names and values should be the
        value to insert. 
        **Note: all values should be type string.**
    """
    query = (
        "INSERT INTO " + table + " "
        "    (" + ', '.join(row_data.keys()) + ")"
        "  VALUES"
        "    ('" + "', '".join(row_data.values()) + "');")
    return query

#def last_insert_id(cur):
    """
    THIS IS GETTING DEPRECIATED IN FAVOR OF
        id = cursor.lastrowid
    """
    #cur.execute("SELECT LAST_INSERT_ID();")
    #return cur.fetchone()[0]

def setting_exists(cur, setting):
    """Use the cursor and a setting dictionary to check if a setting already exists.

    Uses the setting dictionary where the keys are the columns in the Setting table and the values
    are the string values. The cursor executes a DML select statement and returns the SettingID if
    the setting exists and False if no setting matching the query exists.

    Parameters
    ----------
    cur : MySQLCursor
        Cursor used to interact with the MySQL database.
    setting : dict of strings
        Set of setting values to check for. Keys should be column names from the Setting table and
        values should be the value to insert. 
        **Note: all values should be type string.**
    
    Returns
    -------
    SettingID : int or False
        This is the primary key for the Setting table if the setting already exists. If the setting
        does not exist in the database the function returns False.
    """
    query = (
        "SELECT SettingID FROM Setting"
        "  WHERE"
        "    InitialDewPoint = " + setting['InitialDewPoint'] + " AND"
        "    InitialDuty = " + setting['InitialDuty'] + " AND"
        "    InitialMass = " + setting['InitialMass'] + " AND"
        "    InitialPressure = " + setting['InitialPressure'] + " AND"
        "    InitialTemp = " + setting['InitialTemp'] + " AND"
        "    TimeStep = " + setting['TimeStep'] + ";")
    cur.execute(query)
    result = cur.fetchall()
    if not result:
        return False
    else:
        return result[0][0]

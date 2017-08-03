"""Docstring."""

import os
import mysql.connector as conn
from mysql.connector import errorcode

def connect_sqldb():
    """Use connect constructor to connect to a MySQL server.

    Description: Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and
    MySqlDataBase to connect to a MySQL server. The function returns both the connection object as well as the cursor object. If these variables are not already available use,
    for example, $ export MySqlUserName=user in the shell.
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
    """Use cur and a list of tuples of names and DDL queries to create tables in the database.

    Description: Uses a list of tuples where the 0 index is the name of the table and the 1 index is
    a string of MySQL DDL used to create the table. A list is required so that the DDL can be
    executed in order so that foreign key constraint errors do not occur.
    
    Positional arguments:
    cur -- mysql.connector.cursor.MySQLCursor
    tables -- list
    """
    for table in tables:
        name, ddl = table
        try:
            #print("\tCreating table {}: ".format(name), end='')
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

def insert_dml(table, row_data):
    """Use a table name and dictionay to return a MySQL insert DML query.

    Description: Use the name of the table and a dictionary called row_data, where the keys are
    attribute names and the values are row data, to build and return a MySQL DML INSERT query.
    Please note that all the values in the row_data dictionary should be string types.

    Positional arguments:
    table -- string
    row_data -- dict of strings
    """
    query = (
        "INSERT INTO " + table + " "
        "    (" + ', '.join(row_data.keys()) + ")"
        "  VALUES"
        "    ('" + "', '".join(row_data.values()) + "');")
    return query

def setting_exists(cur, setting):
    """Use the cursor and a setting dictionary to check if a setting already exists"""
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
    result = cur.fetchall()[0][0]
    if not result:
        return False
    else:
        return result

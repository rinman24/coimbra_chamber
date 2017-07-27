"""Docstring."""

import os
import mysql.connector as conn
from mysql.connector import errorcode

def connect_sqldb():
    """Use connect constructor to connect to a MySQL server.

    Description: Uses environment variables MySqlUserName, MySqlCredentials, MySqlHost, and
    MySqlDataBase to connect to a MySQL server. The function returns both the connection object as well as the cursor object. If these variables are not already available use,
    for example, $ export MySqlUserName=user in the shell.

    Usage:
        >>> cnx, cur = connect_sqldb()
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
    """Use cur and a dictionaty of names and DDL to create tables in the database.

    Description: Uses a dictionaty where the key is the name of the table and the value is a string
    of MySQL DDL used to create the table."""
    for name, ddl in tables.items():
        try:
            print("\nCreating table {}: ".format(name), end='')
            cur.execute(ddl)
        except conn.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

def table_insert(cur, add_row, row_data):
    """Use cur and two DDL lines to add a row of data."""
    try:
        cur.execute(add_row, row_data)
    except conn.Error as err:
        print(err.msg)
    else:
        print('Sucessfully added row.')

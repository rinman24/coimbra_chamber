"""Docstring."""
import sys
import time

import mysql.connector as conn
from mysql.connector import errorcode
import schedule

import const
import sqldb


def build_tables():
    """Checks for and builds tables from const.TABLES in database."""
    cnx = sqldb.connect('test_chamber')
    cur = cnx.cursor()
    sqldb.create_tables(cur, const.TABLES)
    sqldb.add_tube_info(cur)
    cnx.commit()
    cur.close()
    cnx.close()


def job():
    """Writes .tdms files from argument directory to database."""
    print("\nConnecting to MySQL...")
    cnx = sqldb.connect('test_chamber')
    cur = cnx.cursor()
    print("Connected.")
    sqldb.add_input(cur, sys.argv[1])
    print("Disconnecting from MySQL...")
    cnx.commit()
    cur.close()
    cnx.close()
    print("Connection to MySQL closed.")


def execute_job():
    """Calls build_test_tables once and calls job() every day at 23:00."""
    build_tables()
    schedule.every().day.at("23:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    execute_job()

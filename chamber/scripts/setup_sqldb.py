"""
Set up the initial state of the database.

Be sure to only run onece.

The first input from the commad line should be the name of the database to
setup.

Note: The database must already exists, which can be accomplished, for
example, by executing the following line in your MySQL server:

    CREATE SCHEMA <name-of-your-database>;

Once the database is created, this script will create the tables, populate the
'Unit' table and the 'Tube' table. A default tube is entered, which was the
original tube used for experiments at UCSD by Rich Inman.

"""

import sys

import chamber.const as const
from chamber.data import sqldb, ddl, dml


if __name__ == '__main__':
    cnx = sqldb.connect(sys.argv[1])
    print("Sucessfully created a connection to the database")

    cur = cnx.cursor()
    print("Sucessfully created a cursor for the database")
    sqldb.create_tables(cur, ddl.tables)

    print("Populating Units table...")
    cur.execute(dml.add_unit, ddl.units)

    print("Committing changes to Unit table...")
    cnx.commit()

    print("Populating Tube table with initial tube...")
    sqldb.add_tube_info(cur)

    print("Committing changes to Tube table...")
    cnx.commit()

    print("All done, closing connection to server...")
    cur.close()
    cnx.close()
    print("Closed the connection.")

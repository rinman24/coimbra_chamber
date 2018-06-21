"""Docstring. This module sets up the initial state of the database.
Be sure to only run onece."""

import sys

import chamber.const as const
import chamber.sqldb as sqldb

if __name__ == '__main__':
    cnx = sqldb.connect(sys.argv[1])
    print("Sucessfully created a connection to the database")

    cur = cnx.cursor()
    print("Sucessfully created a cursor for the database")
    sqldb.create_tables(cur, const.TABLES)

    print("Populating Units table...")
    cur.execute(const.ADD_UNIT, dict(Duty='Percent', Length='Meter', Mass='Meter',
                                     Power='Watt', Pressure='Pascal', Temperature='Kelvin',
                                     Time='Second'))

    print("Populating Tube table with initial tube...")
    cur.execute(const.ADD_TUBE, dict(DiameterIn=0.03, DiameterOut=0.04, Length='0.06',
                                     Material='Delrin', Mass=0.0873832))

    print("Committing changes to Unit table...")
    cnx.commit()

    print("All done, closing connection to server...")
    cur.close()
    cnx.close()
    print("Closed the connection.")

"""Docstring. This module sets up the initial state of the database.
Be sure to only run onece."""

import sys

import chamber.const as const
from chamber.data import sqldb, ddl


def add_tube(cnx):
    """Add tube to database."""
    attributes = {}
    attributes['DiameterIn'] = input("Enter the inside diameter [m]: ")
    attributes['DiameterOut'] = input("Enter the outside diameter [m]: ")
    attributes['Length'] = input("Enter the inner length [m]: ")
    attributes['Material'] = input("Enter the material: ")
    attributes['Mass'] = input("Enter the mass [kg]: ")

    print("Summary:")
    for key, value in attributes.items():
        print("\t", key+':', value)

    resp = input("Is this correct? [y/n]: ")

    if "y" in resp.lower():
        cur = cnx.cursor()
        print('Successfully created cursor to add tube...')
        print("Submitting to database...")
        add_row_dml = (
            "INSERT INTO Tube (DiameterIn, DiameterOut, Length, Material, Mass) "
            "VALUES (%s, %s, %s, %s, %s);")
        row_data = (attributes['DiameterIn'], attributes['DiameterOut'],
                    attributes['Length'], attributes['Material'],
                    attributes['Mass'])
        sqldb.table_insert(cur, add_row_dml, row_data)
        print("Committing changes to Tube table...")
        cnx.commit()
        print("All done, closing cursor but leaving connection open...")
        cur.close()
    else:
        print("Ok, no changes made to daabase.")


if __name__ == '__main__':
    cnx = sqldb.connect_sqldb(sys.argv[1])
    print("Sucessfully created a connection to the database")

    cur = cnx.cursor()
    print("Sucessfully created a cursor for the database")
    sqldb.create_tables(cur, ddl.tables)

    print("Populating Units table...")
    cur.execute(dml.add_unit, dict(Duty='Percent', Length='Meter', Mass='Meter',
                                     Power='Watt', Pressure='Pascal', Temperature='Kelvin',
                                     Time='Second'))

    print("Committing changes to Unit table...")
    cnx.commit()
    
    print("Populating Tube table with initial tube...")
    add_tube(cnx)

    print("All done, closing connection to server...")
    cur.close()
    cnx.close()
    print("Closed the connection.")

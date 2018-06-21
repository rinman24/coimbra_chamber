"""Docstring. This module adds a tube to the MySQL Database."""
import chamber.sqldb as sqldb


ATTRIBUTES = {}
ATTRIBUTES['DiameterIn'] = input("Enter the inside diameter [m]: ")
ATTRIBUTES['DiameterOut'] = input("Enter the outside diameter [m]: ")
ATTRIBUTES['Length'] = input("Enter the inner length [m]: ")
ATTRIBUTES['Material'] = input("Enter the material: ")
ATTRIBUTES['Mass'] = input("Enter the mass [kg]: ")

print("Summary:")
for key, value in ATTRIBUTES.items():
    print("\t", key+':', value)

ANS = input("Is this correct? [y/n]: ")

if "y" in ANS.lower():
    CNX = sqldb.connect()
    print("Sucessfully created a connection to the database")
    CUR = CNX.cursor()
    print("Sucessfully created a cursor for the database")
    print("Submitting to database...")
    ADD_ROW = (
        "INSERT INTO Tube (DiameterIn, DiameterOut, Length, Material, Mass) "
        "VALUES (%s, %s, %s, %s, %s);")
    ROW_DATA = (ATTRIBUTES['DiameterIn'], ATTRIBUTES['DiameterOut'],
                ATTRIBUTES['Length'], ATTRIBUTES['Material'],
                ATTRIBUTES['Mass'])
    sqldb.table_insert(CUR, ADD_ROW, ROW_DATA)
    print("Committing changes to Unit table...")
    CNX.commit()
    print("All done, closing connection to server...")
    CUR.close()
    CNX.close()
    print("Closed the connection.")
else:
    print("Ok, no changes made to daabase.")

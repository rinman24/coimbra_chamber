"""This script adds a tube to the MySQL Database."""
import sys

from chamber.data import sqldb


def add_tube(database):
    """Add tube to database."""
    # ------------------------------------------------------------------------
    # Get the user input regarding the tube and store it in a dictionary
    attributes = dict(
        DiameterIn=input("Enter the inside diameter [m]: "),
        DiameterOut=input("Enter the outside diameter [m]: "),
        Length=input("Enter the inner length [m]: "),
        Material=input("Enter the material: "),
        Mass=input("Enter the mass [kg]: ")
        )

    # ------------------------------------------------------------------------
    # Notw print a summary and ask the user if it is correct
    print("Summary:")
    for key, value in attributes.items():
        print("\t{0}: {1}".format(key, value))
    resp = input("Is this correct? [y/n]: ")

    # ------------------------------------------------------------------------
    # If user said yes, add the tube to the database
    if "y" in resp.lower():
        cnx = sqldb.connect(database)
        print("Sucessfully created a connection to the database")
        cur = cnx.cursor()
        print("Sucessfully created a cursor for the database")
        print("Submitting to database...")
        add_row = (
            "INSERT INTO Tube (DiameterIn, DiameterOut, Length, Material, Mass) "
            "VALUES (%s, %s, %s, %s, %s);")
        row_data = (attributes['DiameterIn'], attributes['DiameterOut'],
                    attributes['Length'], attributes['Material'],
                    attributes['Mass'])
        cur.execute(add_row, row_data)
        print("Committing changes to Unit table...")
        cnx.commit()
        print("All done, closing connection to server...")
        cur.close()
        cnx.close()
        print("Closed the connection.")
    else:
        print("Ok, no changes made to daabase.")

if __name__ == '__main__':
    add_tube(sys.argv[1])
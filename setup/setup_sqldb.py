"""Docstring. This module sets up the initial state of the database.
Be sure to only run onece."""

import sys

import chamber.const as const
import chamber.sqldb as sqldb


TABLES = []
TABLES.append(('Unit',
               "CREATE TABLE Unit ("
               "    Duty VARCHAR(30) NOT NULL,"
               "    Length VARCHAR(30) NOT NULL,"
               "    Mass VARCHAR(30) NOT NULL,"
               "    Power VARCHAR(30) NOT NULL,"
               "    Pressure VARCHAR(30) NOT NULL,"
               "    Temperature VARCHAR(30) NOT NULL,"
               "    Time VARCHAR(30) NOT NULL"
               ");"))
TABLES.append(('Tube',
               "CREATE TABLE Tube("
               "    TubeID TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,"
               "    DiameterIn DECIMAL(7, 7) NOT NULL,"
               "    DiameterOut DECIMAL(7, 7) NOT NULL,"
               "    Length DECIMAL(4, 4) NOT NULL,"
               "    Material VARCHAR(30) NOT NULL,"
               "    Mass DECIMAL(7, 7) NOT NULL,"
               "  PRIMARY KEY (TubeID)"
               ");"))
TABLES.append(('Setting',
               "CREATE TABLE Setting("
               "    SettingID SERIAL,"
               "    Duty DECIMAL(4, 1) NOT NULL,"
               "    Pressure MEDIUMINT UNSIGNED NOT NULL,"
               "    Temperature DECIMAL(5, 2) NOT NULL,"
               "  PRIMARY KEY (SettingID)"
               ");"))
TABLES.append(('Test',
               "CREATE TABLE Test("
               "    TestID SERIAL,"
               "    Author VARCHAR(30) NOT NULL,"
               "    DateTime DATETIME NOT NULL,"
               "    Description VARCHAR(200) NOT NULL,"
               "    IsMass BIT(1) NOT NULL,"
               "    TimeStep DECIMAL(4, 2) NOT NULL,"
               "    SettingID BIGINT UNSIGNED NOT NULL,"
               "    TubeID TINYINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (TestID),"
               "  FOREIGN KEY (SettingID) REFERENCES Setting(SettingID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT,"
               "  FOREIGN KEY (TubeID) REFERENCES Tube(TubeID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))
TABLES.append(('Observation',
               "CREATE TABLE Observation("
               "    ObservationID SERIAL,"
               "    CapManOk TINYINT(1) NOT NULL,"
               "    DewPoint DECIMAL(5, 2) NOT NULL,"
               "    Duty DECIMAL(4, 1) NOT NULL,"
               "    Idx SMALLINT UNSIGNED NOT NULL,"
               "    Mass DECIMAL(7, 7) NOT NULL,"
               "    OptidewOk TINYINT(1) NOT NULL,"
               "    PowOut DECIMAL(6, 4) NOT NULL,"
               "    PowRef DECIMAL(6, 4) NOT NULL,"
               "    Pressure MEDIUMINT UNSIGNED NOT NULL,"
               "    TestID BIGINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (ObservationID),"
               "  FOREIGN KEY (TestID) REFERENCES Test(TestID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))
TABLES.append(('TempObservation',
               "CREATE TABLE TempObservation("
               "    ObservationID BIGINT UNSIGNED NOT NULL,"
               "    ThermocoupleNum TINYINT(2) UNSIGNED NOT NULL,"
               "    Temperature DECIMAL(5, 2) NOT NULL,"
               "  PRIMARY KEY (ObservationID, ThermocoupleNum),"
               "  FOREIGN KEY (ObservationID) REFERENCES Observation(ObservationID)"
               "    ON UPDATE CASCADE ON DELETE RESTRICT"
               ");"))

UNIT_DATA = {'Duty': 'Percent', 'Length': 'Meter', 'Mass': 'Kilogram',
             'Power': 'Watt', 'Pressure': 'Pascal', 'Temperature': 'Kelvin',
             'Time': 'Second'}

TUBE_DATA = {'DiameterIn': 0.03, 'DiameterOut': 0.04, 'Length': 0.06,
             'Material': 'Delrin', 'Mass': 0.0873832}

if __name__ == '__main__':
    cnx = sqldb.connect_sqldb(sys.argv[1])
    print("Sucessfully created a connection to the database")

    cur = cnx.cursor()
    print("Sucessfully created a cursor for the database")
    sqldb.create_tables(cur, TABLES)

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

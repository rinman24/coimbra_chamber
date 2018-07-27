"""MySQL DDL constants."""

tables = list()


# ----------------------------------------------------------------------------
# Table `Tube`
tables.append(("Tube",
               "CREATE TABLE IF NOT EXISTS `Tube` ("
               "  `TubeId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `DiameterIn` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  `DiameterOut` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  `Length` DECIMAL(4,4) UNSIGNED NOT NULL,"
               "  `Material` VARCHAR(50) NOT NULL,"
               "  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`TubeId`))"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))


# ----------------------------------------------------------------------------
# Table `Setting`
tables.append(("Setting",
               "CREATE TABLE IF NOT EXISTS `Setting` ("
               "  `SettingId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `Duty` DECIMAL(4,1) UNSIGNED NOT NULL,"
               "  `IsMass` BIT(1) NOT NULL,"
               "  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL,"
               "  `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL,"
               "  `Reservoir` BIT(1) NOT NULL,"
               "  `TubeId` TINYINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`SettingId`, `TubeId`),"
               "  INDEX `fk_Setting_Tube1_idx` (`TubeId` ASC),"
               "  CONSTRAINT `fk_Setting_Tube`"
               "    FOREIGN KEY (`TubeId`)"
               "    REFERENCES `Tube` (`TubeId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE) "
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))


# ----------------------------------------------------------------------------
# Table `Test`
tables.append(("Test",
               "CREATE TABLE IF NOT EXISTS `Test` ("
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,"
               "  `Author` VARCHAR(50) NOT NULL,"
               "  `DateTime` DATETIME NOT NULL,"
               "  `Description` VARCHAR(1000) NOT NULL,"
               "  `SettingId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`TestId`, `SettingId`),"
               "  INDEX `fk_Test_Setting_idx` (`SettingId` ASC),"
               "  CONSTRAINT `fk_Test_Setting`"
               "    FOREIGN KEY (`SettingId`)"
               "    REFERENCES `Setting` (`SettingId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))


# ----------------------------------------------------------------------------
# Table `Observation`
tables.append(("Observation",
               "CREATE TABLE IF NOT EXISTS `Observation` ("
               "  `CapManOk` BIT(1) NOT NULL,"
               "  `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL,"
               "  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `Mass` DECIMAL(7,7) UNSIGNED NULL DEFAULT NULL,"
               "  `OptidewOk` BIT(1) NOT NULL,"
               "  `PowOut` DECIMAL(6,4) NULL DEFAULT NULL,"
               "  `PowRef` DECIMAL(6,4) NULL DEFAULT NULL,"
               "  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Idx`, `TestId`),"
               "  INDEX `fk_Observation_Test_idx` (`TestId` ASC),"
               "  CONSTRAINT `fk_Observation_Test`"
               "    FOREIGN KEY (`TestId`)"
               "    REFERENCES `Test` (`TestId`)"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))


# ----------------------------------------------------------------------------
# Table `TempObservation`
tables.append(("TempObservation",
               "CREATE TABLE IF NOT EXISTS `TempObservation` ("
               "  `ThermocoupleNum` TINYINT(2) UNSIGNED NOT NULL,"
               "  `Temperature` DECIMAL(5,2) NOT NULL,"
               "  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Idx`, `TestId`, `ThermocoupleNum`),"
               "  CONSTRAINT `fk_TempObservation_Observation`"
               "    FOREIGN KEY (`Idx` , `TestId`)"
               "    REFERENCES `Observation` (`Idx` , `TestId`)"
               "    ON UPDATE CASCADE)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# -- -----------------------------------------------------
# -- Table `RHTargets`
tables.append(("RHTargets",
               "  CREATE TABLE IF NOT EXISTS `RHTargets` ("
               "  `RH` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`RH`, `TestId`),"
               "  INDEX `fk_RHTargets_Test_idx` (`TestId` ASC),"
               "  CONSTRAINT `fk_RHTargets_Test`"
               "    FOREIGN KEY (`TestId`)"
               "    REFERENCES `Test` (`TestId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               " ENGINE = InnoDB;"))

# -- -----------------------------------------------------
# -- Table `Results`
tables.append(("Results",
               "  CREATE TABLE IF NOT EXISTS `Results` ("
               "  `RH` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `TestId` SMALLINT(3) UNSIGNED NOT NULL,"
               "  `A` FLOAT NOT NULL,"
               "  `SigA` FLOAT UNSIGNED NOT NULL,"
               "  `B` FLOAT NOT NULL,"
               "  `SigB` FLOAT UNSIGNED NOT NULL,"
               "  `Chi2` FLOAT UNSIGNED NOT NULL,"
               "  `Q` DECIMAL(3,2) UNSIGNED NOT NULL,"
               "  `Nu` SMALLINT UNSIGNED NOT NULL,"
               "  PRIMARY KEY (`Nu`, `RH`, `TestId`),"
               "  CONSTRAINT `fk_Results_RHTargets1`"
               "    FOREIGN KEY (`RH` , `TestId`)"
               "    REFERENCES `RHTargets` (`RH` , `TestId`)"
               "    ON DELETE RESTRICT"
               "    ON UPDATE CASCADE)"
               "ENGINE = InnoDB;"))


# ----------------------------------------------------------------------------
# Table `Unit`
tables.append(("Unit",
               "CREATE TABLE IF NOT EXISTS `Unit` ("
               "  `Duty` VARCHAR(50) NOT NULL,"
               "  `Length` VARCHAR(50) NOT NULL,"
               "  `Mass` VARCHAR(50) NOT NULL,"
               "  `Power` VARCHAR(50) NOT NULL,"
               "  `Pressure` VARCHAR(50) NOT NULL,"
               "  `Temperature` VARCHAR(50) NOT NULL,"
               "  `Time` VARCHAR(50) NOT NULL)"
               "  ENGINE = InnoDB"
               "  DEFAULT CHARACTER SET = latin1;"))

# Convert tables list to immutable tuple
tables = tuple(tables)

# Constant for Table Drop
table_name_list = [table[0] for table in reversed(tables)]


# Default tube
tube_data = dict(
    DiameterIn=0.03, DiameterOut=0.04, Length=0.06, Material='Delrin',
    Mass=0.0873832
    )

# Default units
units = dict(
    Duty='Percent', Length='Meter', Mass='Kilogram', Power='Watt',
    Pressure='Pascal', Temperature='Kelvin', Time='Second'
    )

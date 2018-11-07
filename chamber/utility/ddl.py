"""DDL utility module."""

build_instructions = {
    ('experiment', 'table_order'): (
        'Tube', 'Setting', 'Test', 'Observation', 'TempObservation'
        ),
    ('experiment', 'ddl'): dict(
        Tube=(
            'CREATE TABLE IF NOT EXISTS `Tube` ('
            '  `TubeId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT, '
            '  `DiameterIn` DECIMAL(7,7) UNSIGNED NOT NULL,'
            '  `DiameterOut` DECIMAL(7,7) UNSIGNED NOT NULL,'
            '  `Length` DECIMAL(4,4) UNSIGNED NOT NULL,'
            '  `Material` VARCHAR(50) NOT NULL,'
            '  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,'
            '  PRIMARY KEY (`TubeId`))'
            '  ENGINE = InnoDB'
            '  DEFAULT CHARACTER SET = latin1;'
            ),
        Setting=(
            'CREATE TABLE IF NOT EXISTS `Setting` ('
            '  `SettingId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,'
            '  `Duty` DECIMAL(4,1) UNSIGNED NOT NULL,'
            '  `IsMass` BIT(1) NOT NULL,'
            '  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,'
            '  `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL,'
            '  `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL,'
            '  `Reservoir` BIT(1) NOT NULL,'
            '  `TubeId` TINYINT(3) UNSIGNED NOT NULL,'
            '  PRIMARY KEY (`SettingId`, `TubeId`),'
            '  INDEX `fk_Setting_Tube1_idx` (`TubeId` ASC),'
            '  CONSTRAINT `fk_Setting_Tube`'
            '    FOREIGN KEY (`TubeId`)'
            '    REFERENCES `Tube` (`TubeId`)'
            '    ON UPDATE CASCADE)'
            '  ENGINE = InnoDB'
            '  DEFAULT CHARACTER SET = latin1;'
            ),
        Test=(
            'CREATE TABLE IF NOT EXISTS `Test` ('
            '  `TestId` SMALLINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,'
            '  `Author` VARCHAR(50) NOT NULL,'
            '  `DateTime` DATETIME NOT NULL,'
            '  `Description` VARCHAR(1000) NOT NULL,'
            '  `SettingId` SMALLINT(3) UNSIGNED NOT NULL,'
            '  PRIMARY KEY (`TestId`, `SettingId`),'
            '  INDEX `fk_Test_Setting_idx` (`SettingId` ASC),'
            '  CONSTRAINT `fk_Test_Setting`'
            '    FOREIGN KEY (`SettingId`)'
            '    REFERENCES `Setting` (`SettingId`)'
            '    ON UPDATE CASCADE) '
            '  ENGINE = InnoDB'
            '  DEFAULT CHARACTER SET = latin1;'
            ),
        Observation=(
            'CREATE TABLE IF NOT EXISTS `Observation` ('
            '  `CapManOk` BIT(1) NOT NULL,'
            '  `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL,'
            '  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,'
            '  `Mass` DECIMAL(7,7) UNSIGNED NULL DEFAULT NULL,'
            '  `OptidewOk` BIT(1) NOT NULL,'
            '  `PowOut` DECIMAL(6,4) NULL DEFAULT NULL,'
            '  `PowRef` DECIMAL(6,4) NULL DEFAULT NULL,'
            '  `Pressure` MEDIUMINT(6) UNSIGNED NOT NULL,'
            '  `TestId` SMALLINT(3) UNSIGNED NOT NULL,'
            '  PRIMARY KEY (`Idx`, `TestId`),'
            '  INDEX `fk_Observation_Test_idx` (`TestId` ASC),'
            '  CONSTRAINT `fk_Observation_Test`'
            '    FOREIGN KEY (`TestId`)'
            '    REFERENCES `Test` (`TestId`)'
            '    ON UPDATE CASCADE)'
            '  ENGINE = InnoDB'
            '  DEFAULT CHARACTER SET = latin1;'
            ),
        TempObservation=(
            'CREATE TABLE IF NOT EXISTS `TempObservation` ('
            '  `ThermocoupleNum` TINYINT(2) UNSIGNED NOT NULL,'
            '  `Temperature` DECIMAL(5,2) NOT NULL,'
            '  `Idx` MEDIUMINT(6) UNSIGNED NOT NULL,'
            '  `TestId` SMALLINT(3) UNSIGNED NOT NULL,'
            '  PRIMARY KEY (`Idx`, `TestId`, `ThermocoupleNum`),'
            '  CONSTRAINT `fk_TempObservation_Observation`'
            '    FOREIGN KEY (`Idx` , `TestId`)'
            '    REFERENCES `Observation` (`Idx` , `TestId`)'
            '    ON UPDATE CASCADE)'
            '  ENGINE = InnoDB'
            '  DEFAULT CHARACTER SET = latin1;'
            )
        )
    }

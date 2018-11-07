"""DDL utility module."""

build_instructions = {
    ('experiment', 'table_order'): (
        'Tube', 'Setting'
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
            'ENGINE = InnoDB '
            'DEFAULT CHARACTER SET = latin1;'
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
            '    REFERENCES `chamber`.`Tube` (`TubeId`)'
            '    ON UPDATE CASCADE)'
            'ENGINE = InnoDB '
            'DEFAULT CHARACTER SET = latin1;'
            )
        )
    }

-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema chamber
-- -----------------------------------------------------
USE `chamber` ;

-- -----------------------------------------------------
-- Table `chamber`.`Pools`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `chamber`.`Pools` (
  `PoolId` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `InnerDiameter` DECIMAL(7,7) UNSIGNED NOT NULL,
  `OutterDiameter` DECIMAL(7,7) UNSIGNED NOT NULL,
  `Height` DECIMAL(7,7) UNSIGNED NOT NULL,
  `Material` VARCHAR(50) NOT NULL,
  `Mass` DECIMAL(7,7) NOT NULL,
  PRIMARY KEY (`PoolId`),
  UNIQUE INDEX `InnerDiameter_UNIQUE` (`InnerDiameter` ASC) VISIBLE,
  UNIQUE INDEX `OutterDiameter_UNIQUE` (`OutterDiameter` ASC) VISIBLE,
  UNIQUE INDEX `Height_UNIQUE` (`Height` ASC) VISIBLE,
  UNIQUE INDEX `Material_UNIQUE` (`Material` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `chamber`.`Settings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `chamber`.`Settings` (
  `SettingId` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Duty` DECIMAL(4,1) UNSIGNED NOT NULL,
  `Pressure` MEDIUMINT UNSIGNED NOT NULL,
  `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL,
  `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL,
  PRIMARY KEY (`SettingId`),
  UNIQUE INDEX `Duty_UNIQUE` (`Duty` ASC) VISIBLE,
  UNIQUE INDEX `Pressure_UNIQUE` (`Pressure` ASC) VISIBLE,
  UNIQUE INDEX `Temperature_UNIQUE` (`Temperature` ASC) VISIBLE,
  UNIQUE INDEX `TimeStep_UNIQUE` (`TimeStep` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `chamber`.`Tests`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `chamber`.`Tests` (
  `TestId` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Author` TINYTEXT NOT NULL,
  `DateTime` DATETIME NOT NULL,
  `Description` TEXT NOT NULL,
  `Pools_PoolId` TINYINT UNSIGNED NOT NULL,
  `Settings_SettingId` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`TestId`, `Pools_PoolId`, `Settings_SettingId`),
  UNIQUE INDEX `DateTime_UNIQUE` (`DateTime` ASC) VISIBLE,
  INDEX `fk_Tests_Pools_idx` (`Pools_PoolId` ASC) VISIBLE,
  INDEX `fk_Tests_Settings1_idx` (`Settings_SettingId` ASC) VISIBLE,
  CONSTRAINT `fk_Tests_Pools`
    FOREIGN KEY (`Pools_PoolId`)
    REFERENCES `chamber`.`Pools` (`PoolId`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Tests_Settings1`
    FOREIGN KEY (`Settings_SettingId`)
    REFERENCES `chamber`.`Settings` (`SettingId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `chamber`.`Observations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `chamber`.`Observations` (
  `ObservationId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `CapManOk` BIT(1) NOT NULL,
  `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL,
  `Idx` MEDIUMINT UNSIGNED NOT NULL,
  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,
  `OptidewOk` BIT(1) NOT NULL,
  `PowOut` DECIMAL(6,4) NULL,
  `PowRef` DECIMAL(6,4) NULL,
  `Pressure` MEDIUMINT UNSIGNED NOT NULL,
  `Tests_TestId` SMALLINT UNSIGNED NOT NULL,
  `Tests_Pools_PoolId` TINYINT UNSIGNED NOT NULL,
  `Tests_Settings_SettingId` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`ObservationId`, `Tests_TestId`, `Tests_Pools_PoolId`, `Tests_Settings_SettingId`),
  INDEX `fk_Observations_Tests1_idx` (`Tests_TestId` ASC, `Tests_Pools_PoolId` ASC, `Tests_Settings_SettingId` ASC) VISIBLE,
  CONSTRAINT `fk_Observations_Tests1`
    FOREIGN KEY (`Tests_TestId` , `Tests_Pools_PoolId` , `Tests_Settings_SettingId`)
    REFERENCES `chamber`.`Tests` (`TestId` , `Pools_PoolId` , `Settings_SettingId`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `chamber`.`Temperatures`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `chamber`.`Temperatures` (
  `ThermocoupleId` INT UNSIGNED NOT NULL,
  `Temperature` DECIMAL(5,2) UNSIGNED NOT NULL,
  `Observations_ObservationId` INT UNSIGNED NOT NULL,
  `Observations_Tests_TestId` SMALLINT UNSIGNED NOT NULL,
  `Observations_Tests_Pools_PoolId` TINYINT UNSIGNED NOT NULL,
  `Observations_Tests_Settings_SettingId` SMALLINT UNSIGNED NOT NULL,
  PRIMARY KEY (`ThermocoupleId`, `Observations_ObservationId`, `Observations_Tests_TestId`, `Observations_Tests_Pools_PoolId`, `Observations_Tests_Settings_SettingId`),
  INDEX `fk_Temperatures_Observations1_idx` (`Observations_ObservationId` ASC, `Observations_Tests_TestId` ASC, `Observations_Tests_Pools_PoolId` ASC, `Observations_Tests_Settings_SettingId` ASC) VISIBLE,
  CONSTRAINT `fk_Temperatures_Observations1`
    FOREIGN KEY (`Observations_ObservationId` , `Observations_Tests_TestId` , `Observations_Tests_Pools_PoolId` , `Observations_Tests_Settings_SettingId`)
    REFERENCES `chamber`.`Observations` (`ObservationId` , `Tests_TestId` , `Tests_Pools_PoolId` , `Tests_Settings_SettingId`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

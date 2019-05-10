-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema experimental
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `experimental` DEFAULT CHARACTER SET utf8 ;
USE `experimental` ;

-- -----------------------------------------------------
-- Table `experimental`.`Pools`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `experimental`.`Pools` (
  `PoolId` TINYINT(3) UNSIGNED NOT NULL AUTO_INCREMENT,
  `InnerDiameter` DECIMAL(4,4) UNSIGNED NOT NULL,
  `OuterDiameter` DECIMAL(4,4) UNSIGNED NOT NULL,
  `Height` DECIMAL(4,4) UNSIGNED NOT NULL,
  `Material` VARCHAR(50) NOT NULL,
  `Mass` DECIMAL(7,7) NOT NULL,
  PRIMARY KEY (`PoolId`))
ENGINE = InnoDB 
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `experimental`.`Settings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `experimental`.`Settings` (
  `SettingId` SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `Duty` DECIMAL(4,1) UNSIGNED NOT NULL,
  `Pressure` MEDIUMINT(8) UNSIGNED NOT NULL,
  `Temperature` DECIMAL(4,1) UNSIGNED NOT NULL,
  `TimeStep` DECIMAL(4,2) UNSIGNED NOT NULL,
  PRIMARY KEY (`SettingId`))
ENGINE = InnoDB 
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `experimental`.`Experiments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `experimental`.`Experiments` (
  `ExperimentId` SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT,
  `Author` TINYTEXT NOT NULL,
  `DateTime` DATETIME NOT NULL,
  `Description` TEXT NOT NULL,
  `Pools_PoolId` TINYINT(3) UNSIGNED NOT NULL,
  `Settings_SettingId` SMALLINT(5) UNSIGNED NOT NULL,
  PRIMARY KEY (`ExperimentId`),
  UNIQUE INDEX `DateTime_UNIQUE` (`DateTime` ASC) VISIBLE,
  INDEX `fk_Experiments_Pools_idx` (`Pools_PoolId` ASC) VISIBLE,
  INDEX `fk_Experiments_Settings_idx` (`Settings_SettingId` ASC) VISIBLE,
  CONSTRAINT `fk_Experiments_Pools`
    FOREIGN KEY (`Pools_PoolId`)
    REFERENCES `experimental`.`Pools` (`PoolId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Experiments_Settings`
    FOREIGN KEY (`Settings_SettingId`)
    REFERENCES `experimental`.`Settings` (`SettingId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB 
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `experimental`.`Observations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `experimental`.`Observations` (
  `ObservationId` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `CapManOk` BIT(1) NOT NULL,
  `DewPoint` DECIMAL(5,2) UNSIGNED NOT NULL,
  `Idx` MEDIUMINT(8) UNSIGNED NOT NULL,
  `Mass` DECIMAL(7,7) UNSIGNED NOT NULL,
  `OptidewOk` BIT(1) NOT NULL,
  `PowOut` DECIMAL(6,4) NULL DEFAULT NULL,
  `PowRef` DECIMAL(6,4) NULL DEFAULT NULL,
  `Pressure` MEDIUMINT(8) UNSIGNED NOT NULL,
  `Experiments_ExperimentId` SMALLINT(5) UNSIGNED NOT NULL,
  PRIMARY KEY (`ObservationId`),
  INDEX `fk_Observations_Experiments_idx` (`Experiments_ExperimentId` ASC) VISIBLE,
  CONSTRAINT `fk_Observations_Experiments`
    FOREIGN KEY (`Experiments_ExperimentId`)
    REFERENCES `experimental`.`Experiments` (`ExperimentId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB 
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `experimental`.`Temperatures`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `experimental`.`Temperatures` (
  `TemperatureId` INT(12) NOT NULL AUTO_INCREMENT,
  `ThermocoupleNum` TINYINT(2) UNSIGNED NOT NULL,
  `Temperature` DECIMAL(5,2) UNSIGNED NOT NULL,
  `Observations_ObservationId` INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (`TemperatureId`),
  INDEX `fk_Temperatures_Observations_idx` (`Observations_ObservationId` ASC) VISIBLE,
  CONSTRAINT `fk_Temperatures_Observations`
    FOREIGN KEY (`Observations_ObservationId`)
    REFERENCES `experimental`.`Observations` (`ObservationId`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB 
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

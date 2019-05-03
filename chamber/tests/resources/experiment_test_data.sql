USE `chamber`;

-- -----------------------------------------------------
-- Table `chamber`.`Settings`
-- -----------------------------------------------------
INSERT INTO `chamber`.`Settings` 
            (`Duty`, 
             `Pressure`, 
             `Temperature`, 
             `TimeStep`) 
VALUES      (0, 
             101325, 
             300, 
             1);

-- -----------------------------------------------------
-- Table `chamber`.`Pools`
-- -----------------------------------------------------
INSERT INTO `chamber`.`Pools` 
            (`InnerDiameter`, 
             `OuterDiameter`, 
             `Height`, 
             `Material`, 
             `Mass`) 
VALUES      (0.03, 
             0.04, 
             0.01, 
             'Delrin', 
             0.050);

-- -----------------------------------------------------
-- Table `chamber`.`Tests`
-- -----------------------------------------------------
INSERT INTO `chamber`.`Tests` 
            (`Author`,
             `DateTime`,
             `Description`,
             `Pools_PoolId`,
             `Settings_SettingId`) 
VALUES      ('RHI',
             '2019-9-24 7:45:00',
             'Test description.',
             1,
             1);

-- -----------------------------------------------------
-- Table `chamber`.`Tests`
-- -----------------------------------------------------
INSERT INTO `chamber`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Tests_TestId`,
             `Tests_Pools_PoolId`,
             `Tests_Settings_SettingId`)
VALUES      (1,
             280,
             0,
             0.999,
             1,
             101325,
             1,
             1,
             1);
INSERT INTO `chamber`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Tests_TestId`,
             `Tests_Pools_PoolId`,
             `Tests_Settings_SettingId`)
VALUES      (1,
             281,
             1,
             0.998,
             1,
             101324,
             1,
             1,
             1);
INSERT INTO `chamber`.`Observations` 
            (`CapManOk`,
             `DewPoint`,
             `Idx`,
             `Mass`,
             `OptidewOk`,
             `Pressure`,
             `Tests_TestId`,
             `Tests_Pools_PoolId`,
             `Tests_Settings_SettingId`)
VALUES      (1,
             282,
             2,
             0.997,
             1,
             101323,
             1,
             1,
             1);

-- -----------------------------------------------------
-- Table `chamber`.`Temperatures`
-- -----------------------------------------------------
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (0,
             290,
             1,
             1,
             1,
             1);
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (1,
             290.2,
             1,
             1,
             1,
             1);
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (0,
             291,
             2,
             1,
             1,
             1);
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (1,
             291.2,
             2,
             1,
             1,
             1);
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (0,
             292,
             3,
             1,
             1,
             1);
INSERT INTO `chamber`.`Temperatures` 
            (`ThermocoupleId`,
             `Temperature`,
             `Observations_ObservationId`,
             `Observations_Tests_TestId`,
             `Observations_Tests_Pools_PoolId`,
             `Observations_Tests_Settings_SettingId`)
VALUES      (1,
             292.2,
             3,
             1,
             1,
             1);

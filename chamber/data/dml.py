"""MySQL DML constants."""


add_setting = ("INSERT INTO Setting "
               "(Duty, IsMass, Pressure, Reservoir, Temperature, TimeStep,"
               " TubeId)"
               " VALUES "
               "(%(Duty)s, %(IsMass)s, %(Pressure)s, %(Reservoir)s, "
               "%(Temperature)s, %(TimeStep)s, %(TubeId)s)")

add_test = ("INSERT INTO Test "
            "(Author, DateTime, Description,"
            " SettingID)"
            " VALUES "
            "(%(Author)s, %(DateTime)s, %(Description)s,"
            " %(SettingID)s)")

add_obs_m_t = ("INSERT INTO Observation "
               "(CapManOk, DewPoint, Idx, Mass, OptidewOk, PowOut, PowRef,"
               " Pressure, TestID)"
               " VALUES "
               "(%(CapManOk)s, %(DewPoint)s, %(Idx)s, %(Mass)s, %(OptidewOk)s,"
               " %(PowOut)s, %(PowRef)s, %(Pressure)s, %(TestId)s)")

add_obs_m_f = ("INSERT INTO Observation "
               "(CapManOk, DewPoint, Idx, OptidewOk, PowOut, PowRef,"
               " Pressure, TestID)"
               " VALUES "
               "(%(CapManOk)s, %(DewPoint)s, %(Idx)s, %(OptidewOk)s,"
               " %(PowOut)s, %(PowRef)s, %(Pressure)s, %(TestId)s)")

add_temp = ("INSERT INTO TempObservation "
            "(ThermocoupleNum, Temperature, Idx, TestId)"
            " VALUES "
            "(%s, %s, %s, %s)")

add_rh = ("INSERT INTO RHTarget "
          "(TestId, RH)"
          " VALUES "
          "(%(TestId)s, %(RH)s)")

add_result = ("INSERT INTO Results "
              "(TestId, RH, A, SigA, B, SigB, Chi2, Q,"
              " Nu)"
              " VALUES "
              "(%(TestId)s, %(RH)s, %(A)s, %(SigA)s, %(B)s, "
              "%(SigB)s, %(Chi2)s, %(Q)s, %(Nu)s)")

add_tube = ("INSERT INTO Tube "
            "(DiameterIn, DiameterOut, Length, Material, Mass)"
            " VALUES "
            "(%(DiameterIn)s, %(DiameterOut)s, %(Length)s,"
            " %(Material)s, %(Mass)s)")

add_rh_targets = ("INSERT INTO RHTargets (TestId, RH, SigRH) VALUES "
                  "(%s, %s, %s)")

add_results = ("INSERT INTO Results"
               "  (TestId, RH, A, SigA, B, SigB, Chi2, Q, Nu)"
               "  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

add_unit = ("INSERT INTO Unit "
            "(Duty, Length, Mass, Power, Pressure, Temperature, Time)"
            " VALUES "
            "(%(Duty)s, %(Length)s, %(Mass)s, %(Power)s, %(Pressure)s,"
            " %(Temperature)s, %(Time)s)")

select_setting = ("SELECT SettingID FROM Setting WHERE "
                  "  Duty = %(Duty)s AND"
                  "  Pressure = %(Pressure)s AND"
                  "  Temperature = %(Temperature)s AND"
                  "  IsMass = %(IsMass)s AND"
                  "  Reservoir = %(Reservoir)s AND"
                  "  TimeStep = %(TimeStep)s AND"
                  "  TubeId = %(TubeId)s")

select_test = ("SELECT TestID FROM Test WHERE "
               "    DateTime='{}'")

test_from_setting = ("SELECT TestId FROM Test WHERE "
                     "    SettingId=({})")

select_tube = ("SELECT TubeID FROM Tube WHERE "
               "  DiameterIn = %(DiameterIn)s AND"
               "  DiameterOut = %(DiameterOut)s AND"
               "  Length = %(Length)s AND"
               "  Material = %(Material)s AND"
               "  Mass = %(Mass)s")

get_last_dew_point = ("SELECT"
                      "    DewPoint "
                      "FROM"
                      "    Observation "
                      "WHERE"
                      "    TestID={} "
                      "ORDER BY Idx DESC "
                      "LIMIT 1;")

get_temp_obs = ("SELECT"
                "    Temperature, ThermocoupleNum "
                "FROM"
                "    TempObservation "
                "WHERE"
                "    TestId={} "
                "AND"
                "    Idx={} "
                "ORDER BY ThermocoupleNum ASC;")

get_obs_data_m = ("SELECT"
                  "    CapManOk, DewPoint, Mass,"
                  "    OptidewOk, PowOut, PowRef, Pressure "
                  "FROM"
                  "    Observation "
                  "WHERE"
                  "    TestId={} "
                  "AND"
                  "    Idx ={};")

get_obs_data_t = ("SELECT"
                  "    CapManOk, DewPoint, OptidewOk,"
                  "    PowOut, PowRef, Pressure "
                  "FROM"
                  "    Observation "
                  "WHERE"
                  "    TestId={} "
                  "AND"
                  "    Idx ={};")

get_temp_obs_data = ("SELECT"
                     "    Temperature "
                     "FROM"
                     "    TempObservation "
                     "WHERE"
                     "    TestId = {} "
                     "AND"
                     "    Idx = {} "
                     "AND"
                     "    ThermocoupleNum = {};")

get_temp_df = ("SELECT Idx,"
               "MAX(CASE WHEN ThermocoupleNum=0 THEN VALUE ELSE 0 END) TC0, "
               "MAX(CASE WHEN ThermocoupleNum=1 THEN VALUE ELSE 0 END) TC1, "
               "MAX(CASE WHEN ThermocoupleNum=2 THEN VALUE ELSE 0 END) TC2, "
               "MAX(CASE WHEN ThermocoupleNum=3 THEN VALUE ELSE 0 END) TC3, "
               "MAX(CASE WHEN ThermocoupleNum=4 THEN VALUE ELSE 0 END) TC4, "
               "MAX(CASE WHEN ThermocoupleNum=5 THEN VALUE ELSE 0 END) TC5, "
               "MAX(CASE WHEN ThermocoupleNum=6 THEN VALUE ELSE 0 END) TC6, "
               "MAX(CASE WHEN ThermocoupleNum=7 THEN VALUE ELSE 0 END) TC7, "
               "MAX(CASE WHEN ThermocoupleNum=8 THEN VALUE ELSE 0 END) TC8, "
               "MAX(CASE WHEN ThermocoupleNum=9 THEN VALUE ELSE 0 END) TC9, "
               "MAX(CASE WHEN ThermocoupleNum=10 THEN VALUE ELSE 0 END) TC10, "
               "MAX(CASE WHEN ThermocoupleNum=11 THEN VALUE ELSE 0 END) TC11, "
               "MAX(CASE WHEN ThermocoupleNum=12 THEN VALUE ELSE 0 END) TC12, "
               "MAX(CASE WHEN ThermocoupleNum=13 THEN VALUE ELSE 0 END) TC13 "
               "FROM("
               "SELECT Idx, ThermocoupleNum, Temperature VALUE FROM "
               "TempObservation WHERE TestId={}) "
               "src GROUP BY Idx;")

get_obs_df = ("SELECT Idx, DewPoint, Mass, Pressure, PowOut, PowRef, "
              "OptidewOk, CapManOk FROM Observation WHERE TestId={};")

get_info_df = ("SELECT Temperature, Pressure, Duty, IsMass, Reservoir, "
               "TimeStep, Test.DateTime, Author, Description, TubeId, TestId, "
               "Setting.SettingId FROM Test INNER JOIN Setting ON "
               "Setting.SettingId=Test.SettingId WHERE TestId={};")

add_best_fit = ("UPDATE RHTargets INNER JOIN (SELECT * FROM Results WHERE "
                "TestId={0} AND REPLACE(REPLACE(CONCAT(RH, SigB+0), '.', ''), "
                "'0', '')+0 IN (SELECT REPLACE(REPLACE(CONCAT(RH, Min(SigB)), "
                "'.', ''), '0', '')+0 FROM Results WHERE TestId={0} AND "
                "CONCAT(RH, ABS(Q-0.5)) IN (SELECT CONCAT(RH, "
                "Min(ABS(Q-0.5))) FROM Results WHERE TestId={0} AND Nu>{1} "
                "GROUP BY RH) GROUP BY RH)) AS BestFit SET "
                "RHTargets.Nu=BestFit.Nu WHERE RHTargets.RH=BestFit.RH AND "
                "RHTargets.TestId=BestFit.TestId")

settings_df = ('SELECT Pressure, Temperature, Reservoir, TestId FROM Setting '
               'INNER JOIN Test ON Test.SettingId=Setting.SettingId')

analysis_tid = 'SELECT DISTINCT TestId FROM RHTargets'

get_high_low_testids = ('SELECT TestId FROM Test Inner Join Setting ON '
                        'Test.SettingId=Setting.SettingId WHERE '
                        'Setting.Temperature={0} AND Setting.Pressure={1} AND '
                        'TestId IN (SELECT TestId FROM RHTargets)')

get_rhtargets_results = ('SELECT RHT.RH, SigRH, B, SigB FROM RHTargets AS RHT '
                         'INNER JOIN Results AS Res ON RHT.RH=Res.RH AND '
                         'RHT.TestId=Res.TestId AND RHT.Nu=Res.Nu WHERE '
                         'RHT.TestId={}')

get_reservoir = ('SELECT Reservoir FROM Setting INNER JOIN Test ON '
                 'Test.SettingId=Setting.SettingId WHERE TestId={}')

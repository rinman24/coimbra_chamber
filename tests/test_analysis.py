"""Unit tests (pytest) for the analysis module."""

import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from scipy import stats

import chamber.analysis as anlys

TARGET_RH = 0.15
TARGET_IDX = 12770
HALF_LEN = 7000
SIGMA = 4e-8


@pytest.fixture(scope='module')
def df_01():
    """
    Fixture to instantiate only one pd.DataFrame object for testing.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = '1atm_290K_0duty_44mm_Mass_FanOff_LowRH_Sample.csv'
    filepath = os.path.join(dir_path, 'csv_test_files', filename)
    dataframe = pd.read_csv(filepath)
    return dataframe


@pytest.fixture(scope='module')
def df_bad():
    """
    Fixture to instantiate only one pd.DataFrame object for testing.
    """
    data = [[1, 2, 3], [4, 5, 6]]
    columns = ['A', 'B', 'C']
    dataframe = pd.DataFrame(data, columns=columns)
    return dataframe


class Test_Analysis(object):
    """Unit testing of analysis module."""

    @staticmethod
    def test__zero_time(df_01, df_bad):
        assert df_01.Idx[0] == 8000

        df_01 = anlys._zero_time(df_01)
        assert df_01.Idx[0] == 0

        with pytest.raises(AttributeError) as err:
            anlys._zero_time(df_bad)
        assert err.value.args[0] == "'DataFrame' object has no attribute 'Idx'"

    @staticmethod
    def test__format_temp(df_01, df_bad):
        assert math.isclose(df_01.TC4[0], 290.799)
        assert math.isclose(df_01.TC7[100], 290.358)
        assert math.isclose(df_01.TC11[8000], 289.975)

        df_01 = anlys._format_temp(df_01)

        assert math.isclose(df_01.TC4[0], round(290.799, 1))
        assert math.isclose(df_01.TC7[100], round(290.358, 1))
        assert math.isclose(df_01.TC11[8000], round(289.975, 1))

        with pytest.raises(KeyError) as err:
            anlys._format_temp(df_bad)
        err_msg = (
            "None of [['TC4', 'TC5', 'TC6', 'TC7', 'TC8', 'TC9', 'TC10', "
            "'TC11', 'TC12', 'TC13']] are in the [columns]"
            )
        assert err.value.args[0] == err_msg

    @staticmethod
    def test__format_dew_point(df_01, df_bad):
        assert math.isclose(df_01.DewPoint[0], 259.04)
        assert math.isclose(df_01.DewPoint[100], 259.145)
        assert math.isclose(df_01.DewPoint[8000], 263.562)

        df_01 = anlys._format_dew_point(df_01)

        assert math.isclose(df_01.DewPoint[0], round(259.04, 1))
        assert math.isclose(df_01.DewPoint[100], round(259.145, 1))
        assert math.isclose(df_01.DewPoint[8000], round(263.562, 1))

        with pytest.raises(AttributeError) as err:
            anlys._format_dew_point(df_bad)
        assert err.value.args[0] == (
            "'DataFrame' object has no attribute 'DewPoint'"
            )

    @staticmethod
    def test__format_pressure(df_01, df_bad):
        assert math.isclose(df_01.Pressure[0], 100156.841)
        assert math.isclose(df_01.Pressure[100], 100161.21800000001)
        assert math.isclose(df_01.Pressure[8000], 100266.27900000001)

        df_01 = anlys._format_pressure(df_01)

        assert math.isclose(df_01.Pressure[0], round(100156.841, 0))
        assert math.isclose(df_01.Pressure[100], round(100161.21800000001, 0))
        assert math.isclose(df_01.Pressure[8000], round(100266.27900000001, 0))

        with pytest.raises(AttributeError) as err:
            anlys._format_pressure(df_bad)
        assert err.value.args[0] == (
            "'DataFrame' object has no attribute 'Pressure'"
            )

    @staticmethod
    def test__add_avg_te(df_01, df_bad):
        assert 'Te' not in set(df_01)

        df_01 = anlys._add_avg_te(df_01)
        assert 'Te' in set(df_01)

        tc_keys = ['TC{}'.format(i) for i in range(4, 14)]
        mean = np.mean(df_01.loc[0, tc_keys])
        assert math.isclose(df_01.Te[0], round(mean, 1))

        with pytest.raises(KeyError) as err:
            anlys._add_avg_te(df_bad)
        err_msg = (
            "None of [['TC4', 'TC5', 'TC6', 'TC7', 'TC8', 'TC9', 'TC10', "
            "'TC11', 'TC12', 'TC13']] are in the [columns]"
            )
        assert err.value.args[0] == err_msg

        plt.plot(df_01.loc[:, tc_keys], 'k')
        plt.plot(df_01.Te, 'r', label='Average Temperature')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('temperature/K')
        plt.title('Average Temperature: No Smoothing')
        plt.show()

    @staticmethod
    def test__add_smooth_avg_te(df_01, df_bad):
        assert 'TeSmooth' not in set(df_01)

        df_01 = anlys._add_smooth_avg_te(df_01)
        assert 'TeSmooth' in set(df_01)

        with pytest.raises(AttributeError) as err:
            anlys._add_smooth_avg_te(df_bad)
        assert err.value.args[0] == "'DataFrame' object has no attribute 'Te'"

        plt.plot(df_01.Te, label='before')
        plt.plot(df_01.TeSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('temperature/K')
        plt.title('Smoothed Average Temperature')
        plt.show()

    @staticmethod
    def test__add_smooth_dew_point(df_01, df_bad):
        assert 'DewPointSmooth' not in set(df_01)

        df_01 = anlys._add_smooth_dew_point(df_01)
        assert 'DewPointSmooth' in set(df_01)

        with pytest.raises(AttributeError) as err:
            anlys._add_smooth_dew_point(df_bad)
        assert err.value.args[0] == ("'DataFrame' object has no attribute" +
                                     " 'DewPoint'")

        plt.plot(df_01.DewPoint, label='before')
        plt.plot(df_01.DewPointSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('Dew Point/K')
        plt.title('Smoothed Dew Point')
        plt.show()

    @staticmethod
    def test__add_smooth_pressure(df_01, df_bad):
        assert 'PressureSmooth' not in set(df_01)

        df_01 = anlys._add_smooth_pressure(df_01)
        assert 'PressureSmooth' in set(df_01)

        with pytest.raises(AttributeError) as err:
            anlys._add_smooth_pressure(df_bad)
        assert err.value.args[0] == (
            "'DataFrame' object has no attribute 'Pressure'"
            )

        plt.plot(df_01.Pressure, label='before')
        plt.plot(df_01.PressureSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('Pressure/Pa')
        plt.title('Smoothed Pressure')
        plt.show()

    @staticmethod
    def test__add_all_smooth(df_01):
        # df_01.drop()
        pass

    @staticmethod
    def test__get_rh():
        rh = anlys._get_coolprop_rh([101325, 290, 275])
        assert math.isclose(rh, 0.36377641815012024)

    @staticmethod
    def test__add_rh(df_01):
        assert 'RH' not in set(df_01)

        df_01 = anlys._add_rh(df_01)
        assert 'RH' in set(df_01)

        plt.plot(df_01.RH, label='RH')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()

    @staticmethod
    def test__get_max_half_len(df_01):
        max_window = anlys._get_max_half_len(df_01, TARGET_IDX)
        assert max_window == (len(df_01)-1) - TARGET_IDX

        fail_list = [0, -1, -2, len(df_01)-1, len(df_01), len(df_01)+1]

        for idx in fail_list:
            with pytest.raises(IndexError) as err:
                anlys._get_max_half_len(df_01, idx)
            err_msg = (
                "no 'half length' available for the target index: "
                "target must have at least one element to right or left"
                )
            assert err.value.args[0] == err_msg

    @staticmethod
    def test__get_rh_idx(df_01):
        idx = anlys._get_target_idx(df_01, TARGET_RH)
        assert idx == TARGET_IDX
        rh = df_01.RH[idx]
        assert math.isclose(rh, TARGET_RH, abs_tol=0.01)

        plt.plot(df_01.RH, label='RH', color='orange')
        plt.axvline(x=idx)
        plt.axhline(y=TARGET_RH)

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()

    @staticmethod
    def test__get_stat_group(df_01):
        time, mass = anlys._get_stat_group(df_01, TARGET_IDX, HALF_LEN)

        assert len(time) == 2*HALF_LEN + 1
        assert len(mass) == 2*HALF_LEN + 1

        plt.plot(df_01.RH, label='RH', color='orange')
        plt.plot(time, mass, 'r', label='Group')
        plt.axvline(x=TARGET_IDX)
        plt.axvline(x=TARGET_IDX-HALF_LEN, linestyle='--')
        plt.axvline(x=TARGET_IDX+HALF_LEN+1, linestyle='--')
        plt.axhline(y=TARGET_RH)

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()

    @staticmethod
    def test__get_valid_rh_targets(df_01):
        rh_list = anlys._get_valid_rh_targets(df_01)
        assert rh_list == [0.1, 0.15]

    @staticmethod
    def test__half_len_gen(df_01):
        half_len_list = list(
            anlys._half_len_gen(df_01, TARGET_IDX, steps=1000)
        )

        assert half_len_list == (
            list(map(lambda x: x*1000, range(1, 8)))
            )

        gen_output = []
        for _ in range(3):
            for half_len in anlys._half_len_gen(df_01, TARGET_IDX, steps=1000):
                gen_output.append(half_len)

        assert gen_output == 3*(
            list(map(lambda x: x*1000, range(1, 8)))
            )

    @staticmethod
    def test__analysis(df_01):
        df_res = anlys.analysis(df_01, sigma=SIGMA, steps=1000, plot=True)
        assert math.isclose(df_res.a[0], 0.09929181759175223)
        assert math.isclose(df_res.sig_a[0], 1.882350488972039e-09)
        assert math.isclose(df_res.b[0], -8.48536063565115e-09)
        assert math.isclose(df_res.sig_b[0], 1.5480323625508021e-12)
        assert math.isclose(df_res.chi2[0], 2802.071645)
        assert math.isclose(df_res.Q[0], 5.0309854179812744e-30)
        assert math.isclose(df_res.nu[0], 1999)
        assert math.isclose(df_res.RH[0], 0.10)

        assert math.isclose(df_res.a[1], 0.09928473225936885)
        assert math.isclose(df_res.sig_a[1], 1.9788587163647553e-08)
        assert math.isclose(df_res.b[1], -7.292364819906284e-09)
        assert math.isclose(df_res.sig_b[1], 1.54803236255134e-12)
        assert math.isclose(df_res.chi2[1], 1382.7937526640128)
        assert math.isclose(df_res.Q[1], 1)
        assert math.isclose(df_res.nu[1], 1999)
        assert math.isclose(df_res.RH[1], 0.15)

        assert math.isclose(df_res.a[2], 0.0992847607314092)
        assert math.isclose(df_res.sig_a[2], 7.020334750875644e-09)
        assert math.isclose(df_res.b[2], -7.290912322449235e-09)
        assert math.isclose(df_res.sig_b[2], 5.475172428149881e-13)
        assert math.isclose(df_res.chi2[2], 10638.623831298488)
        assert math.isclose(df_res.Q[2], 0)
        assert math.isclose(df_res.nu[2], 3999)
        assert math.isclose(df_res.RH[2], 0.15)

        assert math.isclose(df_res.a[3], 0.09928492489007704)
        assert math.isclose(df_res.sig_a[3], 3.841190733562833e-09)
        assert math.isclose(df_res.b[3], -7.298178904296539e-09)
        assert math.isclose(df_res.sig_b[3], 2.980678810643896e-13)
        assert math.isclose(df_res.chi2[3], 54716.265494654326)
        assert math.isclose(df_res.Q[3], 0)
        assert math.isclose(df_res.nu[3], 5999)
        assert math.isclose(df_res.RH[3], 0.15)

        assert math.isclose(df_res.a[4], 0.09928501416933047)
        assert math.isclose(df_res.sig_a[4], 2.5125517326302e-09)
        assert math.isclose(df_res.b[4], -7.2980450551660015e-09)
        assert math.isclose(df_res.sig_b[4], 1.936128652762121e-13)
        assert math.isclose(df_res.chi2[4], 185676.2439066843)
        assert math.isclose(df_res.Q[4], 0)
        assert math.isclose(df_res.nu[4], 7999)
        assert math.isclose(df_res.RH[4], 0.15)

        assert math.isclose(df_res.a[5], 0.09928517018827725)
        assert math.isclose(df_res.sig_a[5], 1.8138480092937777e-09)
        assert math.isclose(df_res.b[5], -7.301819411160758e-09)
        assert math.isclose(df_res.sig_b[5], 1.3854328328617352e-13)
        assert math.isclose(df_res.chi2[5], 487010.5588674388)
        assert math.isclose(df_res.Q[5], 0)
        assert math.isclose(df_res.nu[5], 9999)
        assert math.isclose(df_res.RH[5], 0.15)

        assert math.isclose(df_res.a[6], 0.09928533452472244)
        assert math.isclose(df_res.sig_a[6], 1.394557435907611e-09)
        assert math.isclose(df_res.b[6], -7.304318945031545e-09)
        assert math.isclose(df_res.sig_b[6], 1.0539608092031018e-13)
        assert math.isclose(df_res.chi2[6], 1165909.144084889)
        assert math.isclose(df_res.Q[6], 0)
        assert math.isclose(df_res.nu[6], 11999)
        assert math.isclose(df_res.RH[6], 0.15)

        assert math.isclose(df_res.a[7], 0.09928550093016279)
        assert math.isclose(df_res.sig_a[7], 1.1202981539221108e-09)
        assert math.isclose(df_res.b[7], -7.304791649674251e-09)
        assert math.isclose(df_res.sig_b[7], 8.363961634717462e-14)
        assert math.isclose(df_res.chi2[7], 2540353.715297388)
        assert math.isclose(df_res.Q[7], 0)
        assert math.isclose(df_res.nu[7], 13999)
        assert math.isclose(df_res.RH[7], 0.15)

    @staticmethod
    def test_postprocess(df_01):
        df_res = anlys.analysis(df_01, sigma=SIGMA, steps=1000, plot=False)
        # Now I have the result df
        # Pass this into postprocess
        df_post = anlys.postprocess(df_res)
        print(df_post.head())
        assert True

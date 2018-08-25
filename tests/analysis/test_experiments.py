"""Unit tests (pytest) for the analysis module."""

import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle as pkl
import pytest
from scipy import stats

import chamber.analysis.experiments as expr

if os.getenv('CI'):
    PLOT = False
else:
    PLOT = True

TARGET_RH = 0.15
TARGET_IDX = 12770
HALF_LEN = 7000
SIGMA = 4e-8
PARAM_LIST = ['PressureSmooth', 'TeSmooth', 'DewPointSmooth']
TC_LIST = ['TC{0}'.format(i) for i in range(4, 14)]

# ----------------------------------------------------------------------------
# Test _zero_time global variables
ZERO_TIME_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    Idx=[20001, 20001e4, 33338333.5, 1e4, 0, 2e4]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _format_temp global variables
FORMAT_TEMP_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    TC4=[20001, 5811389.8000000007, 0.011664499825010125, 290.55496225188745,
         290.30000000000001, 291.0],
    TC5=[20001, 5802036.4999999991, 0.0011072256387185673, 290.08732063396826,
         290.0, 290.10000000000002],
    TC6=[20001, 5802257.0999999996, 0.00016227763611826785, 290.09835008249587,
         290.0, 290.10000000000002],
    TC7=[20001, 5805846.3000000007, 0.0020231846407686763, 290.27780110994456,
         290.19999999999999, 290.39999999999998],
    TC8=[20001, 5806176.5, 0.001810625518724122, 290.29431028448579,
         290.19999999999999, 290.39999999999998],
    TC9=[20001, 5800010.8000000007, 0.0012011281435933669, 289.98604069796517,
         289.89999999999998, 290.0],
    TC10=[20001, 5797574.1000000015, 0.0022981399430012824, 289.8642117894106,
          289.80000000000001, 289.89999999999998],
    TC11=[20001, 5799775.1000000006, 0.0019117281135951898, 289.97425628718565,
          289.89999999999998, 290.0],
    TC12=[20001, 5796716.9000000013, 0.0016794867756600713, 289.82135393230345,
          289.80000000000001, 289.89999999999998],
    TC13=[20001, 5797926.2000000011, 0.0014878223088835407, 289.88181590920459,
          289.80000000000001, 289.89999999999998]
    )
).set_index('idx')


# ----------------------------------------------------------------------------
# Test _format_dew_point global variables
FORMAT_DP_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    DewPoint=[20001, 5269690.5000000009, 3.5677552185390735,
              263.47135143242843, 259.0, 266.39999999999998]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _format_presssure global variables
FORMAT_P_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    Pressure=[20001, 2005196296.0, 1723.9397677566121, 100254.802059897,
              100078.0, 100358.0]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _add_avg_te global variables
AVG_T_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    Te=[20001, 5801992.4000000004, 0.0014759478526079042, 290.08511574421283,
        290.0, 290.19999999999999]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _multi_rh global variables
RH_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    RH=[20001, 2803.8464972706283, 0.00051402847579061852, 0.14018531559775152,
        0.093374396753349437, 0.1784676778434911]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _multi_rh_err global variables
SIGRH_STATS = pd.DataFrame(dict(
    idx=['cnt', 'sum', 'var', 'avg', 'min', 'max'],
    SigRH=[20001, 49.954031383018787, 1.3734073708436497e-07,
           0.0024975766903164234, 0.0017245551439777212, 0.0031181436063756618]
    )
).set_index('idx')

# ----------------------------------------------------------------------------
# Test _add_rh global variables
RH_STATS_JOIN = RH_STATS.join(SIGRH_STATS)

# ----------------------------------------------------------------------------
# Test best fit analysis global variables
ANALYSIS_DF = pkl.load(open(os.path.join(
   os.getcwd(), 'tests', 'data_test_files', 'analysis_df'), 'rb'))
RH_SET_DF = ANALYSIS_DF[ANALYSIS_DF['RH'] == 0.3].reset_index()
Q_IDX = 8


@pytest.fixture(scope='module')
def df_01():
    """Fixture to instantiate only one pd.DataFrame object for testing."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = '1atm_290K_0duty_44mm_Mass_FanOff_LowRH_Sample.csv'
    filepath = os.path.join(dir_path, 'csv_test_files', filename)
    dataframe = pd.read_csv(filepath)
    return dataframe


@pytest.fixture(scope='module')
def df_01_original():
    """Fixture to instantiate only one pd.DataFrame object for testing."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filename = '1atm_290K_0duty_44mm_Mass_FanOff_LowRH_Sample.csv'
    filepath = os.path.join(dir_path, 'csv_test_files', filename)
    dataframe = pd.read_csv(filepath)
    return dataframe


@pytest.fixture(scope='module')
def df_bad():
    """Fixture to instantiate only one pd.DataFrame object for testing."""
    data = [[1, 2, 3], [4, 5, 6]]
    columns = ['A', 'B', 'C']
    dataframe = pd.DataFrame(data, columns=columns)
    return dataframe


def test__zero_time(df_01, df_bad):
    """Test _zero_time."""
    assert df_01.Idx.iloc[0] == 8000
    assert df_01.Idx.iloc[-1] == 28000

    df_01 = expr._zero_time(df_01)
    for col in ZERO_TIME_STATS:
        assert math.isclose(
            df_01[col].count(), ZERO_TIME_STATS.loc['cnt', col]
            )
        assert math.isclose(df_01[col].sum(), ZERO_TIME_STATS.loc['sum', col])
        assert math.isclose(df_01[col].var(), ZERO_TIME_STATS.loc['var', col])
        assert math.isclose(df_01[col].mean(), ZERO_TIME_STATS.loc['avg', col])
        assert math.isclose(df_01[col].min(), ZERO_TIME_STATS.loc['min', col])
        assert math.isclose(df_01[col].max(), ZERO_TIME_STATS.loc['max', col])

    assert df_01.Idx.iloc[0] == 0
    assert df_01.Idx.iloc[-1] == 20000

    with pytest.raises(AttributeError) as err:
        expr._zero_time(df_bad)
    assert err.value.args[0] == "'DataFrame' object has no attribute 'Idx'"


def test__format_temp(df_01, df_bad):
    """Test _format_temp."""
    assert math.isclose(df_01.TC4[0], 290.799)
    assert math.isclose(df_01.TC7[100], 290.358)
    assert math.isclose(df_01.TC11[8000], 289.975)

    df_01 = expr._format_temp(df_01)
    for col in FORMAT_TEMP_STATS:
        assert math.isclose(
            df_01[col].count(), FORMAT_TEMP_STATS.loc['cnt', col]
            )
        assert math.isclose(
            df_01[col].sum(), FORMAT_TEMP_STATS.loc['sum', col]
            )
        assert math.isclose(
            df_01[col].var(), FORMAT_TEMP_STATS.loc['var', col]
            )
        assert math.isclose(
            df_01[col].mean(), FORMAT_TEMP_STATS.loc['avg', col]
            )
        assert math.isclose(
            df_01[col].min(), FORMAT_TEMP_STATS.loc['min', col]
            )
        assert math.isclose(
            df_01[col].max(), FORMAT_TEMP_STATS.loc['max', col]
            )

    assert math.isclose(df_01.TC4[0], round(290.799, 1))
    assert math.isclose(df_01.TC7[100], round(290.358, 1))
    assert math.isclose(df_01.TC11[8000], round(289.975, 1))

    with pytest.raises(KeyError) as err:
        expr._format_temp(df_bad)
    err_msg = (
        "None of [['TC4', 'TC5', 'TC6', 'TC7', 'TC8', 'TC9', 'TC10', "
        "'TC11', 'TC12', 'TC13']] are in the [columns]"
        )
    assert err.value.args[0] == err_msg


def test__format_dew_point(df_01, df_bad):
    """Test _format_dew_point."""
    assert math.isclose(df_01.DewPoint[0], 259.04)
    assert math.isclose(df_01.DewPoint[100], 259.145)
    assert math.isclose(df_01.DewPoint[8000], 263.562)

    df_01 = expr._format_dew_point(df_01)
    for col in FORMAT_DP_STATS:
        assert math.isclose(
            df_01[col].count(), FORMAT_DP_STATS.loc['cnt', col]
            )
        assert math.isclose(df_01[col].sum(), FORMAT_DP_STATS.loc['sum', col])
        assert math.isclose(df_01[col].var(), FORMAT_DP_STATS.loc['var', col])
        assert math.isclose(df_01[col].mean(), FORMAT_DP_STATS.loc['avg', col])
        assert math.isclose(df_01[col].min(), FORMAT_DP_STATS.loc['min', col])
        assert math.isclose(df_01[col].max(), FORMAT_DP_STATS.loc['max', col])

    assert math.isclose(df_01.DewPoint[0], round(259.04, 1))
    assert math.isclose(df_01.DewPoint[100], round(259.145, 1))
    assert math.isclose(df_01.DewPoint[8000], round(263.562, 1))

    with pytest.raises(AttributeError) as err:
        expr._format_dew_point(df_bad)
    assert err.value.args[0] == (
        "'DataFrame' object has no attribute 'DewPoint'"
        )


def test__format_pressure(df_01, df_bad):
    """Test _format_pressure."""
    assert math.isclose(df_01.Pressure[0], 100156.841)
    assert math.isclose(df_01.Pressure[100], 100161.21800000001)
    assert math.isclose(df_01.Pressure[8000], 100266.27900000001)

    df_01 = expr._format_pressure(df_01)
    for col in FORMAT_P_STATS:
        assert math.isclose(df_01[col].count(), FORMAT_P_STATS.loc['cnt', col])
        assert math.isclose(df_01[col].sum(), FORMAT_P_STATS.loc['sum', col])
        assert math.isclose(df_01[col].var(), FORMAT_P_STATS.loc['var', col])
        assert math.isclose(df_01[col].mean(), FORMAT_P_STATS.loc['avg', col])
        assert math.isclose(df_01[col].min(), FORMAT_P_STATS.loc['min', col])
        assert math.isclose(df_01[col].max(), FORMAT_P_STATS.loc['max', col])

    assert math.isclose(df_01.Pressure[0], round(100156.841, 0))
    assert math.isclose(df_01.Pressure[100], round(100161.21800000001, 0))
    assert math.isclose(df_01.Pressure[8000], round(100266.27900000001, 0))

    with pytest.raises(AttributeError) as err:
        expr._format_pressure(df_bad)
    assert err.value.args[0] == (
        "'DataFrame' object has no attribute 'Pressure'"
        )


def test__add_avg_te(df_01, df_bad):
    """Test add_avg_te."""
    assert 'Te' not in set(df_01)
    purged = expr._add_avg_te(df_01.copy(), purge=True)
    for tc in TC_LIST:
        assert tc not in set(purged)
    assert 'Te' in set(purged)
    df_01 = expr._add_avg_te(df_01)
    assert 'Te' in set(df_01)

    for col in AVG_T_STATS:
        assert math.isclose(df_01[col].count(), AVG_T_STATS.loc['cnt', col])
        assert math.isclose(df_01[col].sum(), AVG_T_STATS.loc['sum', col])
        assert math.isclose(df_01[col].var(), AVG_T_STATS.loc['var', col])
        assert math.isclose(df_01[col].mean(), AVG_T_STATS.loc['avg', col])
        assert math.isclose(df_01[col].min(), AVG_T_STATS.loc['min', col])
        assert math.isclose(df_01[col].max(), AVG_T_STATS.loc['max', col])

    tc_keys = ['TC{}'.format(i) for i in range(4, 14)]
    mean = np.mean(df_01.loc[0, tc_keys])
    assert math.isclose(df_01.Te[0], round(mean, 1))

    with pytest.raises(KeyError) as err:
        expr._add_avg_te(df_bad)
    err_msg = (
        "None of [['TC4', 'TC5', 'TC6', 'TC7', 'TC8', 'TC9', 'TC10', "
        "'TC11', 'TC12', 'TC13']] are in the [columns]"
        )
    assert err.value.args[0] == err_msg

    if PLOT:
        plt.plot(df_01.loc[:, tc_keys], 'k')
        plt.plot(df_01.Te, 'r', label='Average Temperature')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('temperature/K')
        plt.title('Average Temperature: No Smoothing')
        plt.show()


def test__add_smooth_avg_te(df_01, df_bad):
    """Test _add_smooth_avg_te."""
    assert 'TeSmooth' not in set(df_01)
    purged = expr._add_smooth_avg_te(df_01.copy(), purge=True)
    assert 'Te' not in set(purged)
    assert 'TeSmooth' in set(purged)
    df_01 = expr._add_smooth_avg_te(df_01)
    assert 'TeSmooth' in set(df_01)

    with pytest.raises(AttributeError) as err:
        expr._add_smooth_avg_te(df_bad)
    assert err.value.args[0] == "'DataFrame' object has no attribute 'Te'"

    if PLOT:
        plt.plot(df_01.Te, label='before')
        plt.plot(df_01.TeSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('temperature/K')
        plt.title('Smoothed Average Temperature')
        plt.show()


def test__add_smooth_dew_point(df_01, df_bad):
    """Test _add_smooth_dew_point."""
    assert 'DewPointSmooth' not in set(df_01)
    purged = expr._add_smooth_dew_point(df_01.copy(), purge=True)
    assert 'DewPoint' not in set(purged)
    assert 'DewPointSmooth' in set(purged)
    df_01 = expr._add_smooth_dew_point(df_01)
    assert 'DewPointSmooth' in set(df_01)

    with pytest.raises(AttributeError) as err:
        expr._add_smooth_dew_point(df_bad)
    assert err.value.args[0] == ("'DataFrame' object has no attribute" +
                                 " 'DewPoint'")

    if PLOT:
        plt.plot(df_01.DewPoint, label='before')
        plt.plot(df_01.DewPointSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('Dew Point/K')
        plt.title('Smoothed Dew Point')
        plt.show()


def test__add_smooth_pressure(df_01, df_bad):
    """Test _add_smooth_pressure."""
    assert 'PressureSmooth' not in set(df_01)
    purged = expr._add_smooth_pressure(df_01.copy(), purge=True)
    assert 'Pressure' not in set(purged)
    assert 'PressureSmooth' in set(purged)
    df_01 = expr._add_smooth_pressure(df_01)
    assert 'PressureSmooth' in set(df_01)

    with pytest.raises(AttributeError) as err:
        expr._add_smooth_pressure(df_bad)
    assert err.value.args[0] == (
        "'DataFrame' object has no attribute 'Pressure'"
        )

    if PLOT:
        plt.plot(df_01.Pressure, label='before')
        plt.plot(df_01.PressureSmooth, label='smoothed')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('Pressure/Pa')
        plt.title('Smoothed Pressure')
        plt.show()


def test__get_coolprop_rh():
    """Test _get_rh."""
    rh = expr._get_coolprop_rh([101325, 290, 275])
    assert math.isclose(rh, 0.36377641815012024)


def test__get_coolprop_rh_err():
    """Test _get_coolprop_rh_err."""
    rh = expr._get_coolprop_rh_err([101325, 290, 275])
    assert math.isclose(rh, 0.00523992533195583, rel_tol=1e-06)
    rh = expr._get_coolprop_rh_err([70000, 290, 273])
    assert math.isclose(rh, 0.005145568640554932)


def test__multi_rh(df_01):
    """Test _multi_rh."""
    rh = expr._multi_rh(df_01, param_list=PARAM_LIST)
    for col in RH_STATS:
        assert math.isclose(rh.count(), RH_STATS.loc['cnt', col])
        assert math.isclose(rh.sum(), RH_STATS.loc['sum', col])
        assert math.isclose(rh.var(), RH_STATS.loc['var', col])
        assert math.isclose(rh.mean(), RH_STATS.loc['avg', col])
        assert math.isclose(rh.min(), RH_STATS.loc['min', col])
        assert math.isclose(rh.max(), RH_STATS.loc['max', col])

    if PLOT:
        plt.plot(rh, label='RH')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()


def test__multi_rh_err(df_01):
    """Test _multi_rh_err."""
    rh_err = expr._multi_rh_err(df_01, param_list=PARAM_LIST)
    for col in SIGRH_STATS:
        assert math.isclsoe(rh_err.count(), SIGRH_STATS.loc['cnt', col])
        assert math.isclose(rh_err.sum(), SIGRH_STATS.loc['sum', col])
        assert math.isclose(
            rh_err.var(),
            SIGRH_STATS.loc['var', col],
            rel_tol=1e-6
            )
        assert math.isclose(rh_err.mean(), SIGRH_STATS.loc['avg', col])
        assert math.isclose(rh_err.min(), SIGRH_STATS.loc['min', col])
        assert math.isclose(rh_err.max(), SIGRH_STATS.loc['max', col])

    if PLOT:
        plt.plot(rh_err, label='SigRH Function')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('SigRH')
        plt.title('Relative Humidity Error')
        plt.show()


def test__add_rh(df_01):
    """Test _add_rh."""
    assert 'RH' not in set(df_01)
    purged = expr._add_rh(df_01.copy(), purge=True)
    assert 'DewPointSmooth' not in set(purged)
    assert 'RH' in set(purged)
    df_01 = expr._add_rh(df_01)
    assert 'RH' in set(df_01)

    for col in RH_STATS_JOIN:
        assert math.isclose(df_01[col].count(), RH_STATS_JOIN.loc['cnt', col])
        assert math.isclose(df_01[col].sum(), RH_STATS_JOIN.loc['sum', col])
        assert math.isclose(
            df_01[col].var(),
            RH_STATS_JOIN.loc['var', col],
            rel_tol=1e-6
            )
        assert math.isclose(df_01[col].mean(), RH_STATS_JOIN.loc['avg', col])
        assert math.isclose(df_01[col].min(), RH_STATS_JOIN.loc['min', col])
        assert math.isclose(df_01[col].max(), RH_STATS_JOIN.loc['max', col])

    if PLOT:
        plt.errorbar(df_01.Idx, df_01.RH, yerr=df_01.SigRH, label='RH')

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()


def test__get_max_half_len(df_01):
    """Test _get_max_half_length."""
    max_window = expr._get_max_half_len(df_01, TARGET_IDX)
    assert max_window == (len(df_01)-1) - TARGET_IDX
    max_limit = expr._get_max_half_len(df_01, TARGET_IDX, max_=10)
    assert max_limit == 10

    fail_list = [0, -1, -2, len(df_01)-1, len(df_01), len(df_01)+1]

    for idx in fail_list:
        with pytest.raises(IndexError) as err:
            expr._get_max_half_len(df_01, idx)
        err_msg = (
            "no 'half length' available for the target index: "
            "target must have at least one element to right or left"
            )
        assert err.value.args[0] == err_msg


def test__get_rh_idx(df_01):
    """Test _get_rh_idx."""
    idx = expr._get_target_idx(df_01, TARGET_RH)
    assert idx == TARGET_IDX
    rh = df_01.RH[idx]
    assert math.isclose(rh, TARGET_RH, abs_tol=0.01)

    if PLOT:
        plt.plot(df_01.RH, label='RH', color='orange')
        plt.axvline(x=idx)
        plt.axhline(y=TARGET_RH)

        plt.legend()
        plt.xlabel('time/s')
        plt.ylabel('RH')
        plt.title('Relative Humidity')
        plt.show()


def test__get_stat_group(df_01):
    """Test _get_stat_group."""
    time, mass = expr._get_stat_group(df_01, TARGET_IDX, HALF_LEN)

    assert len(time) == 2*HALF_LEN + 1
    assert len(mass) == 2*HALF_LEN + 1

    if PLOT:
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


def test__get_valid_rh_targets(df_01):
    """Test _get_valid_rh_targets."""
    rh_list = expr._get_valid_rh_targets(df_01)
    assert rh_list == [0.1, 0.15]


def test__half_len_gen(df_01):
    """Test _half_len_gen."""
    half_len_list = list(
        expr._half_len_gen(df_01, TARGET_IDX, steps=1000)
    )

    assert half_len_list == (
        list(map(lambda x: x*1000, range(1, 8)))
        )

    gen_output = []
    for _ in range(3):
        for half_len in expr._half_len_gen(df_01, TARGET_IDX, steps=1000):
            gen_output.append(half_len)

    assert gen_output == 3*(
        list(map(lambda x: x*1000, range(1, 8)))
        )


def test_preprocess(df_01, df_01_original):
    """Test preprocess."""
    pd.testing.assert_frame_equal(expr.preprocess(df_01_original), df_01)


def test_mass_transfer(df_01):
    """Test _analysis."""
    df_res = expr.mass_transfer(df_01, sigma=SIGMA, steps=1000, plot=PLOT)
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


def test__get_df_row():
    """Test _get_df_row."""
    df_row = expr._get_df_row(RH_SET_DF)
    rh_row = RH_SET_DF[RH_SET_DF.index == Q_IDX]
    pd.testing.assert_frame_equal(df_row, rh_row)

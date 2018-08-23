"""
Plot the evaporation rate data from the RHTargets table for each test.

his script should be called as follows:

   $ python -m chamber.scripts.plot_res

Where the filepath is the tdms file to be quality checkd and database is the
name of the schema to insert the results into.
"""

import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib import rcParams
import numpy as np
import seaborn as sns

from chamber.data import dml
from chamber.data import sqldb
from chamber.scripts import db_check

TUBE_A = np.power(0.015, 2)*np.pi


ALL_P_T = ('SELECT DISTINCT Pressure, Temperature FROM RHTargets NATURAL JOIN '
           'Test NATURAL JOIN Setting')


def format_plot():
    """Format the plots."""
    sns.set_palette('colorblind')
    font = dict(family='Times New Roman',
                weight='normal',
                size=20)
    rc('font', **font)
    rcParams['figure.figsize'] = 6, 4
    rcParams['mathtext.fontset'] = 'stix'
    rcParams['font.size'] = 12
    rcParams['font.weight'] = 'normal'
    rcParams['axes.linewidth'] = 0.3
    rcParams['lines.linewidth'] = 1
    rcParams['errorbar.capsize'] = 2


def _get_tid_list(cur, p, t):
    """Prompt the user to get p and t setting."""
    tid_list = sqldb.get_high_low_testids(cur, p, t)
    return tid_list


def _check_reservoir(cur, tid):
    """Check if the reservoir was open for a TestId."""
    cur.execute(dml.get_reservoir.format(tid))
    return cur.fetchall()[0][0]


def _get_res_dict(cnx, tid_list):
    """Get a `dict` of result where each TestId is a key."""
    res_dict = dict()
    for tid in tid_list:
        res_dict['{}'.format(tid)] = sqldb.get_rht_results(cnx, tid)
    return res_dict


def _gen_plot(cnx, res_dict, p, t):
    """Plot the evaporation rate as a function of RH."""
    cur = cnx.cursor()
    for tid in res_dict.keys():
        rh_val = _check_reservoir(cur, tid)
        res_df = res_dict[tid]
        rh = res_df['RH']
        sig_rh = res_df['SigRH']
        b = -res_df['B']
        sig_b = res_df['SigB']
        mdpp = b/TUBE_A
        sig_mdpp = sig_b/TUBE_A
        plt.errorbar(rh, mdpp, xerr=3*sig_rh, yerr=3*sig_mdpp, fmt='.',
                     label='High RH' if rh_val == 1 else 'Low RH')
    plt.title(r"$\dot m$'' vs. RH at {0}kPa {1}K".format(int(p)//1000, t))
    plt.legend()
    plt.xlabel('RH')
    plt.ylabel(r"$\dot m''/(kg/m^2s)$")
    plt.grid()
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.show()


def _db_status_plot(cnx):
    """
    Plot the P vs. T settings for the tests in the MySQL database.

    Plot the Pressure vs. Temperature settings for the tests currently in the
    MySQL database. Also provides visual feedback denoting which tests are
    analyzed.

    Parameters
    ----------
    cnx : mysql.connector.connection.MySQLConnection
        Connection to MySQL database.

    Returns
    -------
    `True` or `None`
        `True` if sucessful, else `None`.

    Examples
    --------
    Get the TestIds that have been analyzed from the database.

    >>> cnx = connect('my-schema')
    >>> db_status_plot(cnx)
    True

    """
    t_max = 313.15
    gamma = 11.4
    p_not = 101325.0
    t = np.linspace(273, 312, 100)
    p = p_not*(t/t_max)**gamma
    plt.plot(t, p)
    sdf = db_check._get_setting_df(cnx)
    for pnt in db_check.PT_LIST:
        plt.plot(pnt[0], pnt[1], c='grey', marker='.')
    tid_df = db_check._get_analysis_tid_df(cnx)
    label_list = []
    for tid in sdf.TestId:
        if tid in sdf[sdf.TestId.isin(tid_df.TestId)].TestId.values:
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 1),
                        'Pressure'],
                c='blue', marker='+', s=300,
                label='HighRH A' if 'HighRH A' not in label_list else '')
            plt.scatter(
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Temperature'],
                sdf.loc[(sdf['TestId'] == tid) & (sdf['Reservoir'] == 0),
                        'Pressure'],
                c='orange', marker='x', s=250,
                label='LowRH A' if 'LowRH A' not in label_list else '')
            if 'HighRH A' not in label_list:
                label_list = label_list + ['HighRH A', 'LowRH A']
    plt.xlim(273, 312)
    plt.ylim(20000, 102000)
    plt.xlabel('T/K')
    plt.ylabel('P/Pa')
    plt.title('Tests In Database')
    plt.grid()
    plt.legend()
    plt.show()
    return True


def _plot_evap(cnx, p, t):
    """Get data to plot m-dot'' vs. RH and pass it on to plot function."""
    cur = cnx.cursor()
    tid_list = _get_tid_list(cur, p, t)
    res_dict = _get_res_dict(cnx, tid_list)
    _gen_plot(cnx, res_dict, p, t)


if __name__ == '__main__':
    print('Starting results plotting script...')
    format_plot()
    cnx = sqldb.connect('chamber')
    cur = cnx.cursor()
    plot = True
    while plot is True:
        _db_status_plot(cnx)
        p = input('Specify a pressure setting in kPa, "a" if all: ')
        t = input('Specify a temperature setting in K, "a" if all: ')
        if p == 'a' or t == 'a':
            cur.execute(ALL_P_T)
            p_t_list = [p_t for p_t in cur.fetchall()]
            for p_t in p_t_list:
                _plot_evap(cnx, p_t[0], p_t[1])
        else:
            _plot_evap(cnx, int(p)*1000, t)
        if input('Plot another setting? [y/n]') != 'y':
            plot = False
    print('End.')

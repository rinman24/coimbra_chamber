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

TUBE_A = np.power(0.015, 2)*np.pi


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


def get_tid_list(cur, p, t):
    """Prompt the user to get p and t setting."""
    tid_list = sqldb.get_high_low_testids(cur, p, t)
    return tid_list


def check_reservoir(cur, tid):
    """Check if the reservoir was open for a TestId."""
    cur.execute(dml.get_reservoir.format(tid))
    return cur.fetchall()[0][0]


def get_res_dict(cnx, tid_list):
    """Get a `dict` of result where each TestId is a key."""
    res_dict = dict()
    for tid in tid_list:
        res_dict['{}'.format(tid)] = sqldb.get_rht_results(cnx, tid)
    return res_dict


def plot_evap(cnx, res_dict, p, t):
    """Plot the evaporation rate as a function of RH."""
    cur = cnx.cursor()
    for tid in res_dict.keys():
        rh_val = check_reservoir(cur, tid)
        res_df = res_dict[tid]
        rh = res_df['RH']
        sig_rh = res_df['SigRH']
        b = -res_df['B']
        sig_b = res_df['SigB']
        mdpp = b/TUBE_A
        sig_mdpp = sig_b/TUBE_A
        plt.errorbar(rh, mdpp, xerr=3*sig_rh, yerr=3*sig_mdpp, fmt='.',
                     label='High RH' if rh_val == 1 else 'Low RH')
    plt.title(r"$\dot m$'' vs. RH at {0} kPa {1} K".format(int(p)//1000, t))
    plt.legend()
    plt.xlabel('RH')
    plt.ylabel(r"$\dot m''$")
    plt.grid()
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.show()


if __name__ == '__main__':
    print('Starting results plotting script...')
    format_plot()
    cnx = sqldb.connect('chamber')
    cur = cnx.cursor()
    plot = True
    while plot is True:
        p = input('Specify a pressure setting in Pa: ')
        t = input('Specify a temperature setting in K: ')
        tid_list = get_tid_list(cur, p, t)
        res_dict = get_res_dict(cnx, tid_list)
        plot_evap(cnx, res_dict, p, t)
        if input('Plot another setting? [y/n]') != 'y':
            plot = False
    print('End.')

from sys import argv

import matplotlib.pyplot as plt
from nptdms import TdmsFile
from numpy import array

from chamber.models import props
from chamber.data import sqldb


def get_tdms_obj(file_path):
    # Returns the nptdms.TdmsFile object generated from the argument file path
    print('Loading TDMS file...')
    tdms_obj = TdmsFile(file_path)
    print('TDMS file loaded.')
    return tdms_obj


def get_is_mass(tdms_obj):
    # Gets the IsMass value from a nptdms.TdmsFile object
    is_mass = tdms_obj.object('Settings', 'IsMass').data[0]
    return is_mass


def get_m_data(tdms_obj):
    # Gets the mass data from a nptdms.TdmsFile object if IsMass = 1
    m_data = tdms_obj.object('Data', 'Mass').data
    return m_data


def get_p_data(tdms_obj):
    # Gets the pressure data from a nptdms.TdmsFile object
    p_data = tdms_obj.object('Data', 'Pressure').data
    return p_data


def get_t_data(tdms_obj):
    # Gets the temperature data of the thermocouples
    # measureing chamber temperature
    t_data = array([tdms_obj.object(
        "Data", "TC{}".format(cpl_idx)).data for cpl_idx in range(4, 14)])
    return t_data


def get_t_dp_data(tdms_obj):
    # Gets the dewpoint data form a nptdms.TdmsFile object
    t_dp_data = tdms_obj.object('Data', 'DewPoint').data
    return t_dp_data


def get_rh_data(t_data, p_data, t_dp_data):
    # Uses props module to calculate the rh data
    t_data_avg = t_data.mean(axis=0)
    rh_data = props.get_rh(p_data, t_data_avg, t_dp_data)
    return rh_data


def plot_mass(m_data):
    # Plots mass vs time
    plt.plot(m_data, label='Mass ata')
    plt.xlabel('Time (s)')
    plt.ylabel('Mass (kg)')
    plt.title('Mass (kg) vs. Time (s)')
    plt.show()


def plot_rh_t_dp(rh_data, t_dp_data):
    # Plots Relative Humidity vs time and Dew Point vs time

    # Mass vs. time plot
    fig, ax1 = plt.subplots()
    ax1.plot(t_dp_data, 'r', label='Dew Point Data')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Dew Point Temperature (K)', color='r')
    ax1.tick_params('y', colors='r')

    # TH vs time plot plot
    ax2 = ax1.twinx()
    ax2.plot(rh_data, 'b', label='Relative Humidity Data')
    ax2.set_ylabel('Relative Humidity', color='b')
    ax2.tick_params('y', colors='b')

    plt.title('Dew Point Temperature (K) and Relative Humidity vs. Time (s)')
    plt.show()


def plot_t_p(t_data, p_data):
    # Plots temperature vs time and pressure vs time

    # Temperature vs time plot
    fig, ax1 = plt.subplots()
    for idx in range(10):
        ax1.plot(t_data[idx], label='Tcpl {}'.format(idx + 4))
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Temperature (K)', color='r')
    ax1.tick_params('y', colors='r')
    plt.legend(bbox_to_anchor=(0, -0.05), loc=2, ncol=5)

    # Pressure vs time plot
    ax2 = ax1.twinx()
    ax2.plot(p_data, 'b', label='Pressure Data')
    ax2.set_ylabel('Pressure (kPa)', color='b')
    ax2.tick_params('y', colors='b')

    plt.title('Temperature (K) and Pressure (kPa) vs. Time (s)')
    plt.show()


def make_plots(tdms_obj):
    # Gets data from a nptdms.TdmsFile and plots it using above functions
    print('Gathering data...')
    is_mass = get_is_mass(tdms_obj)
    if is_mass:
        m_data = get_m_data(tdms_obj)
    p_data = get_p_data(tdms_obj)
    t_data = get_t_data(tdms_obj)
    t_dp_data = get_t_dp_data(tdms_obj)
    rh_data = get_rh_data(t_data, p_data, t_dp_data)
    print('Data gathered.')

    print('Plotting...')
    if is_mass:
        plot_mass(m_data)
    plot_rh_t_dp(rh_data, t_dp_data)
    plot_t_p(t_data, p_data)


def add_to_database(tdms_obj):
    # Adds the test to the database from a nptdms.TdmsFile if user input is 'y'
    add_test = input('Add test to database? [y/n]')
    if add_test == 'y':
        print('Adding test...')
        cnx = sqldb.connect('test_results')
        sqldb.add_tdms_file(cnx, tdms_obj)
        print('Test added.')
    elif add_tets == 'n':
        print('Test not added.')
    else:
        add_to_database(tdms_obj)


def qc_check():
    # Creates a nptdms.TdmsFile object and calls the plot and adding functions
    tdms_obj = get_tdms_obj(argv[1])
    make_plots(tdms_obj)
    add_to_database(tdms_obj)


print('Starting QC check...')
qc_check()
print('QC check complete.')

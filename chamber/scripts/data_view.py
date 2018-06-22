# The goal of this script is to display a test's data (from tdms format) as a series of plots using matplotlib
from sys import argv

import matplotlib.pyplot as plt
from nptdms import TdmsFile
from numpy import array
import pandas as pd

from chamber.models import props

def get_m_data(tdms_obj):
	if tdms_obj.object('Settings', 'IsMass').data[0] == 1:
		m_data = tdms_obj.object('Data', 'Mass').data
		return m_data
	else:
		return array(False)


def get_p_data(tdms_obj):
	p_data = tdms_obj.object('Data', 'Pressure').data
	return p_data


def get_t_data(tdms_obj):
	t_data = array([tdms_obj.object(
		"Data", "TC{}".format(cpl_idx)).data for cpl_idx in range(4,14)])
	return t_data


def get_t_dp_data(tdms_obj):
	t_dp_data = tdms_obj.object('Data', 'DewPoint').data
	return t_dp_data


def get_rh_data(t_data, p_data, t_dp_data):
	t_data_avg = t_data.mean(axis=0)
	rh_data = props.get_rh(p_data, t_data_avg, t_dp_data)
	return rh_data


def plot_mass(m_data):
	plt.plot(m_data, label='Mass ata')
	plt.xlabel('Time (s)')
	plt.ylabel('Mass (kg)')
	plt.title('Mass (kg) vs. Time (s)')
	plt.show()


def plot_rh_t_dp(rh_data, t_dp_data):
	fig, ax1 = plt.subplots()
	ax1.plot(t_dp_data, 'r', label='Dew Point Data')
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Dew Point Temperature (K)', color='r')
	ax1.tick_params('y', colors='r')

	ax2 = ax1.twinx()
	ax2.plot(rh_data, 'b', label='Relative Humidity Data')
	ax2.set_ylabel('Relative Humidity', color='b')
	ax2.tick_params('y', colors='b')

	plt.title('Dew Point Temperature (K) and Relative Humidity vs. Time (s)')
	plt.show()


def plot_t_p(t_data, p_data):
	fig, ax1 = plt.subplots()
	for idx in range(10):
		ax1.plot(t_data[idx], label='Tcpl {}'.format(idx + 4))
	ax1.set_xlabel('Time (s)')
	ax1.set_ylabel('Temperature (K)', color='r')
	ax1.tick_params('y', colors='r')
	plt.legend(bbox_to_anchor=(0, -0.05), loc=2, ncol=5)

	ax2 = ax1.twinx()
	ax2.plot(p_data, 'b', label='Pressure Data')
	ax2.set_ylabel('Pressure (kPa)', color='b')
	ax2.tick_params('y', colors='b')

	plt.title('Temperature (K) and Pressure (kPa) vs. Time (s)')
	plt.show()


print('Starting QC check...')
print('Setting up file path...')
FILEPATH = argv[1]
print('File found.')

print('Loading tdms file...')
tdms_obj = TdmsFile(FILEPATH)
print('Tdms file loaded.')

print('Getting mass data...')
m_data = get_m_data(tdms_obj)
if m_data.any():
	print('Mass data found.')
else:
	print('IsMass = 0...no mass plot will be created.')

print('Getting pressure data...')
p_data = get_p_data(tdms_obj)
print('Pressure data found.')

print('Getting temperature data...')
t_data = get_t_data(tdms_obj)
print('Temperature data found.')

print('Getting dew point temperature data...')
t_dp_data = get_t_dp_data(tdms_obj)
print('Dew Point temperature data found.')

print('Calculating relative humidity data...')
rh_data = get_rh_data(t_data, p_data, t_dp_data)
print('Relative humidity data calculated.')

print('Plotting ', FILEPATH, ' data...')

if m_data.any():
	print('Plotting mass...')
	plot_mass(m_data)
	print('Mass plot closed.')

print('Plotting relative humidity and dew point temperature...')
plot_rh_t_dp(rh_data, t_dp_data)
print('Relative humidity and dew point plot closed.')

print('Plotting temperatures and pressure...')
plot_t_p(t_data, p_data)
print('Temperature and pressure plot closed.')
print('QC check complete.')

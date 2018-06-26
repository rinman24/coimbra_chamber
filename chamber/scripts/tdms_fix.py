# This script takes a command line argument of a directory in which
# you want all the tdms files to be edited.
from numpy import array
import os
from re import compile
from sys import argv

from nptdms import TdmsWriter, ChannelObject, types


def list_tdms(file_path, file_list=None):
	# Finds all teh .tdms files in the argument directory
	# and returns them as a list of strings
	if file_list is None:
		file_list = []
	try:
		for file_name in os.listdir(file_path):
			list_tdms(os.path.join(file_path, file_name), file_list)
	except NotADirectoryError:
		regex = compile(r".tdms$")
		if regex.search(file_path):
			return file_list.append(file_path)
	return file_list


def get_rh(file_path):
	# Returns the value of RH 1 for HighRH, 0 for LowRH
	# False if RH not found in title
	re_high = compile(r'HighRH')
	re_low = compile(r'LowRH')
	if re_high.search(file_path):
		return 1
	elif re_low.search(file_path):
		return 0
	else:
		print('Error with {}. Could not find RH setting in file path.'.format(file_path))
		return False


def get_channel_obj(rh):
	# Returns the channel object for the RH
	channel_obj = ChannelObject('Settings', 'RH', array([rh]),
		properties={'datatype': types.DoubleFloat(rh)})
	return channel_obj


def append_file(file_path, channel_obj):
	# Appends the RH to othe existing TDMS files
	with TdmsWriter(str(file_path), mode='a') as tdms_writer:
		tdms_writer.write_segment([channel_obj])


def fix_tdms(directory):
	# Get list of file paths (str)
	file_list = list_tdms(directory)
	for file_path in file_list:
		print('Fixing {}'.format(file_path))
		rh = get_rh(file_path)
		if isinstance(rh, int):
			print('Added in {0} rh = {1}.'.format(file_path, rh))
			channel_obj = get_channel_obj(rh)
			append_file(file_path, channel_obj)


# Get the directory from command line argument
directory = argv[1]
fix_tdms(directory)

from os import listdir
from re import compile

from nptdms import TdmsFile

def list_tdms(file_path):
    """Returns a list of the .tdms files contained within the argument file."""
    regex = compile(".tdms")
    file_list = [file for file in listdir(file_path) if regex.match(file, len(file)-5)]
    return file_list

def get_settings(tdms_obj):
    """returns a dictionary of the initial state of Tests in the TdmsFile object argument"""
    settings = {'initial_dew_point': tdms_obj.object("Data", "DewPoint").data[0],
        'initial_duty': tdms_obj.object("Data", "DutyCycle").data[0],
        'initial_mass': tdms_obj.object("Data", "Mass").data[0],
        'initial_pressure': tdms_obj.object("Data", "Pressure").data[0],
        'initial_temp': sum(tdms_obj.object("Data", "TC{}".format(x)).data[0] for x in range(3,14))/11
        }
    return settings

def get_tests(tdms_obj):
    """returns a dictionary of the initial state of Settings in the TdmsFile object argument"""
    tests = { 'author': "", 'date_time': tdms_obj.object().properties['DateTime'],
        'description': "", 'time_step': tdms_obj.object("Settings", "TimeStep").data[0]
        }

    for name, value in tdms_obj.object().properties.items():
        if name == "author":
            tests['author'] = value
        if name == "description":
            tests['description'] = value
    return tests

def get_obs(tdms_obj, idx):
	"""returns a dictionary of strings derived from tdms object observation data"""
    observations = {'cap_man_ok': str(tdms_obj.object("Data", "CapManOk").data[idx]),
        'dew_point': str(tdms_obj.object("Data", "DewPoint").data[idx]),
        'duty_cycle': str(tdms_obj.object("Data", "DutyCycle").data[idx]),
        'idx': str(tdms_obj.object("Data", "Idx").data[idx]),
        'mass': str(tdms_obj.object("Data", "Mass").data[idx]),
        'optidew_ok': str(tdms_obj.object("Data", "OptidewOk").data[idx]),
        'pow_out': str(tdms_obj.object("Data", "PowOut").data[idx]),
        'pow_ref': str(tdms_obj.object("Data", "PowRef").data[idx]),
        'pressure': str(tdms_obj.object("Data", "Pressure").data[idx]),
        }
    return observations

def get_temp(tdms_obj, idx):
	"""returns a dictionary of strings derived from tdms object temperature data"""
    temp = {'TC_num': str(idx), 'temp': str(tdms_obj.object("Data", "TC{}".format(idx)).data[idx])}
    return temp
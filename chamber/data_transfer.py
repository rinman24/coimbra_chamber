import pandas as pd
from os import listdir
from re import compile
from nptdms import TdmsFile

FILE_PATH = ""

def list_tdms(file_path):
    """Returns a list of the .tdms files contained within the argument file."""
    FILE_PATH = file_path
    file_list = []
    regex = compile(".tdms")
    for file in listdir(file_path):
        if regex.match(file, len(file) - len(".tdms")):
            file_list.append(file)
    return file_list

def get_settings(tdms_obj):
	"""returns a dictionary of the initial state of Tests in the TdmsFile object argument"""
    df = pd.DataFrame({chan.channel:chan.data for chan in tdms_obj.group_channels('Data')})

    settings = {'initial_dew_point': df.DewPoint[0], 'initial_duty': df.DutyCycle[0], 'initial_mass': df.Mass[0]
                , 'initial_pressure': df.Pressure[0], 'initial_temp': sum([df['TC'+str(i)][0] for i in range(14)])/14
               }
    
    return settings

def get_tests(tdms_obj): 
	"""returns a dictionary of the initial state of Settings in the TdmsFile object argument"""
    tests = { 'author': "", 'date_time': tdms_obj.object().properties['DateTime']
             , 'description': "", 'time_step': tdms_obj.object("Settings", "TimeStep").data
            }

    for name,value in tdms_obj.object().properties.items():
    	if name == "author":
    		tests['author'] = value
    	if name == "description":
    		tests['description'] = value
    return tests

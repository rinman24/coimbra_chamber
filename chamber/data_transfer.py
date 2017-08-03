from os import listdir
from re import compile

def list_tdms(file_path):
    """Returns a list of the .tdms files contained within the argument file."""
    file_list = []
    regex = compile(".tdms")
    for file in listdir(file_path):
        if regex.match(file, len(file) - len(".tdms")):
            file_list.append(file)
    return file_list
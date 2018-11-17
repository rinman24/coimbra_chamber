"""Analysis engine module."""

import nptdms


def _get_tdms_objs(filepath):
    tdms_file = nptdms.TdmsFile(filepath)
    settings_obj = tdms_file.object('Settings').as_dataframe()
    data_obj = tdms_file.object('Data').as_dataframe()
    return settings_obj, data_obj

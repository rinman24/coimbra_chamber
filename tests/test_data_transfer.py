from datetime import datetime
from os import listdir

import pytest
import pytz

import chamber.data_transfer as data_transfer

CORRECT_FILE_LIST = ["test.tdms", "unit_test_01.tdms", "unit_test_02.tdms",
    "unit_test_03.tdms"
    ]
INCORRECT_FILE_LIST = ["py.tdmstest", "py.tdmstest.py", "unit_test_01.tdms_index",
    "unit_test_02.tdms_index", "unit_test_03.tdms_index"
    ]
TDMS_TEST_FILES = ["tests/data_transfer_test_files/tdms_test_files/tdms_test_file_01.tdms",
    "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_02.tdms",
    "tests/data_transfer_test_files/tdms_test_files/tdms_test_file_03.tdms"
    ]
TDMS_01_DICT_SETS = {'initial_dew_point': 292.501, 'initial_duty': 0, 'initial_mass': -0.0658138,
    'initial_pressure': 99977, 'initial_temp': (297.302+297.27
    +297.284+296.835+296.753+297.094+297.054+296.928+296.86+297.318+297.325)/11
    }
TDMS_01_DICT_TESTS = {'author': "ADL", 'date_time': datetime(2017, 8, 3, 19, 33, 9, 217290, pytz.UTC),
    'description': "This is at room temperature, pressure, no laser power, study of boundy development.",
    'time_step': 1
    }
    
@pytest.fixture(scope='module')
def test_tdms_obj():
    """fixture to instantiate only one TdmsFile object for testing"""
    return TdmsFile(TDMS_TEST_FILES[0])


class TestSqlDb(object):
    """Unit testing of data_transfer.py."""
    
    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument file."""
        files = data_transfer.list_tdms("tests/data_transfer_test_files")

        for file in INCORRECT_FILE_LIST:
            assert file not in files
        for file in CORRECT_FILE_LIST:
            assert file in files

    def test_get_settings(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for settings"""
        assert TDMS_01_DICT_SETS == data_transfer.get_settings(test_tdms_obj)

    def test_get_tests(self, test_tdms_obj):
        """Test correct dictionary output when reading .tdms files for tests"""
        assert TDMS_01_DICT_TESTS == data_transfer.get_tests(test_tdms_obj)
    
    def test_fixture(self, test_tdms_obj):
        """Test existence of test_tdms_obj fixture"""
        assert test_tdms_obj

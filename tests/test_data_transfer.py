import pytest
import chamber.data_transfer as data_transfer

CORRECT_FILE_LIST = ["test.tdms", "unit_test_01.tdms", "unit_test_02.tdms",
                     "unit_test_03.tdms", ".tdms"]
INCORRECT_FILE_LIST = ["py.tdmstest", "py.tdmstest.py",
                       "unit_test_01.tdms_index", "unit_test_02.tdms_index", "unit_test_03.tdms_index"]

class TestSqlDb(object):
    """Unit testing of data_transfer.py."""
    
    def test_list_tdms(self):
        """Test correct output of all .tdms files contained in argument file."""
        files = data_transfer.list_tdms("tests/data_transfer_test_files")
        for file in INCORRECT_FILE_LIST:
            assert file not in files
        for file in CORRECT_FILE_LIST:
            assert file in files

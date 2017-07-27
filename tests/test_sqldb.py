"""Docstring."""

import chamber.sqldb as sqldb

class TestSqlDb(object):
    """Unit testing of sqldb.py."""

    def test_connection(self):
        """Test connection to the MySQL database."""
        cnx = sqldb.connect_sqldb()
        assert cnx
        cnx.close()
        
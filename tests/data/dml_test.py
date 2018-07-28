"""MySQL DDL constants for testing."""

# ----------------------------------------------------------------------------
# Test general table statistics
get_stats_test_id = ('SELECT COUNT({0}), SUM({0}), VARIANCE({0}), AVG({0}),'
                     ' MIN({0}), MAX({0}) FROM {2} WHERE TestId={1}')

get_bit_stats = ('SELECT COUNT({0}), SUM({0}), VARIANCE({0}), AVG({0}), '
                 'MIN(CAST({0} AS UNSIGNED)), MAX(CAST({0} AS UNSIGNED)) '
                 'FROM {2} WHERE TestId={1}')

get_stats_gen = ('SELECT COUNT({0}), SUM({0}), VARIANCE({0}), AVG({0}),'
                 ' MIN({0}), MAX({0}) FROM {1}')

# ----------------------------------------------------------------------------
# Test add_tube_info ddl
get_tube = 'SELECT * FROM Tube'

get_test = 'SELECT * FROM Test WHERE TestID={}'

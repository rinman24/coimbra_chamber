@echo off
echo Running unit test suite...
python -m pytest -k "unit" -xvs --cov-report html --cov=chamber --ignore=tests_depreciated\
echo Testing complete.
 
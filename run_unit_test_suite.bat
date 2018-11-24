@echo off
echo Running unit test suite...
python -m pytest -k "unit" -x --cov-report html --cov=chamber --ignore=tests_depreciated\ --pdb
echo Testing complete.
 
@echo off
echo Running unit test suite...
python -m pytest -k "unit" -x --cov-config .coveragerc --cov=chamber chamber/tests --cov-report html -p no:warnings --ignore=tests_depreciated\
echo Testing complete.
 
@echo off
echo Running integration test suite...
python -m pytest -k "integration" -xvs --cov-report html --cov=chamber --ignore=tests_depreciated\
echo Testing complete.
 
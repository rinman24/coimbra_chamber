@echo off
echo Running integration test suite...
python -m pytest -k "integration" -vs --cov-report html --cov=chamber --ignore=tests_depreciated\
echo Testing complete.
 
@echo off
echo Running integration test suite...
python -m pytest -k "integration" -vs --cov-report html --cov=chamber -p no:warnings --ignore=tests_depreciated\
echo Testing complete.
 
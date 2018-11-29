@echo off
echo Running unit test suite...
python -m pytest -k "unit" -x --cov-report html --cov=chamber --ignore=tests_depreciated\ --pdb -p no:warnings
echo Testing complete.
 
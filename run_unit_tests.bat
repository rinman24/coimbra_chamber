@echo off
title Run pytest unit test suite
echo Attempting to run unit tests...
echo Simulated tests...
python -m pytest -k "unit"
echo Testing complete.
pause

 
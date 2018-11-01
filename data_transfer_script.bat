@echo off
title Python Data Transfer
echo Creating anaconda environment...
call \Users\Jocelyn\Anaconda3\Scripts\activate.bat
echo Environment creation sucessful.
echo Starting python script runner.py...
python \ucsd_ch\chamber\runner.py "\Users\Jocelyn\Desktop\Data Logger - Networked\Data" %*
pause
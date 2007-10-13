rem Batch file for creating py2exe executable for Harvestman
rem Note that this requires the latest version of py2exe i.e,
rem 0.6.1 upwards.
@echo off
python install.py py2exe -O2 --bundle 

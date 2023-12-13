@echo off
setlocal enabledelayedexpansion

set "venv_name=vincent"

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

if "%OS%"=="Windows_NT" (
  set "bat_found=0"
  set "env_found=0"

  for %%p in (
    "C:\ProgramData\miniconda3"
    "C:\ProgramData\Anaconda3"
    "C:\ProgramData\.conda"
    "%UserProfile%\miniconda3"
    "%UserProfile%\.conda"
    "%UserProfile%\Anaconda3"
  ) do (
      if exist "%%~p\envs\%venv_name%" (
          set "env_path=%%~p\envs\%venv_name%"
          set "env_found=1"
      )
      if exist "%%~p\Scripts\activate.bat" (
          set "bat_path=%%~p\Scripts\activate.bat"
          set "bat_found=1"
      )
  )

  if !bat_found!==0 (
      echo activate.bat not found in any of the specified paths.
      echo Please rerun setup.bat to install Miniconda3.
      pause
      exit
  )

  if !env_found!==0 (
      echo Environment %venv_name% not found in any of the specified paths.
      echo Please rerun setup.bat to install Miniconda3.
      pause
      exit 
  )

  set activate_cmd="!bat_path!" "!env_path!"

) else (
  set "conda_path=$HOME/miniconda3"
  set "activate_cmd=source $conda_path/bin/activate %venv_name%"
)

echo %activate_cmd%

REM activate TAN environment
echo Activating virtual environment...
call %activate_cmd%

echo Virtual environment (%venv_name%) activated

echo Running program...
"%CONDA_PREFIX%\python.exe" "%TAN_dir%main.py"

if "%OS%"=="Windows_NT" pause
else read -p "Press [Enter] key to continue..."

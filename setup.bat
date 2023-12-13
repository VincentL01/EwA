@echo off
setlocal enabledelayedexpansion

set "python_version=3.9.13"
set "venv_name=vincent"

REM set TAN_dir to current directory
set "TAN_dir=%~dp0"

if "%OS%"=="Windows_NT" (
  set "miniconda_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
  set "miniconda_installer=%~dp0Miniconda3-latest-Windows-x86_64.exe"
) else (
  set "miniconda_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
  set "miniconda_installer=%~dp0Miniconda3-latest-MacOSX-x86_64.sh"
)

REM if not exists anaconda or miniconda, install
set "conda_path="
set "bat_found=0"

for %%p in (
  "C:\ProgramData\miniconda3"
  "C:\ProgramData\Anaconda3"
  "C:\ProgramData\.conda"
  "%UserProfile%\miniconda3"
  "%UserProfile%\.conda"
  "%UserProfile%\Anaconda3"
) do (
  if exist "%%~p\Scripts\activate.bat" (
    set "conda_path=%%~p"
    set "bat_found=1"
  )
)

if !bat_found!==0 (
  echo Downloading Miniconda...
  powershell.exe -Command "(New-Object System.Net.WebClient).DownloadFile('%miniconda_url%', '%miniconda_installer%')"

  echo Installing Miniconda...
  start /wait "" "%miniconda_installer%" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%UserProfile%\miniconda3

  set "conda_path=%UserProfile%\miniconda3"
) else (
  echo Anaconda or Miniconda already installed
)

if exist "!conda_path!\envs\%venv_name%" (
  echo %venv_name% already exists
) else (
  echo %venv_name% not found
  echo Creating virtual environment with Python %python_version%...
  call !conda_path!\Scripts\conda create -n %venv_name% python==%python_version% -y
)

echo Activating virtual environment... at !conda_path!\envs\%venv_name%
call !conda_path!\Scripts\activate.bat %venv_name%

echo Installing TAN requirements
cd %TAN_dir%
pip install -r requirements.txt
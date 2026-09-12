@echo off
setlocal
if exist "%~dp0moneydance_update.config.bat" call "%~dp0moneydance_update.config.bat"
if not defined MD_JAVA set "MD_JAVA=C:\Program Files\Moneydance\jre\bin\java.exe"
if not defined MD_LIB set "MD_LIB=C:\Program Files\Moneydance\lib\*"
if not defined MD_RUNNER set "MD_RUNNER=%~dp0moneydance_production_run.py"
if not defined MD_CSV_PATH (
  echo Set MD_CSV_PATH to the Amazon export CSV path.
  exit /b 2
)
if not defined MD_BOOK_FOLDER (
  echo Set MD_BOOK_FOLDER to the Moneydance book folder.
  exit /b 2
)
if not defined MD_LOG_PATH set "MD_LOG_PATH=%TEMP%\moneydance_update.log"

set "PS_CMD=$p=Read-Host 'Trying to open \"%MD_BOOK_FOLDER%\", please enter the password' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($p); try {[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) | & '%MD_JAVA%' '-Djava.awt.headless=true' '-Dpython.cachedir.skip=true' '-cp' '%MD_LIB%' 'org.python.util.jython' '-B' '%MD_RUNNER%' '%MD_CSV_PATH%' '%MD_BOOK_FOLDER%' '%MD_LOG_PATH%'} finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "%PS_CMD%"
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%

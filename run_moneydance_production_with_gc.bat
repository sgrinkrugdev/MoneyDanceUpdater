@echo off
setlocal EnableDelayedExpansion
if exist "%~dp0moneydance_update.config.bat" call "%~dp0moneydance_update.config.bat"
if not defined MD_JAVA set "MD_JAVA=C:\Program Files\Moneydance\jre\bin\java.exe"
if not defined MD_LIB set "MD_LIB=C:\Program Files\Moneydance\lib\*"
if not defined MD_GC_CSV_PATH set "MD_GC_CSV_PATH=D:\Downloads\amazon-gift-card-transactions.csv"
if not defined MD_GC_RUNNER set "MD_GC_RUNNER=%~dp0moneydance_gc_production_run.py"
if not defined MD_RUNNER set "MD_RUNNER=%~dp0moneydance_production_run.py"
if not defined MD_GC_ON_IMPORT_ISSUES set "MD_GC_ON_IMPORT_ISSUES=prompt"
if not defined MD_LOG_PATH set "MD_LOG_PATH=%TEMP%\moneydance_update.log"
if not defined MD_BOOK_FOLDER (
  echo Set MD_BOOK_FOLDER to the Moneydance book folder.
  exit /b 2
)
if not defined MD_CSV_PATH (
  echo Set MD_CSV_PATH to the Amazon order export CSV path.
  exit /b 2
)

set "PS_GC=$p=Read-Host 'Trying to open \"%MD_BOOK_FOLDER%\", please enter the password' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($p); try {[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) | & '%MD_JAVA%' '-Djava.awt.headless=true' '-Dpython.cachedir.skip=true' '-cp' '%MD_LIB%' 'org.python.util.jython' '-B' '%MD_GC_RUNNER%' '%MD_GC_CSV_PATH%' '%MD_BOOK_FOLDER%' '%MD_LOG_PATH%'} finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "%PS_GC%"
set "GC_EXIT=%ERRORLEVEL%"
if not "%GC_EXIT%"=="0" exit /b %GC_EXIT%

findstr /C:"\"INVALID\"" /C:"\"FAILED\"" "%MD_GC_CSV_PATH%" >nul 2>nul
if "%ERRORLEVEL%"=="0" (
  if /I "%MD_GC_ON_IMPORT_ISSUES%"=="abort" exit /b 3
  if /I "%MD_GC_ON_IMPORT_ISSUES%"=="prompt" (
    choice /C YN /M "Gift Card import reported INVALID or FAILED rows. Continue to Amazon memo matcher"
    if errorlevel 2 exit /b 3
  )
)

call "%~dp0run_moneydance_production.bat"
exit /b %ERRORLEVEL%
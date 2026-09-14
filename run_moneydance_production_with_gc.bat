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

set "PS_CMD=$p=Read-Host 'Trying to open \"%MD_BOOK_FOLDER%\", please enter the password' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($p); $plain=$null; try {$plain=[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b); $plain | & '%MD_JAVA%' '-Djava.awt.headless=true' '-Dpython.cachedir.skip=true' '-cp' '%MD_LIB%' 'org.python.util.jython' '-B' '%MD_GC_RUNNER%' '%MD_GC_CSV_PATH%' '%MD_BOOK_FOLDER%' '%MD_LOG_PATH%'; $gcExit=$LASTEXITCODE; if($gcExit -ne 0){exit $gcExit}; $issues=$false; if(Test-Path '%MD_GC_CSV_PATH%'){$text=Get-Content -Raw '%MD_GC_CSV_PATH%'; $issues=($text -match '\"INVALID\"' -or $text -match '\"FAILED\"')}; if($issues){ if('%MD_GC_ON_IMPORT_ISSUES%' -ieq 'abort'){exit 3}; if('%MD_GC_ON_IMPORT_ISSUES%' -ieq 'prompt'){$answer=Read-Host 'Gift Card import reported INVALID or FAILED rows. Continue to Amazon memo matcher? [Y/N]'; if($answer -notmatch '^[Yy]'){exit 3}}}; $plain | & '%MD_JAVA%' '-Djava.awt.headless=true' '-Dpython.cachedir.skip=true' '-cp' '%MD_LIB%' 'org.python.util.jython' '-B' '%MD_RUNNER%' '%MD_CSV_PATH%' '%MD_BOOK_FOLDER%' '%MD_LOG_PATH%'; exit $LASTEXITCODE} finally {if($b -ne [IntPtr]::Zero){[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}; $plain=$null}"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "%PS_CMD%"
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%
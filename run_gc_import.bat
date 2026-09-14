@echo off
setlocal
if exist "%~dp0moneydance_update.config.bat" call "%~dp0moneydance_update.config.bat"
if not defined MD_JAVA set "MD_JAVA=C:\Program Files\Moneydance\jre\bin\java.exe"
if not defined MD_LIB set "MD_LIB=C:\Program Files\Moneydance\lib\*"
if not defined MD_GC_CSV_PATH set "MD_GC_CSV_PATH=D:\Downloads\amazon-gift-card-transactions.csv"
if not defined MD_GC_DRY_RUN set "MD_GC_DRY_RUN=true"
if not defined MD_GC_ACCOUNT_NAME set "MD_GC_ACCOUNT_NAME=Amazon Gift Card"
if not defined MD_GC_CATEGORY_NAME set "MD_GC_CATEGORY_NAME=Uncategorized"
if not "%~1"=="" set "MD_GC_CSV_PATH=%~1"
if not "%~2"=="" set "MD_BOOK_FOLDER=%~2"
if not defined MD_BOOK_FOLDER (
  echo Set MD_BOOK_FOLDER to the Moneydance book folder, or pass it as the second argument.
  exit /b 2
)
set "MD_RUNNER=%~dp0moneydance_gc_import_run.py"
"%MD_JAVA%" -Djava.awt.headless=true -Dpython.cachedir.skip=true -cp "%MD_LIB%" org.python.util.jython -B "%MD_RUNNER%" "%MD_GC_CSV_PATH%" "%MD_BOOK_FOLDER%"
set "EXIT_CODE=%ERRORLEVEL%"
exit /b %EXIT_CODE%
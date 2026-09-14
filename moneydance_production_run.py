"""Production Moneydance runner.

Usage:
  java ... org.python.util.jython -B moneydance_production_run.py CSV MONEYDANCE LOG

The password is read from standard input and is never written to disk.
"""
from __future__ import print_function
import json
import os
import sys
import subprocess
from com.moneydance.security import SecretKeyCallback
from java.lang import Exception as JavaException
from java.lang import System as JavaSystem
from java.io import FileOutputStream, OutputStream, PrintStream
import moneydance_single_record as updater
import moneydance_headless_test as runner

def project_version():
    from moneydance_version import VERSION
    return VERSION

if len(sys.argv) != 4:
    raise RuntimeError('Usage: moneydance_production_run.py CSV_PATH MONEYDANCE_FOLDER LOG_PATH')

updater.CSV_PATH = os.path.abspath(sys.argv[1])
updater.TEST_FOLDER = os.path.abspath(sys.argv[2])
updater.AUTHORIZED_ONLY = False
LOG_PATH = os.path.abspath(sys.argv[3])
log_dir = os.path.dirname(LOG_PATH)
if log_dir and not os.path.isdir(log_dir):
    os.makedirs(log_dir)

class JavaTeeOutputStream(OutputStream):
    def __init__(self, screen, log):
        self.screen, self.log = screen, log
    def write(self, value, offset=None, length=None):
        if offset is None:
            self.screen.write(value); self.log.write(value); return
        for index in range(offset, offset + length):
            self.screen.write(value[index]); self.log.write(value[index])
    def flush(self):
        self.screen.flush(); self.log.flush()

log_file = FileOutputStream(LOG_PATH, False)
java_tee = PrintStream(JavaTeeOutputStream(JavaSystem.out, log_file), True, 'UTF-8')
JavaSystem.setOut(java_tee); JavaSystem.setErr(java_tee)
original_stdout, original_stderr = sys.stdout, sys.stderr

class Tee(object):
    def write(self, text):
        if not isinstance(text, str): text = str(text)
        java_tee.print(text)
        java_tee.flush()
    def flush(self):
        java_tee.flush()

sys.stdout = Tee(); sys.stderr = Tee()
print('MoneyDanceUpdate version=%s' % project_version())

class Password(SecretKeyCallback):
    def __init__(self, value): self.value = value
    def getPassphrase(self, *args): return self.value
    def setVerifier(self, verifier): pass

password = Password(sys.stdin.readline().rstrip('\r\n'))
try:
    processes = subprocess.check_output(['tasklist.exe', '/FI', 'IMAGENAME eq Moneydance.exe', '/FO', 'CSV', '/NH'])
    if 'moneydance.exe' in processes.lower():
        raise RuntimeError('MONEYDANCE_OPEN: Close Moneydance completely before running this utility. Moneydance can overwrite this headless update if it remains open.')
    result = runner.run(updater.TEST_FOLDER, password)
    print('FINAL_LOG_SUMMARY_BEGIN')
    print(json.dumps(result, indent=2))
    print('FINAL_LOG_SUMMARY_END')
    counters = result.get('counters', {})
    print('FINAL_COUNTERS_BEGIN')
    print('  "counters": {')
    counter_names = ('edited', 'ambiguous', 'unsafe', 'unmatched', 'total', 'mismatch')
    for index, name in enumerate(counter_names):
        comma = ',' if index < len(counter_names) - 1 else ''
        print('    "%s": %s%s' % (name, counters.get(name, 0), comma))
    print('  },')
    print('  "edited_by_account": {')
    edited_by_account = result.get('edited_by_account', {})
    account_names = sorted(edited_by_account.keys())
    for index, account_name in enumerate(account_names):
        comma = ',' if index < len(account_names) - 1 else ''
        print('    "%s": %s%s' % (account_name.replace('"', '\\"'), edited_by_account.get(account_name, 0), comma))
    print('  }')
    print('FINAL_COUNTERS_END')
except (Exception, JavaException) as error:
    runner.report_failure(error)
    if isinstance(error, (RuntimeError, ValueError, TypeError, AttributeError)):
        print(str(error))
    sys.exit(1)
finally:
    password.value = None
    sys.stdout, sys.stderr = original_stdout, original_stderr
    java_tee.flush(); log_file.close()

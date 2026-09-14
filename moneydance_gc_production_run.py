# -*- coding: utf-8 -*-
"""Production runner for Amazon Gift Card import."""
from __future__ import print_function
import json

import os
import sys
import subprocess
from java.lang import Exception as JavaException
from com.moneydance.security import SecretKeyCallback
from java.lang import System as JavaSystem
from java.io import FileOutputStream, OutputStream, PrintStream

import moneydance_gift_card_import as importer
import moneydance_gc_import_run as gc_runner
import moneydance_headless_test as runner


def project_version():
    from moneydance_version import VERSION
    return VERSION


if len(sys.argv) != 4:
    raise RuntimeError('Usage: moneydance_gc_production_run.py GC_CSV_PATH MONEYDANCE_FOLDER LOG_PATH')

CSV_PATH = os.path.abspath(sys.argv[1])
BOOK_FOLDER = os.path.abspath(sys.argv[2])
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


log_file = FileOutputStream(LOG_PATH, True)
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


class Password(SecretKeyCallback):
    def __init__(self, value): self.value = value
    def getPassphrase(self, *args): return self.value
    def setVerifier(self, verifier): pass


sys.stdout = Tee(); sys.stderr = Tee()
print('MoneyDanceUpdate Gift Card import version=%s' % project_version())
password = Password(sys.stdin.readline().rstrip('\r\n'))
try:
    processes = subprocess.check_output(['tasklist.exe', '/FI', 'IMAGENAME eq Moneydance.exe', '/FO', 'CSV', '/NH'])
    if 'moneydance.exe' in processes.lower():
        raise RuntimeError('MONEYDANCE_OPEN: Close Moneydance completely before running this utility. Moneydance can overwrite this headless update if it remains open.')
    result = gc_runner.run(CSV_PATH, BOOK_FOLDER, password)
    counts = result.get('counts', {})
    problem_count = int(counts.get(importer.IMPORT_INVALID, 0)) + int(counts.get(importer.IMPORT_FAILED, 0))
    if problem_count:
        print('GIFT_CARD_IMPORT_ISSUES=%s' % problem_count)
    print('FINAL_GIFT_CARD_LOG_SUMMARY_BEGIN')
    print(json.dumps(result, indent=2, sort_keys=True))
    print('FINAL_GIFT_CARD_LOG_SUMMARY_END')
except (Exception, JavaException) as error:
    runner.report_failure(error)
    if isinstance(error, (RuntimeError, ValueError, TypeError, AttributeError)):
        print(str(error))
    sys.exit(1)
finally:
    password.value = None
    sys.stdout, sys.stderr = original_stdout, original_stderr
    java_tee.flush(); log_file.close()

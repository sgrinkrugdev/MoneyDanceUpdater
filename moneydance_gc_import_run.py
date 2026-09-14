# -*- coding: utf-8 -*-
"""Headless runner for Amazon Gift Card import into Moneydance."""
from __future__ import print_function

import json
import os
import subprocess
import sys

from java.lang import Exception as JavaException
from com.moneydance.security import SecretKeyCallback

import moneydance_gift_card_import as importer
import moneydance_headless_test as runner
from moneydance_local_password import LocalPassword

STAGE = 'startup'


def stage(name):
    global STAGE
    STAGE = name


class NoPassword(SecretKeyCallback):
    def getPassphrase(self, *args):
        return ''

    def setVerifier(self, verifier):
        pass


def report_failure(error):
    print('FAILED stage=%s type=%s' % (STAGE, type(error).__name__))
    runner.report_failure(error)


def run(csv_path, folder, callback):
    csv_path = os.path.abspath(csv_path)
    folder = os.path.abspath(folder)
    importer.CSV_PATH = csv_path
    importer.BOOK_FOLDER = folder
    stage('read_csv')
    rows = importer.read_csv(csv_path)
    column_errors = importer.validate_columns(rows)
    if column_errors:
        raise RuntimeError('; '.join(column_errors))
    stage('load')
    wrapper, book = runner.load(folder, callback)
    if importer.DRY_RUN:
        stage('dry_run')
        result = importer.dry_run(csv_path, rows, book)
        print(json.dumps(result, indent=2, sort_keys=True))
        return result
    stage('apply_import')
    inserted, backup = importer.apply_import(csv_path, rows, book, folder)
    book = None
    wrapper = None
    stage('reopen')
    wrapper, reopened = runner.load(folder, callback)
    stage('verify_after_reopen')
    account_balance = importer.verify_after_reopen(reopened, inserted, rows, csv_path)
    result = importer.summary(rows, inserted, dry_run=False, account_balance_cents=account_balance, backup=backup)
    dry_json, dry_csv, summary_path = importer.report_paths(csv_path)
    importer.write_json(summary_path, result)
    result['summary_report_path'] = summary_path
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == '__main__':
    processes = subprocess.check_output(['tasklist.exe', '/FI', 'IMAGENAME eq Moneydance.exe', '/FO', 'CSV', '/NH'])
    if 'moneydance.exe' in processes.lower():
        raise RuntimeError('Close Moneydance completely before running this utility')
    if len(sys.argv) != 3:
        raise RuntimeError('Usage: moneydance_gc_import_run.py CSV_PATH MONEYDANCE_FOLDER')
    use_no_password = os.environ.get('MD_NO_PASSWORD', '').lower() in ('1', 'true', 'yes')
    password = NoPassword() if use_no_password else LocalPassword()
    try:
        if not use_no_password:
            password.read(sys.argv[2])
        run(sys.argv[1], sys.argv[2], password)
    except RuntimeError as error:
        message = str(error)
        if message.startswith(('PASSWORD_MISMATCH:', 'UNLOCK_PASSWORD_REJECTED:', 'UNLOCK_FAILED:')):
            print(message)
        else:
            report_failure(error)
        sys.exit(1)
    except (Exception, JavaException) as error:
        report_failure(error)
        sys.exit(1)
    finally:
        if hasattr(password, 'clear'):
            password.clear()
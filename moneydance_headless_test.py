"""Single-record run against the authorized closed test file or a workspace copy."""
from __future__ import print_function
import json
import os
import re
import sys
from java.io import File
from com.moneydance.apps.md.controller import AccountBookWrapper, MDException, Main
from java.lang import Exception as JavaException
from com.moneydance.apps.md.controller.io import AccountBookUtil
from java.util import ArrayList
import moneydance_single_record as updater
from moneydance_local_password import LocalPassword
STAGE = 'startup'

def stage(name):
    global STAGE
    STAGE = name

def report_failure(error):
    # Print type and code locations only, never exception values or locals.
    import traceback
    print('FAILED stage=%s type=%s' % (STAGE, type(error).__name__))
    for filename, line, function, source in traceback.extract_tb(sys.exc_info()[2]):
        print('  %s:%s (%s)' % (os.path.basename(filename), line, function))
    if isinstance(error, JavaException):
        print('  java_type=%s' % error.getClass().getName())
        for frame in list(error.getStackTrace())[:4]:
            print('  %s.%s:%s' % (frame.getClassName(), frame.getMethodName(), frame.getLineNumber()))
    print('No password or exception message included. Do not assume rollback.')

def load(folder, callback):
    # Standalone library use has no UI-initialized internal storage directory.
    # Configure this process only; no preferences or installed-app state changed.
    containers = ArrayList()
    containers.add(File(os.path.dirname(folder)))
    AccountBookUtil.INTERNAL_FOLDER_CONTAINERS = containers
    app = Main()
    Main.main(['-d', '-v'])
    app.DEBUG = True
    app.initializeApp(app.getPlatformHelper(), File(folder))
    wrapper = AccountBookWrapper.wrapperForFolder(File(folder))
    try:
        initialized = wrapper.loadLocalStorage(callback)
    except MDException as error:
        if error.getCode() == MDException.WRONG_DECRYPTION_PASSWORD:
            raise RuntimeError('UNLOCK_PASSWORD_REJECTED: Moneydance rejected the password. No transaction edit attempted.')
        raise RuntimeError('UNLOCK_FAILED: Moneydance error code %d. No transaction edit attempted.' % error.getCode())
    if not initialized:
        raise RuntimeError('Storage initialization failed; encryption level=%s. No update attempted.' % wrapper.getEncryptionLevel())
    if not wrapper.loadDataModel(callback):
        raise RuntimeError('Cannot load data model')
    # Moneydance 2024.4 may leave the root account lazy when no UI book is set.
    book = wrapper.getBook()
    book.doInitialLoad(wrapper.isMasterSyncNode())
    book.setFinishedInitialLoad(True)
    return wrapper, book

def run(folder, callback):
    root = os.path.realpath(os.path.join(os.path.dirname(__file__), 'moneydance_test_copies'))
    folder = os.path.realpath(folder)
    is_test = os.path.normcase(folder) == os.path.normcase(updater.TEST_FOLDER)
    if updater.AUTHORIZED_ONLY and not is_test and (not folder.startswith(root + os.sep) or not folder.endswith('.moneydance')):
        raise RuntimeError('Only the authorized test file or workspace test copies are accepted')
    stage('load')
    wrapper, book = load(folder, callback)
    stage('read_csv')
    rows = updater.read_csv(updater.CSV_PATH)
    stage('match')
    plan = updater.plan_all(book, rows, folder)
    stage('snapshot_before')
    before = updater.snapshot(book)
    stage('apply_and_verify')
    result = updater.apply_all(book, rows, plan, folder)
    book = None
    wrapper = None
    stage('reopen')
    wrapper, reopened = load(folder, callback)
    stage('verify_disk')
    for item in plan['plan']:
        saved = reopened.getItemForID(item['txn_id'])
        actual_memo = saved.getMemo() if saved is not None else None
        expected_prefix = item['row']['Item description'] + ' AI_MEMO_'
        memo_ok = (saved is not None and actual_memo == item['expected_memo'])
        # A transaction may already have a valid AI_MEMO timestamp from an
        # earlier run. Accept it only when it belongs to this CSV item.
        if saved is not None and actual_memo is not None:
            memo_ok = memo_ok or bool(re.match(
                r'^' + re.escape(expected_prefix) + r'[0-9]{12}$', actual_memo))
        if not memo_ok:
            raise RuntimeError('Disk Memo verification failed for CSV row %s transaction %s; '
                               'expected=%r actual=%r' %
                               (item.get('row_index'), item.get('txn_id'),
                                item['expected_memo'], actual_memo))
        if saved.getDescription() != item['description']:
            raise RuntimeError('Disk Description verification failed for CSV row %s transaction %s' %
                               (item.get('row_index'), item.get('txn_id')))
    repeat = updater.plan_all(reopened, rows, folder, plan['suffix'])
    if any(x['memo_before'] != x['expected_memo'] for x in repeat['plan']):
        raise RuntimeError('Repeat run was not idempotent')
    verified_indexes = set(item['row_index'] for item in plan['plan'])
    for index, row in enumerate(rows):
        row['MD Verify'] = 'Y' if index in verified_indexes else 'N'
    updater.write_csv(updater.CSV_PATH, rows)
    result['csv_verification_writeback'] = 'PASS'
    result['disk_reopen_verification'] = 'PASS'
    result['repeat_run_verification'] = 'PASS'
    return result

if __name__ == '__main__':
    # A separate Moneydance process could overwrite changes from this utility.
    import subprocess
    processes = subprocess.check_output(['tasklist.exe', '/FI', 'IMAGENAME eq Moneydance.exe', '/FO', 'CSV', '/NH'])
    if 'moneydance.exe' in processes.lower():
        raise RuntimeError('MONEYDANCE_OPEN: Close Moneydance completely before running this utility. Moneydance can overwrite this headless update if it remains open.')
    password = LocalPassword()
    try:
        password.read()
        result = run(sys.argv[1], password)
        print(json.dumps(result, indent=2))
    except RuntimeError as error:
        # Only our own fixed diagnostics; never print a library exception message.
        message = str(error)
        if message.startswith(('PASSWORD_MISMATCH:', 'UNLOCK_PASSWORD_REJECTED:', 'UNLOCK_FAILED:')):
            print(message)
        else:
            report_failure(error)
        sys.exit(1)
    except (Exception, JavaException) as error:
        # Never emit arbitrary library exceptions which could include secrets.
        report_failure(error)
        sys.exit(1)
    finally:
        password.clear()

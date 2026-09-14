# -*- coding: utf-8 -*-
"""Amazon Gift Card CSV importer for Moneydance. Jython 2.7 compatible."""
from __future__ import print_function

import csv
import io
import json
import ntpath
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CSV_PATH = os.environ.get('MD_GC_CSV_PATH') or os.environ.get('MD_CSV_PATH', '')
BOOK_FOLDER = os.environ.get('MD_BOOK_FOLDER', '')
TARGET_ACCOUNT_NAME = os.environ.get('MD_GC_ACCOUNT_NAME', 'Amazon Gift Card')
CATEGORY_NAME = os.environ.get('MD_GC_CATEGORY_NAME', 'Uncategorized')
DRY_RUN = os.environ.get('MD_GC_DRY_RUN', 'true').lower() not in ('0', 'false', 'no')
DRY_RUN_REPORT_PATH = os.environ.get('MD_GC_DRY_RUN_REPORT_PATH', '')
SUMMARY_REPORT_PATH = os.environ.get('MD_GC_SUMMARY_REPORT_PATH', '')
CHECK_NUMBER_LIMIT = int(os.environ.get('MD_GC_CHECK_NUMBER_LIMIT', '30'))
UPDATE_CSV_IN_DRY_RUN = os.environ.get('MD_GC_UPDATE_CSV_IN_DRY_RUN', 'false').lower() in ('1', 'true', 'yes')

REQUIRED_COLUMNS = ('Date', 'Amount', 'Description', 'Balance', 'Source fingerprint', 'Amazon Verify')
STATUS_COLUMNS = ('MD Import', 'MD Verify', 'MD Failure reason')
IMPORT_IMPORTED = 'IMPORTED'
IMPORT_DRY_RUN_READY = 'DRY_RUN_READY'
IMPORT_DUP_CSV = 'SKIPPED_DUPLICATE_IN_CSV'
IMPORT_DUP_MD = 'SKIPPED_DUPLICATE_IN_MD'
IMPORT_INVALID = 'INVALID'
IMPORT_FAILED = 'FAILED'
VERIFY_VERIFIED = 'VERIFIED'
VERIFY_NOT_VERIFIED = 'NOT_VERIFIED'
VERIFY_NA = 'NOT_APPLICABLE'


def timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def read_csv(path):
    if sys.version_info[0] == 2:
        with open(path, 'rb') as stream:
            reader = csv.DictReader(stream)
            return [dict((k.decode('utf-8-sig'), v.decode('utf-8')) for k, v in row.items()) for row in reader]
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def fieldnames(rows):
    fields = []
    for row in rows:
        for key in row.keys():
            if key not in fields:
                fields.append(key)
    for key in STATUS_COLUMNS:
        if key not in fields:
            fields.append(key)
    return fields


def write_csv_atomic(path, rows):
    fields = fieldnames(rows)
    tmp = path + '.tmp'
    if sys.version_info[0] == 2:
        with open(tmp, 'wb') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            for row in rows:
                encoded = {}
                for field in fields:
                    value = row.get(field, '')
                    encoded[field] = value.encode('utf-8') if isinstance(value, unicode) else str(value).encode('utf-8')
                writer.writerow(encoded)
    else:
        with io.open(tmp, 'w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            for row in rows:
                writer.writerow(dict((field, row.get(field, '')) for field in fields))
    if os.path.exists(path):
        os.replace(tmp, path) if sys.version_info[0] >= 3 else shutil.move(tmp, path)
    else:
        shutil.move(tmp, path)


def backup_csv(path):
    backup = path + '.' + timestamp() + '.bak'
    shutil.copy2(path, backup)
    return backup


def write_json(path, data):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    with io.open(path, 'w', encoding='utf-8') as stream:
        stream.write(unicode(json.dumps(data, indent=2, sort_keys=True)) if sys.version_info[0] == 2 else json.dumps(data, indent=2, sort_keys=True))


def fnv1a_32(value):
    result = 2166136261
    for char in value:
        result ^= ord(char)
        result = (result * 16777619) & 0xffffffff
    return ('%08x' % result)


def source_fingerprint(row):
    return fnv1a_32('|'.join([row.get('Date', ''), row.get('Description', ''), str(row.get('Amount', '')), str(row.get('Balance', ''))]))


def parse_decimal(value, field):
    try:
        return Decimal(str(value).strip().replace('$', '').replace(',', '')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, AttributeError):
        raise ValueError('Invalid %s value %r' % (field, value))


def cents(value):
    return int((parse_decimal(value, 'Amount') * Decimal('100')).to_integral_value(rounding=ROUND_HALF_UP))


def date_int(value):
    text = (value or '').strip()
    try:
        if '-' in text:
            parts = text.split('-')
            return int('%04d%02d%02d' % (int(parts[0]), int(parts[1]), int(parts[2])))
        parts = text.replace('.', '/').split('/')
        return int('%04d%02d%02d' % (int(parts[2]) + (2000 if len(parts[2]) == 2 else 0), int(parts[0]), int(parts[1])))
    except Exception:
        raise ValueError('Invalid Date value %r' % value)


def validate_columns(rows):
    if not rows:
        return ['CSV has no rows']
    missing = [name for name in REQUIRED_COLUMNS if name not in rows[0]]
    return ['Missing required column %s' % name for name in missing]


def set_status(row, import_status, verify_status, reason=''):
    row['MD Import'] = import_status
    row['MD Verify'] = verify_status
    row['MD Failure reason'] = reason


def validate_row(row):
    if row.get('Amazon Verify', '').strip().upper() != 'VERIFIED':
        return 'AMAZON_NOT_VERIFIED: Amazon Verify is %r' % row.get('Amazon Verify', '')
    if not row.get('Balance', '').strip():
        return 'MISSING_BALANCE: Balance is blank'
    expected = source_fingerprint(row)
    actual = row.get('Source fingerprint', '').strip()
    if actual != expected:
        return 'FINGERPRINT_MISMATCH: expected %s got %s' % (expected, actual)
    if len(actual) > CHECK_NUMBER_LIMIT:
        return 'FINGERPRINT_TOO_LONG: %s chars exceeds limit %s' % (len(actual), CHECK_NUMBER_LIMIT)
    try:
        date_int(row.get('Date', ''))
        cents(row.get('Amount', ''))
        parse_decimal(row.get('Balance', ''), 'Balance')
    except ValueError as error:
        return 'INVALID: %s' % error
    return ''


def walk_accounts(root):
    yield root
    for child in root.getSubAccounts():
        for account in walk_accounts(child):
            yield account


def account_by_name(book, account_name):
    matches = [account for account in walk_accounts(book.getRootAccount()) if account.getAccountName() == account_name]
    if len(matches) != 1:
        raise RuntimeError('Expected exactly one account named %s; found %s' % (account_name, len(matches)))
    return matches[0]


def optional_account_by_name(book, account_name):
    matches = [account for account in walk_accounts(book.getRootAccount()) if account.getAccountName() == account_name]
    if len(matches) > 1:
        raise RuntimeError('Expected at most one account named %s; found %s' % (account_name, len(matches)))
    return matches[0] if matches else None


def assert_expected_book(book, expected_folder):
    actual = str(book.getRootFolder().getCanonicalPath())
    if ntpath.normcase(ntpath.normpath(actual)) != ntpath.normcase(ntpath.normpath(expected_folder)):
        raise RuntimeError('Wrong file: %s; expected %s' % (actual, expected_folder))
    return actual


def md_amount_cents(row):
    source_cents = cents(row.get('Amount', ''))
    transaction_type = (row.get('Transaction type', '') or '').strip().lower()
    visible_amount = (row.get('Visible amount', '') or '').strip()
    if transaction_type == 'charge' or visible_amount.startswith('-'):
        return -abs(source_cents)
    if transaction_type == 'refund':
        return abs(source_cents)
    return source_cents


def existing_fingerprints(book, account):
    result = {}
    for txn in book.getTransactionSet().getTransactionsForAccount(account):
        check = (txn.getCheckNumber() or '').strip()
        if check:
            result.setdefault(check, []).append(txn)
    return result


def existing_balance_cents(book, account):
    total = 0
    for txn in book.getTransactionSet().getTransactionsForAccount(account):
        total += int(txn.getValue())
    return total


def build_txn(book, account, category, row):
    from com.infinitekind.moneydance.model import AbstractTxn, ParentTxn, SplitTxn
    amount = md_amount_cents(row)
    txn = ParentTxn(book)
    txn.setAccount(account)
    txn.setDateInt(date_int(row.get('Date', '')))
    txn.setDescription(row.get('Description', ''))
    txn.setMemo('')
    txn.setCheckNumber(row.get('Source fingerprint', '').strip())
    split = SplitTxn.makeSplitTxn(txn, amount, 1.0, category, '', 0, AbstractTxn.STATUS_UNRECONCILED)
    txn.addSplit(split)
    return txn


def verify_txn(txn, row, account_name, category_name):
    if txn is None:
        return 'Inserted transaction not found after reopen'
    if txn.getAccount().getAccountName() != account_name:
        return 'Account mismatch'
    if int(txn.getDateInt()) != date_int(row.get('Date', '')):
        return 'Date mismatch'
    if int(txn.getValue()) != md_amount_cents(row):
        return 'Amount mismatch: %s expected %s' % (txn.getValue(), md_amount_cents(row))
    if txn.getDescription() != row.get('Description', ''):
        return 'Description mismatch'
    if (txn.getCheckNumber() or '') != row.get('Source fingerprint', '').strip():
        return 'Check# fingerprint mismatch'
    return ''


def plan_rows(rows, existing=None):
    existing = existing or {}
    seen = set()
    planned = []
    for index, row in enumerate(rows):
        fingerprint = row.get('Source fingerprint', '').strip()
        reason = validate_row(row)
        if reason:
            set_status(row, IMPORT_INVALID, VERIFY_NOT_VERIFIED, reason)
        elif fingerprint in seen:
            set_status(row, IMPORT_DUP_CSV, VERIFY_NA, 'DUPLICATE_IN_CSV: Source fingerprint already appeared earlier in this CSV')
        elif fingerprint in existing:
            md_matches = existing[fingerprint]
            mismatch = []
            for txn in md_matches:
                if int(txn.getDateInt()) != date_int(row.get('Date', '')) or int(txn.getValue()) != md_amount_cents(row) or txn.getDescription() != row.get('Description', ''):
                    mismatch.append(txn)
            if mismatch:
                set_status(row, IMPORT_FAILED, VERIFY_NOT_VERIFIED, 'FINGERPRINT_MISMATCH: existing Moneydance Check# matches but date, amount, or description differs')
            else:
                set_status(row, IMPORT_DUP_MD, VERIFY_NA, 'DUPLICATE_IN_MD: Source fingerprint already exists in Moneydance Check#')
        else:
            set_status(row, IMPORT_DRY_RUN_READY if DRY_RUN else '', VERIFY_NA if DRY_RUN else '', '')
            planned.append((index, row))
        if fingerprint:
            seen.add(fingerprint)
    return planned


def report_paths(csv_path):
    base = os.path.splitext(csv_path)[0]
    stamp = timestamp()
    dry_base = DRY_RUN_REPORT_PATH or (base + '-import-dry-run')
    if dry_base.lower().endswith('.json'):
        dry_base = dry_base[:-5]
    summary = SUMMARY_REPORT_PATH or (base + '-import-summary-' + stamp + '.json')
    return dry_base + '-' + stamp + '.json', dry_base + '-' + stamp + '.csv', summary


def dry_run(csv_path, rows, book=None):
    existing = {}
    account_balance = None
    if book is not None:
        account = account_by_name(book, TARGET_ACCOUNT_NAME)
        existing = existing_fingerprints(book, account)
        account_balance = existing_balance_cents(book, account)
    planned = plan_rows(rows, existing)
    dry_json, dry_csv, summary_path = report_paths(csv_path)
    report = summary(rows, planned, dry_run=True, account_balance_cents=account_balance)
    write_json(dry_json, report)
    write_csv_atomic(dry_csv, rows)
    if UPDATE_CSV_IN_DRY_RUN:
        write_csv_atomic(csv_path, rows)
    return report


def apply_import(csv_path, rows, book, expected_folder):
    assert_expected_book(book, expected_folder)
    account = account_by_name(book, TARGET_ACCOUNT_NAME)
    category = optional_account_by_name(book, CATEGORY_NAME)
    if category is None:
        raise RuntimeError('CATEGORY_MISSING: configured category %s was not found; Moneydance API requires a real category/split account and blank category transactions are deleted as invalid on reopen' % CATEGORY_NAME)
    existing = existing_fingerprints(book, account)
    planned = plan_rows(rows, existing)
    backup = backup_csv(csv_path)
    inserted = []
    for index, row in planned:
        try:
            txn = build_txn(book, account, category, row)
            txn.setEditingMode()
            if not txn.syncItem():
                raise RuntimeError('syncItem failed')
            if not book.save():
                raise RuntimeError('book.save failed')
            book.saveTrunkFile()
            if not book.save():
                raise RuntimeError('final book.save failed')
            row['_md_transaction_id'] = str(txn.getUUID())
            set_status(row, IMPORT_IMPORTED, VERIFY_NOT_VERIFIED, '')
            inserted.append((index, row, str(txn.getUUID())))
            write_csv_atomic(csv_path, rows)
        except Exception as error:
            set_status(row, IMPORT_FAILED, VERIFY_NOT_VERIFIED, 'WRITE_FAILED: %s' % str(error))
            write_csv_atomic(csv_path, rows)
    return inserted, backup


def verify_after_reopen(book, inserted, rows, csv_path):
    account_balance = None
    try:
        account = account_by_name(book, TARGET_ACCOUNT_NAME)
        account_balance = existing_balance_cents(book, account)
    except Exception:
        pass
    for index, row, txn_id in inserted:
        txn = book.getItemForID(txn_id)
        reason = verify_txn(txn, row, TARGET_ACCOUNT_NAME, CATEGORY_NAME)
        if reason:
            set_status(row, IMPORT_IMPORTED, VERIFY_NOT_VERIFIED, reason)
        else:
            set_status(row, IMPORT_IMPORTED, VERIFY_VERIFIED, '')
    write_csv_atomic(csv_path, rows)
    return account_balance


def summary(rows, planned, dry_run, account_balance_cents=None, backup=None):
    counts = defaultdict(int)
    for row in rows:
        counts[row.get('MD Import', '') or 'PENDING'] += 1
    last_balance = None
    for row in rows:
        if row.get('Balance', '').strip():
            last_balance = cents(row.get('Balance', ''))
            break
    balance_check = None
    if account_balance_cents is not None and last_balance is not None:
        balance_check = dict(moneydance_cents=account_balance_cents, amazon_cents=last_balance,
                             matches=(account_balance_cents == last_balance))
    return dict(dry_run=dry_run, csv_path=CSV_PATH, target_account=TARGET_ACCOUNT_NAME,
                category=CATEGORY_NAME, planned_rows=len(planned), counts=dict(counts),
                balance_check=balance_check, backup=backup, rows=rows)


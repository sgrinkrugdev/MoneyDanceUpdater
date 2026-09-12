# -*- coding: utf-8 -*-
"""Single-record Moneydance updater. Defaults to preview; Jython 2.7."""
from __future__ import print_function
import csv
import io
import ntpath
import os
import re
from collections import defaultdict
import sys
from datetime import date, datetime
from decimal import Decimal

CSV_PATH = os.environ.get('MD_CSV_PATH', '')
TEST_FOLDER = os.environ.get('MD_BOOK_FOLDER', '')
AUTHORIZED_ONLY = os.environ.get('MD_AUTHORIZED_ONLY', 'true').lower() not in ('0', 'false', 'no')
ACCOUNT_NAME = os.environ.get('MD_ACCOUNT_NAME', '')
CARD_NAMES = tuple(x.strip() for x in os.environ.get('MD_CARD_NAMES', '').split('|') if x.strip())
EXPLICIT_CARD_ACCOUNTS = dict(
    part.split('=', 1) for part in os.environ.get('MD_CARD_ACCOUNT_MAP', '').split(';')
    if '=' in part
)

def run_suffix():
    return ' AI_MEMO_' + datetime.now().strftime('%y%m%d%H%M%S')

def csv_date(value):
    """US numeric dates (month first), ISO dates, and English month names."""
    text = (value or '').strip()
    parts = re.split(r'[\s,./-]+', text)
    months = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
    full_months = ('january february march april may june july august '
                   'september october november december').split()
    month_numbers = dict((name, index + 1) for index, name in enumerate(months))
    month_numbers.update((name, index + 1) for index, name in enumerate(full_months))
    try:
        if len(parts) != 3:
            raise ValueError()
        first, second, year = parts
        if first.lower() in month_numbers:
            month, day = month_numbers[first.lower()], int(second)
        elif second.lower() in month_numbers:
            day, month = int(first), month_numbers[second.lower()]
        elif len(first) == 4:
            year, month, day = first, int(second), int(year)
        else:
            month, day = int(first), int(second)
        if len(year) not in (2, 4) or not year.isdigit():
            raise ValueError()
        year_number = int(year) + (2000 if len(year) == 2 else 0)
        return date(year_number, month, day)
    except (ValueError, TypeError):
        raise ValueError('Invalid CSV date %r; use US month/day/year, '
                         'YYYY-MM-DD, or an English month name' % value)

def read_csv(path):
    if sys.version_info[0] == 2:
        with open(path, 'rb') as stream:
            return [dict((k.decode('utf-8-sig'), v.decode('utf-8'))
                         for k, v in row.items()) for row in csv.DictReader(stream)]
    with io.open(path, 'r', encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def write_csv(path, rows):
    """Write the CSV back with the MD Match result column populated."""
    fields = list(rows[0].keys()) if rows else ['MD Match']
    if 'MD Match' not in fields:
        fields.append('MD Match')
    with open(path, 'wb') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            encoded = {}
            for field in fields:
                value = row.get(field, '')
                if isinstance(value, unicode):
                    encoded[field] = value.encode('utf-8')
                else:
                    encoded[field] = str(value).encode('utf-8')
            writer.writerow(encoded)

def generated_memo(memo):
    return bool(memo and re.search(r' AI_MEMO_[0-9]{12}$', memo))

def generated_memo_for_item(memo, item_description):
    """Return true only when the generated Memo belongs to this CSV item."""
    return bool(memo and item_description and
                re.match(r'^' + re.escape(item_description) + r' AI_MEMO_[0-9]{12}$', memo))

def csv_key(row):
    amount = Decimal(row['Order amount']).quantize(Decimal('0.01'))
    return (csv_date(row['Date']).isoformat(), format(abs(amount), '.2f'),
            'refund' if amount < 0 else 'charge')

def amount_matches_moneydance(value, csv_amount):
    """Credit-card charges are negative in Moneydance; refunds are positive."""
    amount = Decimal(csv_amount).quantize(Decimal('0.01'))
    moneydance_amount = Decimal(str(value)) / Decimal('100')
    return (abs(moneydance_amount).quantize(Decimal('0.01')) == abs(amount)
            and ((amount >= 0 and moneydance_amount < 0) or
                 (amount < 0 and moneydance_amount > 0)))

def target_row(rows):
    """Compatibility helper for the original single-record test."""
    found = [r for r in rows if r['Overall Result'].strip().upper() != 'MISMATCH'
             and r['Credit card'] in CARD_NAMES and csv_date(r['Date']) == date(2026, 6, 10)
             and Decimal(r['Order amount']) == Decimal('44.32')
             and r['Item description'] == 'Temptations Cat Treats Seafood']
    if len(found) != 1: raise ValueError('Expected exactly one eligible target CSV row; found %s' % len(found))
    return found[0]

def walk_accounts(root):
    yield root
    for child in root.getSubAccounts():
        for account in walk_accounts(child):
            yield account

def card_last4(card_name):
    match = re.search(r'(\d{4})\s*$', (card_name or '').strip())
    return match.group(1) if match else None

def account_candidates(accounts, card_name):
    """Resolve a CSV card to Moneydance accounts by card last four digits."""
    last4 = card_last4(card_name)
    if not last4:
        return []
    explicit = EXPLICIT_CARD_ACCOUNTS.get(last4)
    if explicit:
        return [a for a in accounts if a.getAccountName() == explicit]
    return [a for a in accounts if re.search(r'\d{4}\s*$', a.getAccountName() or '')
            and card_last4(a.getAccountName()) == last4]

def preview(book, rows, expected_folder=TEST_FOLDER):
    from com.infinitekind.moneydance.model import ParentTxn
    if book is None:
        raise ValueError('No Moneydance file is open')
    folder = str(book.getRootFolder().getCanonicalPath())
    if ntpath.normcase(ntpath.normpath(folder)) != ntpath.normcase(ntpath.normpath(expected_folder)):
        raise ValueError('Wrong file: %s; expected %s' % (folder, expected_folder))
    row = target_row(rows)
    accounts = list(walk_accounts(book.getRootAccount()))
    account_matches = account_candidates(accounts, row['Credit card'])
    if len(account_matches) != 1:
        raise ValueError('Expected one account for card %s; found %s' %
                         (row['Credit card'], len(account_matches)))
    account = account_matches[0]
    currency = account.getCurrencyType()
    if currency.getIDString() != 'USD' or currency.getDecimalPlaces() != 2:
        raise ValueError('Expected USD with two decimal places')
    matches = []
    for txn in book.getTransactionSet().getTransactionsForAccount(account):
        encoded = int(txn.getDateInt())
        txn_date = date(encoded // 10000, (encoded // 100) % 100, encoded % 100)
        # Purchases are negative in the credit-card account, not abs(value).
        if txn.getValue() == -4432 and abs((txn_date - TARGET_DATE).days) <= 3:
            matches.append(txn)
    if len(matches) != 1:
        return {'status': 'unmatched' if not matches else 'ambiguous',
                'matches': len(matches), 'edited': 0}
    txn = matches[0]
    if not isinstance(txn, ParentTxn):
        return {'status': 'unsafe', 'reason': 'Account is on split side', 'edited': 0}
    return {'status': 'eligible', 'edited': 0, 'file': folder,
            'account': ACCOUNT_NAME, 'transaction_id': str(txn.getUUID()),
            'date': int(txn.getDateInt()), 'amount': '44.32',
            'description': txn.getDescription(), 'memo_before': txn.getMemo(),
            'memo_proposed': row['Item description'] + run_suffix()}

def plan_all(book, rows, expected_folder=TEST_FOLDER, suffix=None):
    """Build a complete, side-effect-free plan for the CSV."""
    from com.infinitekind.moneydance.model import ParentTxn
    folder = str(book.getRootFolder().getCanonicalPath())
    if ntpath.normcase(ntpath.normpath(folder)) != ntpath.normcase(ntpath.normpath(expected_folder)):
        raise ValueError('Wrong file: %s; expected %s' % (folder, expected_folder))
    accounts = list(walk_accounts(book.getRootAccount()))
    txn_rows = []
    transactions_by_account = {}
    for account in accounts:
        account_id = str(account.getUUID())
        transactions_by_account[account_id] = []
        for txn in book.getTransactionSet().getTransactionsForAccount(account):
            encoded = int(txn.getDateInt())
            txn_date = date(encoded // 10000, (encoded // 100) % 100, encoded % 100)
            transactions_by_account[account_id].append((txn, txn_date, txn.getValue()))
    # For repeated exact date/amount groups, pair rows and transactions as a
    # group. This makes a 2-CSV/2-Moneydance group safely processable even when
    # the individual descriptions cannot distinguish the two transactions.
    csv_groups = defaultdict(list)
    for row_index, row in enumerate(rows):
        if row.get('Overall Result', '').strip().upper() == 'MISMATCH': continue
        matching_accounts = account_candidates(accounts, row.get('Credit card', ''))
        if len(matching_accounts) != 1: continue
        csv_groups[(str(matching_accounts[0].getUUID()), csv_key(row))].append((row_index, row))
    grouped_assignments = {}
    blocked_groups = set()
    for group_key, group in csv_groups.items():
        if len(group) < 2: continue
        account_id, key = group_key
        year, month, day = key[0].split('-')
        group_date = date(int(year), int(month), int(day))
        group_amount = Decimal(key[1])
        group_sign = key[2]
        exact = sorted([(txn, txn_date) for txn, txn_date, value in transactions_by_account[account_id]
                        if txn_date == group_date and
                        abs(Decimal(str(value)) / Decimal('100')).quantize(Decimal('0.01')) == group_amount and
                        ((group_sign == 'charge' and value < 0) or
                         (group_sign == 'refund' and value > 0))],
                       key=lambda pair: str(pair[0].getUUID()))
        if len(exact) != len(group):
            blocked_groups.add(group_key)
        else:
            for (row_index, row), (txn, txn_date) in zip(sorted(group), exact):
                grouped_assignments[row_index] = txn
    suffix = suffix or run_suffix()
    plan, exceptions, report = [], [], []
    used_transaction_ids = set()
    counters = dict(total=0, mismatch=0, edited=0, unmatched=0, ambiguous=0, unsafe=0)
    for row_index, row in enumerate(rows):
        counters['total'] += 1
        if row.get('Overall Result', '').strip().upper() == 'MISMATCH':
            counters['mismatch'] += 1
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='mismatch',
                               explanation='CSV Overall Result is MISMATCH; skipped'))
            continue
        matching_accounts = account_candidates(accounts, row.get('Credit card', ''))
        if len(matching_accounts) != 1:
            counters['unmatched'] += 1
            exceptions.append((row['Date'], row['Order amount'], row['Item description']))
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='unmatched',
                               explanation='No unique Moneydance account matched CSV card last four digits'))
            continue
        account_id = str(matching_accounts[0].getUUID())
        account_txns = transactions_by_account[account_id]
        d = csv_date(row['Date'])
        a = abs(Decimal(row['Order amount'])).quantize(Decimal('0.01'))
        key = csv_key(row)
        exception = (row['Date'], row['Order amount'], row['Item description'])
        if (account_id, key) in blocked_groups:
            counters['ambiguous'] += 1; exceptions.append(exception)
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='ambiguous',
                               explanation='Exact date/amount group count differs between CSV and Moneydance'))
            continue
        if row_index in grouped_assignments:
            matches = [grouped_assignments[row_index]]
        else:
            matches = [t for t, td, value in account_txns if abs((td - d).days) <= 3 and
                       amount_matches_moneydance(value, row['Order amount'])]
        if len(matches) > 1:
            exact_matches = [t for t in matches
                             if int(t.getDateInt()) == int(d.strftime('%Y%m%d'))]
            if len(exact_matches) == 1:
                matches = exact_matches
            else:
                amazon_matches = [t for t in matches
                                  if (t.getDescription() or '').strip().lower() == 'amazon']
                if len(amazon_matches) == 1:
                    matches = amazon_matches
        if not matches:
            counters['unmatched'] += 1; exceptions.append(exception)
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='unmatched',
                               explanation='No Moneydance transaction with matching amount within +/- 3 days'))
            continue
        if len(matches) > 1:
            counters['ambiguous'] += 1; exceptions.append(exception)
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='ambiguous',
                               explanation='Multiple Moneydance transactions matched amount/date criteria'))
            continue
        txn = matches[0]
        # A normal ParentTxn may return a parent reference to itself. Do not
        # use getParentTxn() as a safety test; check the actual Moneydance type.
        if not txn.getUUID() or not isinstance(txn, ParentTxn):
            counters['unsafe'] += 1; exceptions.append(exception)
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='unsafe',
                               explanation='Matched transaction could not be safely selected'))
            continue
        txn_id = str(txn.getUUID())
        if txn_id in used_transaction_ids:
            counters['ambiguous'] += 1; exceptions.append(exception)
            report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                               item_description=row['Item description'], status='ambiguous',
                               explanation='The only matching Moneydance transaction was already assigned to another CSV row'))
            continue
        used_transaction_ids.add(txn_id)
        expected = (txn.getMemo() if generated_memo_for_item(txn.getMemo(), row['Item description'])
                    else row['Item description'] + suffix)
        plan.append(dict(row_index=row_index, row=row, txn_id=txn_id, expected_memo=expected,
                         description=txn.getDescription(), memo_before=txn.getMemo()))
        report.append(dict(row_index=row_index, date=row['Date'], amount=row['Order amount'],
                           item_description=row['Item description'], status='eligible',
                           explanation='Exactly one safe amount/date match; eligible for Memo update',
                           transaction_id=str(txn.getUUID()), current_memo=txn.getMemo(),
                           proposed_memo=row['Item description'] + suffix))
    return dict(file=folder, account=ACCOUNT_NAME, suffix=suffix, plan=plan,
                exceptions=exceptions, counters=counters, report=report)

def apply_all(book, rows, approved_plan, expected_folder=TEST_FOLDER):
    current = plan_all(book, rows, expected_folder, approved_plan.get('suffix'))
    if [(x['txn_id'], x['expected_memo']) for x in current['plan']] != [(x['txn_id'], x['expected_memo']) for x in approved_plan['plan']]:
        raise RuntimeError('Bulk preview is stale; no edits made')
    for item in current['plan']:
        if item['memo_before'] == item['expected_memo']: continue
        txn = book.getItemForID(item['txn_id'])
        txn.setEditingMode(); txn.setMemo(item['expected_memo'])
        if not txn.syncItem() or not book.save(): raise RuntimeError('Save failed for one eligible transaction')
        fresh = book.getItemForID(item['txn_id'])
        if fresh.getMemo() != item['expected_memo'] or fresh.getDescription() != item['description']:
            raise RuntimeError('Read-back verification failed for one eligible transaction')
        current['counters']['edited'] += 1
    # Commit CSV status only after every eligible Moneydance row has succeeded.
    eligible_indexes = set(item['row_index'] for item in current['plan'])
    report_by_index = dict((item['row_index'], item) for item in current['report'])
    for index, row in enumerate(rows):
        row['MD Match'] = 'Y' if index in eligible_indexes else 'N'
        report_item = report_by_index.get(index, {})
        row['MD Failure reason'] = '' if index in eligible_indexes else report_item.get('explanation', '')
    write_csv(CSV_PATH, rows)
    current['csv_match_writeback'] = 'PASS'
    return current

def snapshot(book):
    """Capture stored fields of every transaction, including split records."""
    result = {}
    for txn in book.getTransactionSet().getAllTxns():
        result[str(txn.getUUID())] = dict(txn.getSyncInfo())
    return result

def verify_snapshot(before, after, target_id, expected):
    if set(before) != set(after):
        raise RuntimeError('Transaction IDs changed')
    for tid in before:
        old, new = dict(before[tid]), dict(after[tid])
        if tid == target_id:
            if new.get('memo') != expected:
                raise RuntimeError('Saved Memo verification failed')
            old.pop('memo', None)
            new.pop('memo', None)
            # Moneydance updates its internal save timestamp when syncing an edit.
            for key in ('timestamp', 'dtentered'):
                old.pop(key, None)
                new.pop(key, None)
        if old != new:
            changed = sorted(set(old.keys()).union(new.keys()))
            changed = [key for key in changed if old.get(key) != new.get(key)]
            raise RuntimeError('Unexpected field change in transaction %s keys=%s' % (tid, changed))

def apply_one(book, rows, approved_preview, expected_folder=TEST_FOLDER):
    current = preview(book, rows, expected_folder)
    if current.get('status') != 'eligible' or current != approved_preview:
        raise RuntimeError('Preview is stale or transaction is not eligible')
    tid, expected = current['transaction_id'], current['memo_proposed']
    if current['memo_before'] == expected:
        current.update(status='already_correct', edited=0)
        return current
    before = snapshot(book)
    txn = book.getItemForID(tid)
    txn.setEditingMode()
    txn.setMemo(expected)
    if not txn.syncItem():
        raise RuntimeError('syncItem failed; inspect file before retrying')
    if not book.save():
        raise RuntimeError('Save failed; inspect file before retrying')
    verify_snapshot(before, snapshot(book), tid, expected)
    refreshed = book.getItemForID(tid)
    if refreshed.getMemo() != expected or refreshed.getDescription() != current['description']:
        raise RuntimeError('Read-back verification failed')
    current.update(status='saved', edited=1, memo_verification='PASS',
                   description_verification='PASS', other_transaction_fields='PASS')
    return current

def main(context):
    import json
    md = context.get('moneydance')
    if md is None:
        raise RuntimeError('Run inside Moneydance Python Runner; standalone Python cannot access the open file')
    book, rows = md.getCurrentAccountBook(), read_csv(CSV_PATH)
    mode = context.get('MD_MEMO_MODE', 'preview')
    if mode == 'preview':
        result = preview(book, rows)
    elif mode == 'apply':
        result = apply_one(book, rows, context.get('MD_APPROVED_PREVIEW'))
    else:
        raise ValueError('Unknown mode')
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result

if __name__ == '__main__':
    main(globals())



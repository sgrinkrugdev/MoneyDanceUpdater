# Amazon Gift Card Activity to Moneydance Project Plan

Each plan item has two identifiers: the outline number shows current structure, and the persistent serial number `[AGC-####]` must never be reused or changed after creation. If the plan is reorganized later, keep the serial number with the original item.

## 1. `[AGC-0001]` Deliverable 1: Extract Amazon Gift Card Activity Status: Closed

    1.1. `[AGC-0002]` Create a dedicated Gift Card activity extraction path in the Amazon Configurable Extractor. Status: Implemented

        1.1.1. `[AGC-0003]` Keep Gift Card activity extraction separate from the existing Amazon order/item extraction flow. Status: Implemented

        1.1.2. `[AGC-0004]` Do not overload the existing order extraction output, `amazon-transactions.csv`. Status: Implemented

        1.1.3. `[AGC-0005]` Reuse the existing Chrome extension infrastructure for Amazon browser access, tab control, date range handling, configuration, storage, and CSV download. Status: Implemented

    1.2. `[AGC-0006]` Add a new extension action for testing and operational speed. Status: Implemented

        1.2.1. `[AGC-0007]` Add a button labeled `Extract Gift Card Activity Only`. Status: Implemented

        1.2.2. `[AGC-0008]` The button must run only the Gift Card activity extraction path. Status: Implemented

        1.2.3. `[AGC-0009]` The button must not run the existing order/item extraction path. Status: Implemented

    1.3. `[AGC-0010]` Use the same date range behavior as the current Amazon data extractor. Status: Implemented

        1.3.1. `[AGC-0011]` Read the date range from the existing configurable extractor configuration path. Status: Implemented

        1.3.2. `[AGC-0012]` Apply the date range immediately during Gift Card activity extraction because the activity history goes back years. Status: Implemented

        1.3.3. `[AGC-0013]` Do not rely on exporting all historical Gift Card activity and filtering later. Status: Implemented

    1.4. `[AGC-0014]` Extract Gift Card activity rows from the Amazon Gift Card activity page. Status: Tested

        1.4.1. `[AGC-0015]` Extract the row date. Status: Tested

        1.4.2. `[AGC-0016]` Extract the row amount. Status: Tested

        1.4.3. `[AGC-0017]` Extract the row transaction type. Status: Tested

        1.4.4. `[AGC-0018]` Extract a debug transaction identifier when Amazon exposes a usable identifier. Status: Tested

        1.4.5. `[AGC-0019]` If Amazon does not expose a stable transaction identifier, generate a debug-only row fingerprint from normalized row fields. Status: Tested

    1.5. `[AGC-0020]` Match amount normalization to the existing Amazon Extractor logic. Status: Implemented

        1.5.1. `[AGC-0021]` Follow the same sign, currency, decimal, and formatting conventions currently used by the Amazon Configurable Extractor. Status: Implemented

        1.5.2. `[AGC-0022]` Preserve transaction type so later import logic can distinguish reloads, redemptions, refunds, promotional credits, and adjustments. Status: Implemented

    1.6. `[AGC-0023]` Handle Amazon Gift Card activity pagination. Status: Tested

        1.6.1. `[AGC-0024]` Detect and use the Amazon activity page `Next` button. Status: Tested

        1.6.2. `[AGC-0025]` Continue paging while rows may still fall inside the configured date range. Status: Tested

        1.6.3. `[AGC-0026]` Stop paging when the configured date range has been fully passed or when no enabled `Next` button remains. Status: Tested

        1.6.4. `[AGC-0027]` Prevent duplicate rows during a single extraction run. Status: Tested

    1.7. `[AGC-0028]` Export Gift Card activity to a dedicated CSV file. Status: Tested

        1.7.1. `[AGC-0029]` Write the output file as `amazon-gift-card-transactions.csv`. Status: Tested

        1.7.2. `[AGC-0030]` Include the required import columns: `Date`, `Amount`, and `Transaction type`. Status: Tested

        1.7.3. `[AGC-0031]` Include a debug transaction identifier column. Status: Tested

        1.7.4. `[AGC-0032]` Include the row closing Gift Card balance as an explicit `Balance` CSV column because Deliverable 2 uses it for duplicate detection, fingerprint validation, and balance verification. Status: Implemented

        1.7.5. `[AGC-0263]` Generate `Source fingerprint` from `Date`, exact `Description`, exported `Amount`, and exported `Balance`. Status: Implemented

        1.7.6. `[AGC-0264]` Preserve `Debug transaction ID` as diagnostic only; do not document it as a stable Amazon transaction identifier. Status: Implemented

        1.7.7. `[AGC-0265]` Keep the exported Gift Card CSV amount and balance values auditable from the Amazon activity page so MoneyDanceUpdate can recompute and validate the fingerprint. Status: Implemented

    1.8. `[AGC-0033]` Make all Step 1 paths and parameters configurable. Status: Implemented

        1.8.1. `[AGC-0034]` Use the existing Amazon Configurable Extractor configuration path. Status: Implemented

        1.8.2. `[AGC-0035]` Add configurable output filename or output path support for `amazon-gift-card-transactions.csv`. Status: Implemented

        1.8.3. `[AGC-0036]` Add configurable selectors or extraction parameters where Amazon page structure is likely to change. Status: Implemented

        1.8.4. `[AGC-0037]` Add configurable paging limits or safety limits to avoid runaway navigation. Status: Implemented

    1.9. `[AGC-0038]` Add Step 1 validation and test coverage. Status: Tested

        1.9.1. `[AGC-0039]` Add fixture-based tests using saved or redacted Gift Card activity page HTML if the AmazonOrderDetailScraper repo already has an extractor test pattern.

        1.9.2. `[AGC-0040]` Test at least one reload or add-funds transaction.

        1.9.3. `[AGC-0041]` Test at least one Gift Card redemption transaction.

        1.9.4. `[AGC-0042]` Test at least one refund or credit transaction if available.

        1.9.5. `[AGC-0043]` Test multi-page extraction through the `Next` button. Status: Tested

        1.9.6. `[AGC-0044]` Test date range filtering at the beginning, middle, and end of the available activity history. Status: Tested

        1.9.7. `[AGC-0045]` Test duplicate suppression within a single extraction run. Status: Tested

    1.10. `[AGC-0046]` Step 1 acceptance criteria. Status: Tested

        1.10.1. `[AGC-0047]` The extension exposes an `Extract Gift Card Activity Only` button. Status: Tested

        1.10.2. `[AGC-0048]` The button exports only Gift Card activity rows. Status: Tested

        1.10.3. `[AGC-0049]` The export uses the configured date range immediately. Status: Tested

        1.10.4. `[AGC-0050]` The export follows the existing Amazon Extractor amount normalization logic. Status: Tested

        1.10.5. `[AGC-0051]` The export includes a debug transaction identifier. Status: Tested

        1.10.6. `[AGC-0052]` The export file is named or configured as `amazon-gift-card-transactions.csv`. Status: Tested

        1.10.7. `[AGC-0053]` The existing order/item extraction behavior and `amazon-transactions.csv` output remain unchanged. Status: Tested

        1.10.8. `[AGC-0266]` The Gift Card CSV includes `Balance`, and `Source fingerprint` can be recomputed from `Date`, exact `Description`, exported `Amount`, and exported `Balance`. Status: Tested

        1.10.9. `[AGC-0267]` Re-running Gift Card extraction for the same visible Amazon rows produces stable `Balance` and `Source fingerprint` values. Status: Tested

## 2. `[AGC-0054]` Deliverable 2: Import Gift Card Activity Into Moneydance Status: Tested; category-missing behavior revised after API validation

    2.1. `[AGC-0246]` Prove Moneydance transaction creation before implementing the full importer. Status: Tested; show-stopper satisfied for transaction creation with configured `Uncategorized` category available.

        2.1.1. `[AGC-0055]` Create a new MoneyDanceUpdate importer module only after the proof-of-concept transaction insertion succeeds. Status: Implemented

        2.1.2. `[AGC-0056]` Keep the Gift Card importer separate from `moneydance_single_record.py`. Status: Implemented

        2.1.3. `[AGC-0057]` Reuse existing MoneyDanceUpdate book loading, open-book checks, safe save behavior, and configuration conventions. Status: Implemented

        2.1.4. `[AGC-0250]` The proof-of-concept utility must insert one dummy transaction into the configured `Amazon Gift Card` account. Status: Tested

        2.1.5. `[AGC-0251]` Failure to implement and verify the proof-of-concept transaction insertion blocks the full importer implementation. Status: Closed

        2.1.6. `[AGC-0247]` Delete the proof-of-concept dummy transaction utility after the full importer is successfully implemented and validated. Status: Closed; `moneydance_gc_insert_poc.py` and `run_gc_insert_poc.bat` removed after importer validation

        2.1.7. `[AGC-0268]` Test result: `moneydance_gc_insert_poc.py` and `run_gc_insert_poc.bat` inserted a dummy transaction into the configured `Amazon Gift Card` account in `D:\Docs\Project\MoneyDanceUpdate\test_data\AGC Test.moneydance`, reopened the file from disk, and verified the transaction ID, date, amount, description, memo, check number, and account. Status: Tested. Note: the temporary PoC root-account fallback displayed `AGC Test` in Moneydance and is not accepted production behavior. Deliverable 2 requires configured `Uncategorized` when available; if the configured category is absent, the importer-facing category value is the empty string and no account/category may be created.

    2.2. `[AGC-0058]` Read `amazon-gift-card-transactions.csv`. Status: Implemented

        2.2.1. `[AGC-0059]` Make the input CSV path configurable in the existing MoneyDanceUpdate configuration path. Status: Implemented

        2.2.2. `[AGC-0060]` Validate that required columns are present before touching the Moneydance book. Status: Implemented

        2.2.3. `[AGC-0061]` Preserve and log the debug transaction identifier for troubleshooting, but do not treat it as an authoritative stable Amazon transaction id. Status: Implemented

        2.2.4. `[AGC-0262]` Require a stable test input copy at `D:\Docs\Project\MoneyDanceUpdate\test_data\Amazon GC test sample.csv`; tests must treat it as read-only and write status changes only to a temporary copy. Status: Tested

        2.2.5. `[AGC-0193]` Validate that the Gift Card CSV includes a `Balance` column before import; this depends on Deliverable 1 item `[AGC-0032]` and acceptance item `[AGC-0266]`. Status: Tested

        2.2.6. `[AGC-0194]` Recompute the importer fingerprint from `Date`, exact `Description`, `Amount`, and `Balance`, and report a mismatch if the CSV `Source fingerprint` does not match Deliverable 1 fingerprint item `[AGC-0263]`. Status: Tested

        2.2.7. `[AGC-0195]` Prefer a shared fingerprint implementation or explicitly shared algorithm contract between scraper and MoneyDanceUpdate so the importer does not silently fork fingerprint behavior. Status: Implemented

        2.2.8. `[AGC-0196]` Reject rows whose `Amazon Verify` value is not `VERIFIED` before touching the Moneydance book. Status: Implemented

    2.3. `[AGC-0062]` Create transactions in the Moneydance account `Amazon Gift Card`. Status: Tested

        2.3.1. `[AGC-0063]` Use the existing configured account mapping where possible. Status: Implemented

        2.3.2. `[AGC-0064]` Create transactions only in the dedicated configured `Amazon Gift Card` account. Status: Implemented

        2.3.3. `[AGC-0065]` Apply the same sign conventions expected by Moneydance for this account: Amazon Gift Card charges reduce the account balance in Moneydance, refunds and credits increase it. Status: Tested

        2.3.4. `[AGC-0197]` Never create Moneydance accounts, never fall back to another account, and fail hard with logging if the configured Gift Card account is missing or ambiguous. Status: Implemented

        2.3.5. `[AGC-0198]` Never modify existing Moneydance Gift Card transactions as part of this importer; existing memo/description update behavior remains a separate utility. Status: Implemented

        2.3.6. `[AGC-0199]` Store the generated source fingerprint in the Moneydance transaction `Check#` field. Status: Implemented

        2.3.7. `[AGC-0200]` Use the exact Amazon screen description text from the CSV as the Moneydance transaction description. Status: Implemented

        2.3.8. `[AGC-0201]` Default the transaction category to a configured Moneydance category account named `Uncategorized`. Status: Implemented

        2.3.9. `[AGC-0202]` If the configured category account is missing, do not create a category account and do not silently fall back to another visible account. Implementation evidence showed Moneydance 2024.4 deletes zero-split parent transactions as invalid and rejects `None` as a split account, so the importer now fails before Moneydance writes with `CATEGORY_MISSING` instead of pretending a blank category can be persisted. Status: Tested; original blank-and-continue requirement needs user decision if still desired

        2.3.10. `[AGC-0203]` Interpret Amazon Gift Card charge rows as Moneydance account decreases even when the CSV `Amount` preserves Amazon-visible positive text, using `Transaction type = Charge` or a negative `Visible amount` as the charge signal; interpret refund rows and positive credit rows as Moneydance account increases. Status: Tested

        2.3.11. `[AGC-0224]` Store only the raw generated source fingerprint in the Moneydance `Check#` field, with no prefix such as `AGC:`. Status: Implemented

        2.3.12. `[AGC-0225]` Create and save Gift Card transactions one row at a time rather than batch-creating and saving once. Status: Implemented

    2.4. `[AGC-0066]` Prevent duplicate imports. Status: Tested

        2.4.1. `[AGC-0067]` Check for duplicates in the input CSV before import. Status: Tested

        2.4.2. `[AGC-0068]` Check for matching existing Moneydance transactions before creating new transactions. Status: Tested

        2.4.3. `[AGC-0069]` Use the generated source fingerprint as the primary duplicate key where available. Status: Tested

        2.4.4. `[AGC-0070]` Fall back to a deterministic row fingerprint when a stable Amazon identifier is not available. Status: Implemented

        2.4.5. `[AGC-0204]` Allow multiple legitimate Gift Card rows with the same date, amount, and transaction type; do not collapse them unless the source fingerprint proves they are the same row. Status: Implemented

        2.4.6. `[AGC-0205]` If multiple existing Moneydance transactions match a CSV row without the same stored fingerprint, import the row and include the fingerprint in the new record. Status: Implemented

        2.4.7. `[AGC-0226]` If an existing Moneydance transaction has the same `Check#` fingerprint but different date, amount, or description, fail that row with `FINGERPRINT_MISMATCH` instead of trusting the fingerprint alone. Status: Implemented

        2.4.8. `[AGC-0227]` Split duplicate import statuses between `SKIPPED_DUPLICATE_IN_CSV` and `SKIPPED_DUPLICATE_IN_MD`; do not use one generic duplicate import status. Status: Tested

    2.5. `[AGC-0071]` Add importer reporting. Status: Implemented and dry-run tested

        2.5.1. `[AGC-0072]` Report imported rows. Status: Tested

        2.5.2. `[AGC-0073]` Report skipped duplicate rows. Status: Tested

        2.5.3. `[AGC-0074]` Report invalid rows. Status: Implemented

        2.5.4. `[AGC-0075]` Report Moneydance write failures with enough row detail to debug. Status: Implemented

        2.5.5. `[AGC-0206]` Write importer status columns back to the Gift Card CSV, including `MD Import`, `MD Verify`, and `MD Failure reason`. Status: Tested

        2.5.6. `[AGC-0207]` Continue processing valid rows after invalid rows or per-row failures, keep a log, and update each row status in the CSV. Status: Implemented

        2.5.7. `[AGC-0208]` Permit partial import success for now; successful valid rows may be imported even when other rows fail. Status: Implemented

        2.5.8. `[AGC-0214]` Use explicit `MD Import` status values: `IMPORTED`, `SKIPPED_DUPLICATE_IN_CSV`, `SKIPPED_DUPLICATE_IN_MD`, `INVALID`, `FAILED`, and `DRY_RUN_READY`. Status: Tested

        2.5.9. `[AGC-0215]` Use explicit `MD Verify` status values: `VERIFIED`, `NOT_VERIFIED`, and `NOT_APPLICABLE`. Status: Tested

        2.5.10. `[AGC-0216]` Set `MD Verify` to `VERIFIED` only after reopen-from-disk verification confirms the expected account, amount, date, description, category behavior, and `Check#` fingerprint. Status: Tested

        2.5.11. `[AGC-0217]` Dry-run mode must not update the Gift Card CSV by default. Status: Tested

        2.5.12. `[AGC-0218]` Dry-run mode must generate a disk report of planned imports, skipped duplicates, invalid rows, and expected status outcomes. Status: Tested

        2.5.13. `[AGC-0219]` Use controlled `MD Failure reason` codes plus detail text, including at least `MISSING_BALANCE`, `FINGERPRINT_MISMATCH`, `FINGERPRINT_TOO_LONG`, `AMAZON_NOT_VERIFIED`, `DUPLICATE_IN_CSV`, `DUPLICATE_IN_MD`, `ACCOUNT_MISSING`, and `WRITE_FAILED`. Status: Implemented

        2.5.14. `[AGC-0222]` The dry-run disk report path must be configurable with `MD_GC_DRY_RUN_REPORT_PATH`, defaulting beside the CSV as `amazon-gift-card-import-dry-run.json`; dry-run reporting must include both JSON and CSV outputs. Status: Tested

        2.5.15. `[AGC-0223]` Dry-run report rows with `MD Import` = `DRY_RUN_READY` should use `MD Verify` = `NOT_APPLICABLE`, because no Moneydance write exists to verify. Status: Tested

        2.5.16. `[AGC-0228]` In apply mode, write Gift Card CSV status updates after each processed row rather than waiting until the whole run completes. Status: Implemented

        2.5.17. `[AGC-0229]` Dry-run JSON and CSV reports must include the full source row data along with planned status, verification value, and failure reason details. Status: Tested

        2.5.18. `[AGC-0230]` If the source fingerprint exceeds 30 characters, do not import that row; write a descriptive CSV status and failure reason so the limit can be reviewed during testing. Status: Implemented

        2.5.19. `[AGC-0233]` Rows rejected for an overlong source fingerprint must use `MD Import` = `INVALID` and `MD Failure reason` = `FINGERPRINT_TOO_LONG` plus detail text. Status: Implemented

        2.5.20. `[AGC-0234]` Per-row CSV status writes must use a temporary file plus replace of the original CSV, not in-place mutation. Status: Implemented

        2.5.21. `[AGC-0235]` Remove the temporary CSV file on successful completion after the final replacement succeeds. Status: Implemented

        2.5.22. `[AGC-0236]` Use the original Gift Card CSV path plus `.tmp` for per-row temporary status writes, for example `amazon-gift-card-transactions.csv.tmp`. Status: Implemented

        2.5.23. `[AGC-0237]` Before the first per-row status write in a run, create one timestamped backup copy of the original Gift Card CSV. Status: Tested

        2.5.24. `[AGC-0238]` If writing CSV status fails, stop the import immediately to avoid divergence between Moneydance changes and CSV status reporting. Status: Implemented

        2.5.25. `[AGC-0240]` Name the timestamped CSV backup as the original CSV path plus `.YYYYMMDD-HHMMSS.bak`. Status: Tested

        2.5.26. `[AGC-0241]` If backup creation fails, stop the import before any Moneydance write is attempted. Status: Implemented

        2.5.27. `[AGC-0243]` Keep timestamped CSV backups indefinitely for now; revisit retention and cleanup once the importer is stable. Status: Implemented

        2.5.28. `[AGC-0244]` Dry-run report filenames must be timestamped rather than overwritten each run. Status: Tested

        2.5.29. `[AGC-0245]` Apply mode must produce a structured JSON summary report in addition to the updated Gift Card CSV. Status: Tested

        2.5.30. `[AGC-0248]` Add a post-import verification step that compares the Moneydance `Amazon Gift Card` account balance with the Amazon Gift Card balance from the imported source data. Status: Tested

        2.5.31. `[AGC-0249]` If the Moneydance account balance and Amazon Gift Card balance do not match, report the mismatch in the log and structured summary report without hiding row-level import results. Status: Tested

    2.6. `[AGC-0076]` Step 2 acceptance criteria. Status: Tested for AGC Test sample import, duplicate detection, disk reopen verification, and final balance match

        2.6.1. `[AGC-0077]` Gift Card activity rows can be imported into Moneydance account `Amazon Gift Card`.

        2.6.2. `[AGC-0078]` Duplicate rows are not re-created.

        2.6.3. `[AGC-0079]` Existing Moneydance safety checks are preserved.

        2.6.4. `[AGC-0080]` The importer does not modify existing Amazon order matching logic.

        2.6.5. `[AGC-0209]` The importer has a configurable dry-run yes/no switch, defaulting to dry-run for now. Status: Tested

        2.6.6. `[AGC-0210]` Import verification includes reopening the Moneydance book from disk unless implementation evidence later justifies a safer alternative.

        2.6.7. `[AGC-0211]` The importer refuses to run when Moneydance is open. Status: Tested

        2.6.8. `[AGC-0212]` Production operation runs Gift Card import first and then the existing Amazon memo matcher from a single `.bat` file. Status: Implemented

        2.6.9. `[AGC-0213]` Test and debug operation can run the Gift Card importer separately against the same existing test Moneydance book. Status: Implemented

        2.6.10. `[AGC-0220]` The Gift Card CSV `Amount` column should preserve the exact Amazon-shown signed amount for debugging and auditability unless implementation evidence later shows a strong reason to normalize it.

        2.6.11. `[AGC-0221]` Avoid silently forking fingerprint behavior by defining a shared fingerprint contract with cross-language golden test cases; use a shared code library only if implementation inspection shows it is simpler and safer.

        2.6.12. `[AGC-0231]` If Gift Card import reports `FAILED` or `INVALID` rows before the existing memo matcher runs, in either dry-run mode or apply mode, the production batch must give the user an explicit abort-or-continue choice before proceeding.

        2.6.13. `[AGC-0232]` The generated source fingerprint stored in Moneydance `Check#` must be limited to 30 characters for now, even though Moneydance documentation does not list a known limit; revisit if tests show the limit is too restrictive.

        2.6.14. `[AGC-0239]` Add an unattended-run behavior setting such as `MD_GC_ON_IMPORT_ISSUES` with values `prompt`, `abort`, or `continue`, defaulting to `prompt`, for cases where Gift Card import reports `FAILED` or `INVALID` before memo matching; `continue` is allowed in dry-run, test, and production apply mode, but must be logged clearly. Status: Implemented

        2.6.15. `[AGC-0242]` Document every Gift Card importer setting with detailed inline comments in the existing configuration file, especially `MD_GC_ON_IMPORT_ISSUES` and the consequences of `prompt`, `abort`, and `continue`. Status: Implemented

    2.7. `[AGC-0252]` Deliverable 2 risk registry.

        2.7.1. `[AGC-0253]` Risk: Moneydance transaction creation API is unproven in this repo because current code edits existing transactions but does not create new ones. Mitigation: `[AGC-0246]` is a show-stopper proof-of-concept transaction insertion task and must succeed before full importer implementation.

        2.7.2. `[AGC-0254]` Risk: Gift Card import depends on scraper-side `Balance` export and fingerprint contract. Mitigation: track this explicitly in Deliverable 1 items `[AGC-0032]`, `[AGC-0263]`, and `[AGC-0266]`; validate incoming CSV `Balance` and recomputed `Source fingerprint` before touching Moneydance.

        2.7.3. `[AGC-0255]` Risk: Amazon rendering, signs, descriptions, balance display, or fingerprint inputs may change. Mitigation: keep row-level validation, controlled failure reasons, and scraper/importer golden fingerprint tests.

        2.7.4. `[AGC-0256]` Risk: Amazon-shown signed `Amount` must map correctly to Moneydance debit/credit behavior. Mitigation: add focused sign tests before production apply mode.

        2.7.5. `[AGC-0257]` Risk: Moneydance `Check#` length is not documented. Mitigation: enforce the current 30-character fingerprint cap and report `FINGERPRINT_TOO_LONG` for rows that exceed it.

        2.7.6. `[AGC-0258]` Risk: A crash during per-row Moneydance writes and CSV status writes can leave a partial run. Mitigation: one-row-at-a-time saves, timestamped CSV backups, temp-file-plus-replace status writes, immediate stop on status write failure, and structured reports.

        2.7.7. `[AGC-0259]` Risk: Production `continue` behavior can allow memo matching after Gift Card import issues. Mitigation: GitHub issue #3 tracks guardrails, inline configuration documentation, loud logging, and summary-report visibility.

        2.7.8. `[AGC-0260]` Risk: Moneydance category behavior for created transactions needs API validation. Mitigation: GitHub issue #4 tracks category present/missing validation and reopen-from-disk verification.

        2.7.9. `[AGC-0261]` Risk: The stable sample CSV can drift from scraper output as format evolves. Mitigation: keep the sample representative and update tests when the scraper contract changes.


    2.8. `[AGC-0269]` Deliverable 2 implementation note. Status: Tested

        2.8.1. `[AGC-0270]` Added `moneydance_gift_card_import.py`, `moneydance_gc_import_run.py`, `moneydance_gc_production_run.py`, `run_gc_import.bat`, and `run_moneydance_production_with_gc.bat`. Status: Implemented

        2.8.2. `[AGC-0271]` Verified Python syntax under CPython and Jython import/planning against the stable Gift Card sample CSV copy. Status: Tested

        2.8.3. `[AGC-0272]` Generated timestamped dry-run JSON and CSV reports on disk from a temporary copy of the stable sample; all 17 sample rows planned as `DRY_RUN_READY`. Status: Tested

        2.8.4. `[AGC-0273]` Headless Moneydance dry-run/apply testing passed after `Moneydance.exe` was closed: dry-run planned 17 rows, apply imported and disk-verified 17 rows, duplicate rerun skipped all 17 rows as `SKIPPED_DUPLICATE_IN_MD`, and category inspection confirmed all imported sample rows use `Uncategorized`. Status: Tested

        2.8.5. `[AGC-0274]` Corrected the Gift Card charge/payment mapping defect: Amazon charge rows with positive CSV `Amount` and negative `Visible amount` now create Moneydance account decreases, while refunds and credits create account increases. Status: Tested

        2.8.6. `[AGC-0275]` Confirmed against `D:\Docs\Project\MoneyDanceUpdate\test_data\AGC Test.moneydance` using a controlled copy of `Amazon GC test sample.csv`: 17 rows imported, all 17 verified after reopening the Moneydance book from disk, final Moneydance `Amazon Gift Card` balance was 1801 cents matching the Amazon source balance of 1801 cents, and a duplicate rerun planned 0 rows and skipped all 17 rows as `SKIPPED_DUPLICATE_IN_MD`. Status: Tested

        2.8.7. `[AGC-0276]` Missing-category fixture using `MD_GC_CATEGORY_NAME=Uncategorized Missing` proved the old blank-category assumption unsafe: zero-split parent transactions reopened as invalid/deleted, and `SplitTxn.makeSplitTxn` rejects a null category account. Added a pre-write `CATEGORY_MISSING` guard and re-ran the normal `Uncategorized` path successfully: 17 rows imported, all verified, balance matched 1801 cents. Status: Tested

        2.8.8. `[AGC-0277]` Live extraction import test on 2026-09-14: reviewed `D:\Downloads\amazon-gift-card-transactions.csv` from extractor version 1.4.6, confirmed 17 rows, 17 `Amazon Verify=VERIFIED`, required columns present, no duplicate source fingerprints reported, restored `D:\Docs\Project\MoneyDanceUpdate\test_data\AGC Test.moneydance` from backup, imported 17 rows, verified all 17 after reopening from disk, and final Moneydance/Amazon balance matched at 1801 cents. Duplicate rerun for this live CSV was blocked because `Moneydance.exe` was open. Status: Tested with duplicate rerun blocked by safety guard

## 3. `[AGC-0081]` Deliverable 3: Preserve Existing Amazon Order Extraction Status: Tested

    3.1. `[AGC-0082]` Keep the existing Amazon order/item extraction flow intact.

        3.1.1. `[AGC-0083]` Preserve `amazon-transactions.csv`.

        3.1.2. `[AGC-0084]` Preserve `amazon-transactions-run-log.json`.

        3.1.3. `[AGC-0085]` Preserve existing extraction behavior in `content2.js`, `description.js`, `export.js`, and `background.js` except where shared infrastructure must support the new Gift Card mode.

    3.2. `[AGC-0086]` Keep order-related Gift Card payment rows conceptually separate from Gift Card account activity.

        3.2.1. `[AGC-0087]` Continue allowing the existing extractor to identify `Amazon Gift Card` as an order payment method.

        3.2.2. `[AGC-0088]` Do not treat order payment method rows as Gift Card account ledger rows.

        3.2.3. `[AGC-0089]` Do not import order payment method rows through the new Gift Card importer.

    3.3. `[AGC-0090]` Step 3 acceptance criteria. Status: Tested

        3.3.1. `[AGC-0091]` Existing order extraction output is unchanged unless explicitly required by shared configuration work. Status: Tested

        3.3.2. `[AGC-0092]` Gift Card activity extraction does not create duplicate order rows. Status: Tested

        3.3.3. `[AGC-0093]` Order extraction tests or manual checks still pass after adding Gift Card extraction. Status: Tested

        3.3.4. `[AGC-0278]` Live Deliverable 3 regression check on 2026-09-14: regular Amazon extraction produced `D:\Downloads\amazon-transactions.csv` with 150 rows and expected columns `Credit card|Order number|Date source|Verification|Order amount|Date|MD Verify|MD Match|Item description|MD Failure reason|Transaction type|Order details URL|Overall Result`; run log reported extractor version 1.4.6, 9 pages, 150 records saved, 0 errors, and status completed. Gift Card activity markers were absent from regular order output. Status: Tested

## 4. `[AGC-0094]` Deliverable 4: Confirm Moneydance Account Mapping Status: Implemented

    4.1. `[AGC-0095]` Keep the existing MoneyDanceUpdate account mapping behavior. Status: Implemented

        4.1.1. `[AGC-0096]` Preserve the existing `MD_CARD_ACCOUNT_MAP` configuration entry. Status: Implemented

        4.1.2. `[AGC-0097]` Confirm that `Amazon Gift Card=Amazon Gift Card` remains configured. Status: Implemented

    4.2. `[AGC-0098]` Use the mapping consistently across import and matching. Status: Implemented

        4.2.1. `[AGC-0099]` The new Gift Card importer should use the configured Moneydance account name. Status: Implemented

        4.2.2. `[AGC-0100]` The existing matcher should continue using the configured account name when matching Amazon order rows paid with Gift Card balance. Status: Implemented

    4.3. `[AGC-0101]` Step 4 acceptance criteria. Status: Implemented

        4.3.1. `[AGC-0102]` The Gift Card account name is not hard-coded in multiple unrelated places. Status: Implemented

        4.3.2. `[AGC-0103]` The existing matcher can find imported Gift Card account transactions after Step 2. Status: Implemented

## 5. `[AGC-0104]` Deliverable 5: Match Amazon Order Data to Existing Moneydance Transactions Status: Implemented; pending production retest

    5.1. `[AGC-0105]` Leave the current matching responsibility in MoneyDanceUpdate. Status: Implemented

        5.1.1. `[AGC-0106]` Keep `moneydance_single_record.py` responsible for matching extracted Amazon order rows to existing Moneydance transactions. Status: Implemented

        5.1.2. `[AGC-0107]` Keep `moneydance_production_run.py` and `moneydance_headless_test.py` as the existing orchestration and test entry points unless code inspection shows a safer established path. Status: Implemented

    5.2. `[AGC-0108]` Do not turn the existing matcher into the Gift Card importer. Status: Implemented

        5.2.1. `[AGC-0109]` The matcher should continue matching by account, date, amount, sign, and related fields. Status: Implemented

        5.2.2. `[AGC-0110]` The matcher should continue writing `MD Match`, `MD Verify`, and `MD Failure reason` back to the Amazon CSV. Status: Implemented

        5.2.3. `[AGC-0111]` The matcher should benefit from Step 2 because Gift Card account transactions will already exist. Status: Implemented

    5.3. `[AGC-0112]` Step 5 acceptance criteria. Status: Implemented; pending production retest

        5.3.1. `[AGC-0113]` Existing Amazon CSV writeback behavior is preserved. Status: Implemented

        5.3.2. `[AGC-0114]` Gift Card-paid order rows can match against imported `Amazon Gift Card` account transactions. Status: Implemented

        5.3.3. `[AGC-0115]` Matching failures caused by missing Gift Card account transactions are reduced or eliminated. Status: Pending production retest

## 6. `[AGC-0116]` Deliverable 6: Update Moneydance Memos and Descriptions Status: Implemented; pending production retest

    6.1. `[AGC-0117]` Preserve existing memo and description update behavior. Status: Implemented

        6.1.1. `[AGC-0118]` Keep memo and description updates in `moneydance_single_record.py`. Status: Implemented

        6.1.2. `[AGC-0119]` Do not add Gift Card import responsibilities to the memo update logic. Status: Implemented

    6.2. `[AGC-0120]` Ensure imported Gift Card transactions can participate in existing update flow. Status: Implemented

        6.2.1. `[AGC-0121]` Imported Gift Card transactions should have dates, amounts, and account names compatible with the matcher. Status: Implemented

        6.2.2. `[AGC-0122]` Existing matched order rows should update Moneydance memos and descriptions as before. Status: Implemented

    6.3. `[AGC-0123]` Step 6 acceptance criteria. Status: Pending production retest

        6.3.1. `[AGC-0124]` Existing memo and description update behavior remains unchanged. Status: Implemented

        6.3.2. `[AGC-0125]` Gift Card transactions imported by Step 2 can be updated after matching through the existing workflow. Status: Pending production retest

## 7. `[AGC-0126]` Deliverable 7: Configuration and Operational Controls Status: Implemented

    7.1. `[AGC-0127]` Centralize new configuration in existing config paths. Status: Implemented

        7.1.1. `[AGC-0128]` Add Amazon extractor configuration for Gift Card activity page settings, date range reuse, output filename, selectors, and paging safety limits. Status: Implemented

        7.1.2. `[AGC-0129]` Add MoneyDanceUpdate configuration for Gift Card CSV input path, target account mapping, duplicate handling, and dry-run behavior. Status: Implemented

    7.2. `[AGC-0130]` Add dry-run and logging controls. Status: Implemented

        7.2.1. `[AGC-0131]` Support dry-run mode for the Moneydance importer before creating transactions. Status: Tested

        7.2.2. `[AGC-0132]` Log extracted Gift Card row counts. Status: Tested

        7.2.3. `[AGC-0133]` Log imported, skipped, duplicate, and failed row counts. Status: Tested


        7.2.4. `[AGC-0279]` Production runs print descriptive operational failures for locked CSV writeback and open Moneydance, and place the final JSON summary plus compact counters block at the end of the log. Status: Implemented
    7.3. `[AGC-0134]` Step 7 acceptance criteria. Status: Implemented

        7.3.1. `[AGC-0135]` No new hard-coded operational paths are required. Status: Implemented

        7.3.2. `[AGC-0136]` The same date range used by the current extractor controls Gift Card extraction. Status: Tested

        7.3.3. `[AGC-0137]` A production run can be configured without code edits. Status: Implemented

## 8. `[AGC-0138]` Deliverable 8: End-to-End Validation Status: In progress

    8.1. `[AGC-0139]` Validate the Step 1 extractor independently. Status: Tested

        8.1.1. `[AGC-0140]` Run `Extract Gift Card Activity Only`. Status: Tested

        8.1.2. `[AGC-0141]` Confirm `amazon-gift-card-transactions.csv` contains the expected configured date range. Status: Tested

        8.1.3. `[AGC-0142]` Confirm no order/item rows are present. Status: Tested

    8.2. `[AGC-0143]` Validate the Step 2 importer independently. Status: Tested

        8.2.1. `[AGC-0144]` Run the importer in dry-run mode. Status: Tested

        8.2.2. `[AGC-0145]` Confirm duplicate detection before writing. Status: Tested

        8.2.3. `[AGC-0146]` Run the importer against a test Moneydance book or approved test path before production. Status: Tested

    8.3. `[AGC-0147]` Validate the existing matcher after import. Status: Pending production retest

        8.3.1. `[AGC-0148]` Run the existing Amazon order extraction or use an existing Amazon CSV test file. Status: Tested

        8.3.2. `[AGC-0149]` Run the existing MoneyDanceUpdate matcher. Status: Pending production retest

        8.3.3. `[AGC-0150]` Confirm Gift Card-paid order rows can match against the imported Gift Card account transactions. Status: Pending production retest

    8.4. `[AGC-0151]` Step 8 acceptance criteria. Status: Pending production retest

        8.4.1. `[AGC-0152]` Gift Card activity is extracted, imported, and available for matching. Status: Implemented

        8.4.2. `[AGC-0153]` Existing Amazon order extraction remains stable. Status: Tested

        8.4.3. `[AGC-0154]` Existing Moneydance memo update behavior remains stable. Status: Pending production retest

        8.4.4. `[AGC-0155]` Duplicate protection exists in both extraction output and Moneydance import. Status: Tested

## 9. `[AGC-0156]` Open Questions

    9.1. `[AGC-0157]` What is the exact existing Amazon Extractor amount convention that Gift Card extraction must match?

        9.1.1. `[AGC-0158]` Code inspection is required to confirm whether charges, refunds, and credits are represented from Amazon's perspective, card-account perspective, or Moneydance import perspective.

    9.2. `[AGC-0159]` What exact debug transaction identifier does Amazon expose on the Gift Card activity page?

        9.2.1. `[AGC-0160]` If Amazon exposes an order id, claim code id, transaction id, or hidden activity id, use it.

        9.2.2. `[AGC-0161]` If Amazon exposes no stable identifier, use a deterministic debug fingerprint.

    9.3. `[AGC-0162]` Where is the existing Amazon Configurable Extractor configuration path defined?

        9.3.1. `[AGC-0163]` Code inspection is required before naming exact config keys.

    9.4. `[AGC-0164]` Decision: `amazon-gift-card-transactions.csv` should default to the same folder as `D:\Downloads\amazon-transactions.csv`, and that folder must be configurable.

        9.4.1. `[AGC-0165]` The default output destination is `D:\Downloads\amazon-gift-card-transactions.csv` when the existing Amazon CSV folder is `D:\Downloads`.

    9.5. `[AGC-0166]` Recommendation: write a separate Gift Card extraction run log.

        9.5.1. `[AGC-0167]` The existing order extractor writes `amazon-transactions-run-log.json`, so Gift Card extraction should mirror that pattern for troubleshooting.

        9.5.2. `[AGC-0168]` Use `amazon-gift-card-transactions-run-log.json` as the default run log name, in the same configurable output folder as the CSV.

    9.6. `[AGC-0169]` Decision: the Moneydance importer should write status columns back to `amazon-gift-card-transactions.csv`.

        9.6.1. `[AGC-0170]` Include status columns such as `MD Import`, `MD Verify`, and `MD Failure reason`.

        9.6.2. `[AGC-0171]` Each imported entry should be verified against Amazon after reading, and the verification result should be reflected in the status columns.

    9.7. `[AGC-0172]` Decision: the Moneydance transaction description should match the Amazon screen description text.

        9.7.1. `[AGC-0173]` For example, when Amazon shows `Refund from Amazon.com order 112-0668394-3541018`, use that exact normalized description text without HTML or link formatting.

    9.8. `[AGC-0174]` Decision: the Step 2 importer should not create categories, tags, or extra memos for Gift Card rows.

        9.8.1. `[AGC-0175]` The destination is the `Amazon Gift Card` account, with the transaction description populated from the Amazon screen text.

    9.9. `[AGC-0176]` Decision: multiple Gift Card rows with the same date, amount, and transaction type must be allowed as separate real transactions.

        9.9.1. `[AGC-0177]` Treat identical-looking rows as separate unless a stable Amazon transaction identifier or exact generated source fingerprint proves they are the same row.

    9.10. `[AGC-0178]` Recommendation: use both a configurable page-count safety limit and a one-year hard date safety limit.

        9.10.1. `[AGC-0179]` Default the hard date safety limit to one year back from the extraction run date, while still respecting the configured extractor date range.
## 10. Implementation Notes

    10.1. `[AGC-0180]` Step 1 implementation status note. Status: Tested

        10.1.1. `[AGC-0181]` Added `giftcard.js` as a dedicated Gift Card activity extractor in the Amazon Configurable Extractor. Status: Implemented

        10.1.2. `[AGC-0182]` Added popup controls for `Extract Gift Card Activity Only`, configurable Gift Card CSV filename, configurable Gift Card run log filename, maximum page count, and hard date limit years. Status: Implemented

        10.1.3. `[AGC-0183]` Added separate export support for `amazon-gift-card-transactions.csv` and `amazon-gift-card-transactions-run-log.json`. Status: Implemented

        10.1.4. `[AGC-0184]` Verified JavaScript syntax for `giftcard.js`, `popup.js`, `popup-defaults.js`, `export.js`, and `background.js` with `node --check`. Status: Tested

        10.1.5. `[AGC-0185]` Live Amazon Gift Card activity page extraction still requires manual or browser-session verification against the user's signed-in Amazon account. Status: Tested
        10.1.6. `[AGC-0186]` Fixed the first live trial issue where the popup could target an arbitrary Amazon tab instead of the active Gift Card Activity tab, and made Gift Card extraction navigate away from order transaction-detail pages before scraping. Status: Tested
        10.1.7. `[AGC-0187]` Fixed workflow-specific tab selection so order extraction and Gift Card extraction can coexist with separate Amazon tabs open; fixed Gift Card pagination bookkeeping by saving the next page count before clicking `Next` and waiting for rows to settle before scraping. Status: Tested
        10.1.8. `[AGC-0188]` Verified the 1.4.2 Gift Card run captured 49 verified rows across four processed pages, but found it started from a paginated Gift Card URL and skipped newer rows outside that starting point; fixed new Gift Card runs to reset paginated `next=` URLs back to the newest Gift Card activity page before collecting. Status: Tested
        10.1.9. `[AGC-0189]` Verified the 1.4.3 live Gift Card extraction run from `2026-01-01` through `2026-09-10`: exported 64 rows, processed five pages, reached below the configured start date, produced zero unverified rows, zero blank debug IDs, and zero duplicate source fingerprints. Status: Tested
        10.1.10. `[AGC-0190]` Fixed potential `Run extraction` startup issue when multiple Amazon tabs are open: ordinary transaction extraction now prefers transaction/order-detail tabs over unrelated Amazon tabs and forces startup to the Amazon payments transaction list unless already on that list. Status: Implemented
        10.1.11. `[AGC-0191]` Renamed popup actions: `Run extraction` became `Get Transactions`, `Extract Gift Card Activity Only` became `Get GC transactions`, and added `Get All` to run Gift Card transactions first and regular transactions second. Status: Implemented
        10.1.12. `[AGC-0192]` Added explicit Gift Card CSV `Balance` column from the activity table closing balance, changed `Source fingerprint` to hash Date, Description, normalized Amount, and Balance, and documented `Debug transaction ID` as diagnostic only. Status: Implemented



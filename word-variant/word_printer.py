#!/usr/bin/env python3
"""
Prototype Word automation script.

Requirements (Windows dev machine for testing):
- Python 3.x
- pywin32 (pip install pywin32)

Usage examples:
  python word_printer.py --config config.json
  python word_printer.py --files file-list.json --date 2026-01-05 --test

Notes:
- This is a prototype. Duplex (two-sided) printing is driver-specific; this script sets the ActivePrinter but may not force duplex on all drivers.
"""
import os
import sys
import json
import argparse
import datetime
import re

# Basic logging to file (also captures stdout/stderr)
import logging
import time

try:
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'word_printer.log')
    logging.basicConfig(level=logging.INFO, filename=log_path,
                        format='%(asctime)s %(levelname)s %(message)s')

    class StreamToLogger(object):
        def __init__(self, logger, level=logging.INFO):
            self.logger = logger
            self.level = level
            self._buffer = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.level, line)

        def flush(self):
            try:
                pass
            except Exception:
                pass

    sys.stdout = StreamToLogger(logging.getLogger('word_printer'), logging.INFO)
    sys.stderr = StreamToLogger(logging.getLogger('word_printer'), logging.ERROR)
    logging.getLogger('word_printer').info('Logging initialized, log file: %s', log_path)
except Exception:
    # If logging setup fails, continue without logging to file
    pass


def format_date_for_word(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%B %d, %Y")


MONTH_RE = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_RE = rf"(?:{MONTH_RE}\s+\d{{1,2}},\s*\d{{4}}|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}})"
DATE_UNDERSCORE_RE = re.compile(
    r"(?i)(?P<prefix>\bDate\b\s*:?)"
    r"(?P<ws1>\s*)"
    r"(?P<left>_+)"
    r"(?P<ws2>\s*)"
    r"(?P<date>[^_\r\n]+?)"
    r"(?P<ws3>\s*)"
    r"(?P<right>_+)"
)
DATE_INLINE_RE = re.compile(
    rf"(?i)(?P<prefix>\bDate\b\s*:?)"
    rf"(?P<ws1>\s*)"
    rf"(?P<left>_{{1,}})?"
    rf"(?P<ws2>\s*)"
    rf"(?P<date>{DATE_RE})"
    rf"(?P<ws3>\s*)"
    rf"(?P<right>_{{1,}})?"
)
DATE_EMPTY_LINE_RE = re.compile(
    r"(?i)(?P<leading>\s*)"
    r"(?P<prefix>\bDate\b\s*:?)"
    r"(?P<ws1>\s*)"
    r"(?P<left>_+)?"
    r"(?P<ws2>\s*)"
    r"(?P<right>_+)?"
    r"(?P<ws3>\s*)$"
)


def replace_date_text(text, formatted_date):
    def repl(match):
        def normalized_prefix():
            ws1 = match.group('ws1') if 'ws1' in match.groupdict() else ""
            spacer = ws1 if ws1 else " "
            return f"Date:{spacer}"

        left = match.group('left') or ""
        right = match.group('right') or ""
        if not left and not right:
            left = "__"
            right = "__"
        return (
            f"{normalized_prefix()}"
            f"{left}{match.group('ws2')}{formatted_date}{match.group('ws3')}{right}"
        )

    if DATE_UNDERSCORE_RE.search(text):
        return DATE_UNDERSCORE_RE.sub(repl, text, count=1)
    if DATE_INLINE_RE.search(text):
        return DATE_INLINE_RE.sub(repl, text, count=1)

    lines = text.splitlines(True)
    for idx, line in enumerate(lines):
        if 'Date' not in line and 'date' not in line:
            continue
        if DATE_INLINE_RE.search(line) or DATE_UNDERSCORE_RE.search(line):
            continue
        match = DATE_EMPTY_LINE_RE.search(line)
        if not match:
            continue
        left = match.group('left') or ""
        right = match.group('right') or ""
        if not left and not right:
            left = "__"
            right = "__"
        ws1 = match.group('ws1') or " "
        lines[idx] = (
            f"{match.group('leading')}Date:{ws1}"
            f"{left}{match.group('ws2')}{formatted_date}{match.group('ws3')}{right}"
        )
        return "".join(lines)
    return text


def run_replacement_tests(formatted_date):
    samples = [
        "Date:     January 1, 2026",
        "Date:\tJanuary 1, 2026",
        "Date : January 1, 2026",
        "Date\t:\tJanuary 1, 2026",
        "Date     January 1, 2026",
        "Date: ",
        "Date: January 1, 2026",
        "Date: _January 1, 2026",
        "Date: _1/1/2026_",
        "Date: __January 1, 2026__",
        "Date: January 1, 2026_",
        "Date: _January 1, 2026_",
        "Date:",
        "Date: ____",
        "Date 1/1/2026",
        "Header left    Date: _1/1/2026_    Room 3",
    ]
    print("Replacement test harness")
    print(f"Using formatted date: {formatted_date}")
    print("")
    for s in samples:
        out = replace_date_text(s, formatted_date)
        print(f"IN : {s}")
        print(f"OUT: {out}")
        print("")


def replace_date_in_headers(doc, formatted_date):
    # Iterate sections and headers/footers; perform a simple replacement strategy.
    # Preserve underscore spacing when a date is already underscored.
    for section in doc.Sections:
        # Headers collection: iterate by index (1-based COM collection)
        try:
            headers = section.Headers
            for i in range(1, headers.Count + 1):
                hdr = headers.Item(i)
                rng = hdr.Range
                txt = rng.Text
                if 'Date' in txt or 'date' in txt:
                    newtxt = replace_date_text(txt, formatted_date)
                    if newtxt != txt:
                        rng.Text = newtxt
        except Exception:
            pass

        try:
            footers = section.Footers
            for i in range(1, footers.Count + 1):
                ftr = footers.Item(i)
                rng = ftr.Range
                txt = rng.Text
                if 'Date' in txt or 'date' in txt:
                    newtxt = replace_date_text(txt, formatted_date)
                    if newtxt != txt:
                        rng.Text = newtxt
        except Exception:
            pass


def replace_date_in_body(doc, formatted_date):
    try:
        rng = doc.Content
        txt = rng.Text
        if 'Date' in txt or 'date' in txt:
            newtxt = replace_date_text(txt, formatted_date)
            # replace entire document text (conservative)
            if newtxt != txt:
                rng.Text = newtxt
                return True
    except Exception:
        return False
    return False


def replace_fields(doc, formatted_date):
    try:
        for i in range(1, doc.Fields.Count + 1):
            f = doc.Fields.Item(i)
            try:
                code = f.Code.Text if f.Code is not None else ''
                if 'DATE' in code.upper():
                    # attempt to set the displayed result
                    try:
                        f.Result.Text = formatted_date
                    except Exception:
                        pass
                    try:
                        f.Update()
                    except Exception:
                        pass
            except Exception:
                continue
    except Exception:
        pass


def replace_content_controls(doc, formatted_date):
    try:
        for i in range(1, doc.ContentControls.Count + 1):
            cc = doc.ContentControls.Item(i)
            try:
                title = getattr(cc, 'Title', '') or ''
                tag = getattr(cc, 'Tag', '') or ''
                rngtxt = getattr(cc.Range, 'Text', '') or ''
                if any(x in (title + tag + rngtxt).lower() for x in ['date', 'Date'.lower()]):
                    newtxt = replace_date_text(rngtxt, formatted_date)
                    if newtxt != rngtxt:
                        cc.Range.Text = newtxt
            except Exception:
                continue
    except Exception:
        pass


def process_files(file_paths, config):
    try:
        import win32com.client
        import pythoncom
        import win32print
        import win32con
    except Exception:
        print("This prototype must be run on Windows with pywin32 installed.")
        raise

    pythoncom.CoInitialize()
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False

    if config.get('printer_name'):
        try:
            word.ActivePrinter = config['printer_name']
            print(f"Set ActivePrinter to {config['printer_name']}")
        except Exception as e:
            print(f"Warning: failed to set ActivePrinter: {e}")

    # Try to enforce duplex at the printer driver level if requested
    if config.get('duplex') and isinstance(config.get('duplex'), dict) and config['duplex'].get('enabled'):
        try:
            def try_set_printer_duplex(printer_name, mode):
                try:
                    hPrinter = win32print.OpenPrinter(printer_name)
                    pinfo = win32print.GetPrinter(hPrinter, 2)
                    devmode = pinfo.get('pDevMode')
                    if not devmode:
                        win32print.ClosePrinter(hPrinter)
                        return False
                    # DEVMODE duplex values: 1=Simplex, 2=Long-edge, 3=Short-edge
                    if mode == 'long-edge':
                        devmode.Duplex = 2
                    else:
                        devmode.Duplex = 3
                    try:
                        devmode.Fields |= win32con.DM_DUPLEX
                    except Exception:
                        pass
                    pinfo['pDevMode'] = devmode
                    win32print.SetPrinter(hPrinter, 2, pinfo, 0)
                    win32print.ClosePrinter(hPrinter)
                    return True
                except Exception as e:
                    print('  Warning: failed to set printer duplex via DEVMODE:', e)
                    try:
                        win32print.ClosePrinter(hPrinter)
                    except Exception:
                        pass
                    return False

            ok = try_set_printer_duplex(config.get('printer_name'), config['duplex'].get('mode', 'long-edge'))
            if ok:
                print('  Duplex preference set at driver level')
            else:
                print('  Duplex preference could not be enforced at driver level; will attempt via Word and fallback if needed')
        except Exception as e:
            print('  Duplex enforcement attempt failed:', e)

    for p in file_paths:
        p_expanded = os.path.expanduser(p)
        if not os.path.isabs(p_expanded):
            p_expanded = os.path.abspath(p_expanded)
        print(f"Processing: {p_expanded}")
        if not os.path.exists(p_expanded):
            print("  SKIP: file not found")
            continue

        try:
            doc = word.Documents.Open(p_expanded)
        except Exception as e:
            print(f"  Failed to open: {e}")
            continue

        try:
            # Apply page setup and margins if present
            try:
                if config.get('orientation'):
                    # 1 = landscape, 0 = portrait
                    doc.PageSetup.Orientation = 1 if config.get('orientation') == 'landscape' else 0
                if config.get('margins_in_inches'):
                    m = config.get('margins_in_inches')
                    # Word uses points (72 points = 1 inch)
                    if 'top' in m: doc.PageSetup.TopMargin = float(m['top']) * 72
                    if 'bottom' in m: doc.PageSetup.BottomMargin = float(m['bottom']) * 72
                    if 'left' in m: doc.PageSetup.LeftMargin = float(m['left']) * 72
                    if 'right' in m: doc.PageSetup.RightMargin = float(m['right']) * 72
            except Exception as e:
                print('  Warning: failed to apply page setup:', e)

            replace_date_in_headers(doc, config['formatted_date'])
            replace_fields(doc, config['formatted_date'])
            replace_content_controls(doc, config['formatted_date'])
            replace_date_in_body(doc, config['formatted_date'])
            print("  Updated document content")

            # Build PrintOut args
            copies = int(config.get('copies', 1))
            collate = bool(config.get('collate', True))
            pages_mode = config.get('pages', 'all')
            pages_arg = config.get('page_range', '')
            try:
                if pages_mode == 'range' and pages_arg:
                    # Range printing uses Range=3 (wdPrintRangeOfPages)
                    doc.PrintOut(Range=3, Pages=pages_arg, Copies=copies, Collate=collate, Background=False)
                else:
                    doc.PrintOut(Copies=copies, Collate=collate, Background=False)
                print("  Sent to printer")
            except Exception as e:
                print(f"  Print failed: {e}")

            # Save or close according to test mode
            if config.get('test_mode'):
                doc.Close(SaveChanges=False)
                print("  Closed without saving (test mode)")
            else:
                try:
                    doc.Save()
                    print('  Saved document')
                except Exception as e:
                    print('  Warning: save failed', e)
                try:
                    doc.Close(SaveChanges=False)
                except Exception:
                    pass
                print("  Closed")

        except Exception as e:
            print(f"  Error processing document: {e}")
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass

    try:
        word.Quit()
    except Exception:
        pass


def load_config(path):
    cfg = {}
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fh:
            cfg = json.load(fh)
    return cfg


def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass


def resolve_relative(base_dir, p):
    # If p is absolute, return as-is, otherwise join with base_dir
    if os.path.isabs(p):
        return p
    return os.path.abspath(os.path.join(base_dir, p))


def main():
    ap = argparse.ArgumentParser(description='Prototype Word printer automation')
    ap.add_argument('--config', help='Path to config.json', default='config.json')
    ap.add_argument('--files', help='Path to file-list.json (array of paths)')
    ap.add_argument('--date', help='Print date (YYYY-MM-DD). Defaults to tomorrow', default=None)
    ap.add_argument('--test', help='Run in test mode (do not save)', action='store_true')
    ap.add_argument('--test-replace', help='Run date replacement tests and exit', action='store_true')
    args = ap.parse_args()
    if args.test_replace:
        date_str = args.date or (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        formatted = format_date_for_word(date_str)
        run_replacement_tests(formatted)
        return
    # Determine directories for locating config/file-list so exe can be run from anywhere.
    exe_dir = None
    try:
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        exe_dir = os.getcwd()

    # Search for config in the following order:
    # 1) explicit --config arg
    # 2) current working directory
    # 3) directory of the script/exe
    # 4) %APPDATA%/ScatterplotPrinter/config.json
    cfg = {}
    if args.config and os.path.exists(args.config):
        cfg = load_config(args.config)
        cfg_base = os.path.dirname(os.path.abspath(args.config))
    else:
        tried = []
        # cwd
        cwd_cfg = os.path.join(os.getcwd(), 'config.json')
        tried.append(cwd_cfg)
        if os.path.exists(cwd_cfg):
            cfg = load_config(cwd_cfg)
            cfg_base = os.path.dirname(cwd_cfg)
        else:
            exe_cfg = os.path.join(exe_dir, 'config.json')
            tried.append(exe_cfg)
            if os.path.exists(exe_cfg):
                cfg = load_config(exe_cfg)
                cfg_base = os.path.dirname(exe_cfg)
            else:
                appdata = os.getenv('APPDATA')
                if appdata:
                    app_cfg_dir = os.path.join(appdata, 'ScatterplotPrinter')
                    app_cfg = os.path.join(app_cfg_dir, 'config.json')
                    tried.append(app_cfg)
                    if os.path.exists(app_cfg):
                        cfg = load_config(app_cfg)
                        cfg_base = os.path.dirname(app_cfg)
                # if still not found, cfg remains {}

    # Find file list using multiple fallbacks and resolve relative paths against the file-list file location
    file_list = []
    file_list_base = None

    def try_load_file_list(path):
        nonlocal file_list_base
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as fh:
                    arr = json.load(fh)
                file_list_base = os.path.dirname(os.path.abspath(path))
                return arr
        except Exception:
            return None
        return None

    # 1) explicit --files
    if args.files:
        arr = try_load_file_list(args.files)
        if arr is None:
            print('files list not found:', args.files)
            sys.exit(1)
        file_list = arr

    # 2) config.file_list
    if not file_list and cfg.get('file_list'):
        arr = try_load_file_list(cfg.get('file_list'))
        if arr:
            file_list = arr

    # 3) search common locations: cwd, exe_dir, APPDATA
    if not file_list:
        candidates = [os.path.join(os.getcwd(), 'file-list.json'), os.path.join(exe_dir, 'file-list.json')]
        appdata = os.getenv('APPDATA')
        if appdata:
            candidates.append(os.path.join(appdata, 'ScatterplotPrinter', 'file-list.json'))
        for c in candidates:
            arr = try_load_file_list(c)
            if arr:
                file_list = arr
                break

    if not file_list:
        print('No files to process. Provide --files, config.file_list, or place file-list.json in working dir, exe dir, or %APPDATA%\\ScatterplotPrinter\\')
        sys.exit(1)

    # Resolve relative file paths relative to the file-list.json location (file_list_base)
    resolved_paths = []
    base = file_list_base or os.getcwd()
    for p in file_list:
        resolved_paths.append(resolve_relative(base, p))
    file_list = resolved_paths

    date_str = args.date or cfg.get('default_date') or (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    formatted = format_date_for_word(date_str)

    runtime_cfg = {
        'printer_name': cfg.get('printer_name') or cfg.get('printerName') or None,
        'duplex': cfg.get('duplex', False),
        'test_mode': args.test or cfg.get('testMode', False),
        'formatted_date': formatted,
    }

    print('Runtime config:', runtime_cfg)
    process_files(file_list, runtime_cfg)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Scatterplot Printer - Main Application

A simple GUI app that:
1. Maintains a list of Word documents (auto-saved)
2. Lets user pick a date to write to documents
3. Prints all documents with the updated date
4. Uses default printer with duplex (long-edge) by default
"""
import json
import os
import sys
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Determine base directory for config storage
def get_app_data_dir():
    """Get the app data directory for storing config and file list."""
    if sys.platform == 'win32':
        appdata = os.getenv('APPDATA')
        if appdata:
            app_dir = os.path.join(appdata, 'ScatterplotPrinter')
        else:
            app_dir = os.path.dirname(__file__)
    else:
        app_dir = os.path.dirname(__file__)

    os.makedirs(app_dir, exist_ok=True)
    return app_dir

APP_DATA_DIR = get_app_data_dir()
CONFIG_PATH = os.path.join(APP_DATA_DIR, 'config.json')
FILELIST_PATH = os.path.join(APP_DATA_DIR, 'file-list.json')

# Default configuration
DEFAULT_CONFIG = {
    "test_mode": True,
    "duplex_mode": "long-edge",  # "long-edge", "short-edge", or "none"
    "printer": "",  # Empty string means default printer
    "last_date": None,
}


def get_available_printers():
    """Get list of available printers. Returns list of printer names."""
    printers = []
    try:
        import platform
        if platform.system() == 'Windows':
            import win32print
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                printers.append(printer[2])  # printer[2] is the name
        else:
            # On Mac/Linux, just return empty - will show placeholder
            pass
    except Exception:
        pass
    return printers


def load_json(path, default):
    """Load JSON file, return default if not found or invalid."""
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path, data):
    """Save data to JSON file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {path}: {e}")


def format_date_for_word(date_obj):
    """Format date as 'January 5, 2026' for Word documents."""
    return date_obj.strftime("%B %d, %Y").replace(" 0", " ")  # Remove leading zero from day


class ScatterplotPrinterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scatterplot Printer')
        self.geometry('700x550')
        self.configure(bg='#1a1a1a')

        # Load saved data
        self.config_data = load_json(CONFIG_PATH, DEFAULT_CONFIG.copy())
        self.file_list = load_json(FILELIST_PATH, [])

        # Ensure file list is a list (handle old format)
        if not isinstance(self.file_list, list):
            self.file_list = []

        self.create_widgets()
        self.refresh_file_list()

    def create_widgets(self):
        # Style configuration for ttk widgets
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Configure combobox colors
        style.configure('TCombobox',
                        fieldbackground='#2a2a2a',
                        background='#2a2a2a',
                        foreground='white')
        style.map('TCombobox',
                  fieldbackground=[('readonly', '#2a2a2a')],
                  selectbackground=[('readonly', '#4a90a4')],
                  selectforeground=[('readonly', 'white')])

        # Configure button styles
        style.configure('Blue.TButton',
                        background='#4a90a4',
                        foreground='white',
                        font=('Segoe UI', 10, 'bold'),
                        padding=(12, 6))
        style.map('Blue.TButton',
                  background=[('active', '#3a7080')])

        style.configure('Gray.TButton',
                        background='#3a3a3a',
                        foreground='white',
                        font=('Segoe UI', 10),
                        padding=(12, 6))
        style.map('Gray.TButton',
                  background=[('active', '#4a4a4a')])

        style.configure('Green.TButton',
                        background='#27ae60',
                        foreground='white',
                        font=('Segoe UI', 12, 'bold'),
                        padding=(24, 12))
        style.map('Green.TButton',
                  background=[('active', '#1e8449')])

        # Main container
        main_frame = tk.Frame(self, bg='#1a1a1a', padx=16, pady=16)
        main_frame.pack(fill='both', expand=True)

        # Title
        title_label = tk.Label(main_frame, text='Scatterplot Printer',
                               font=('Segoe UI', 18, 'bold'),
                               bg='#1a1a1a', fg='white')
        title_label.pack(anchor='w', pady=(0, 4))

        subtitle_label = tk.Label(main_frame,
                                  text='Update dates and print Word documents automatically',
                                  font=('Segoe UI', 10), bg='#1a1a1a', fg='#888888')
        subtitle_label.pack(anchor='w', pady=(0, 16))

        # === File List Section ===
        file_section = tk.Frame(main_frame, bg='#2a2a2a', padx=12, pady=12)
        file_section.pack(fill='both', expand=True, pady=(0, 12))

        file_header = tk.Frame(file_section, bg='#2a2a2a')
        file_header.pack(fill='x', pady=(0, 8))

        tk.Label(file_header, text='Documents', font=('Segoe UI', 12, 'bold'),
                 bg='#2a2a2a', fg='white').pack(side='left')

        file_count_var = tk.StringVar(value='0 files')
        self.file_count_label = tk.Label(file_header, textvariable=file_count_var,
                                          font=('Segoe UI', 10), bg='#2a2a2a', fg='#888888')
        self.file_count_label.pack(side='right')
        self.file_count_var = file_count_var

        # Listbox with scrollbar
        list_frame = tk.Frame(file_section, bg='#1a1a1a')
        list_frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.listbox = tk.Listbox(list_frame, selectmode='extended',
                                   bg='#1a1a1a', fg='white',
                                   selectbackground='#4a90a4', selectforeground='white',
                                   font=('Segoe UI', 10), borderwidth=0,
                                   highlightthickness=0,
                                   yscrollcommand=scrollbar.set)
        self.listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)

        # File buttons
        file_btns = tk.Frame(file_section, bg='#2a2a2a')
        file_btns.pack(fill='x', pady=(8, 0))

        add_btn = ttk.Button(file_btns, text='+ Add Files', command=self.add_files,
                             style='Blue.TButton')
        add_btn.pack(side='left')

        remove_btn = ttk.Button(file_btns, text='Remove Selected', command=self.remove_selected,
                                style='Gray.TButton')
        remove_btn.pack(side='left', padx=(8, 0))

        clear_btn = ttk.Button(file_btns, text='Clear All', command=self.clear_all,
                               style='Gray.TButton')
        clear_btn.pack(side='left', padx=(8, 0))

        # === Settings Section ===
        settings_frame = tk.Frame(main_frame, bg='#2a2a2a', padx=12, pady=12)
        settings_frame.pack(fill='x', pady=(0, 12))

        # Printer row
        printer_row = tk.Frame(settings_frame, bg='#2a2a2a')
        printer_row.pack(fill='x', pady=(0, 8))

        tk.Label(printer_row, text='Printer:', font=('Segoe UI', 11, 'bold'),
                 bg='#2a2a2a', fg='white').pack(side='left')

        # Get available printers
        available_printers = get_available_printers()
        printer_options = ['Default Printer'] + available_printers

        saved_printer = self.config_data.get('printer', '')
        if saved_printer and saved_printer in available_printers:
            default_printer = saved_printer
        else:
            default_printer = 'Default Printer'

        self.printer_var = tk.StringVar(value=default_printer)
        printer_menu = ttk.Combobox(printer_row, textvariable=self.printer_var,
                                     values=printer_options, state='readonly',
                                     width=35, font=('Segoe UI', 10))
        printer_menu.pack(side='left', padx=(12, 0))
        printer_menu.bind('<<ComboboxSelected>>', lambda e: self.save_config())

        # Date picker row
        date_row = tk.Frame(settings_frame, bg='#2a2a2a')
        date_row.pack(fill='x', pady=(0, 8))

        tk.Label(date_row, text='Date to print:', font=('Segoe UI', 11, 'bold'),
                 bg='#2a2a2a', fg='white').pack(side='left')

        # Default to tomorrow
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        # Month dropdown
        self.month_var = tk.StringVar(value=tomorrow.strftime('%B'))
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        month_menu = ttk.Combobox(date_row, textvariable=self.month_var, values=months,
                                   state='readonly', width=12, font=('Segoe UI', 10))
        month_menu.pack(side='left', padx=(12, 4))

        # Day dropdown
        self.day_var = tk.StringVar(value=str(tomorrow.day))
        days = [str(i) for i in range(1, 32)]
        day_menu = ttk.Combobox(date_row, textvariable=self.day_var, values=days,
                                 state='readonly', width=4, font=('Segoe UI', 10))
        day_menu.pack(side='left', padx=(0, 4))

        tk.Label(date_row, text=',', font=('Segoe UI', 11),
                 bg='#2a2a2a', fg='white').pack(side='left')

        # Year dropdown
        current_year = tomorrow.year
        self.year_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year - 1, current_year + 3)]
        year_menu = ttk.Combobox(date_row, textvariable=self.year_var, values=years,
                                  state='readonly', width=6, font=('Segoe UI', 10))
        year_menu.pack(side='left', padx=(4, 0))

        # Options row
        options_row = tk.Frame(settings_frame, bg='#2a2a2a')
        options_row.pack(fill='x')

        # Test mode checkbox
        self.test_mode_var = tk.BooleanVar(value=self.config_data.get('test_mode', True))
        test_cb = tk.Checkbutton(options_row, text="Test Mode (print but don't save changes)",
                                  variable=self.test_mode_var, command=self.save_config,
                                  bg='#2a2a2a', fg='white', selectcolor='#3a3a3a',
                                  activebackground='#2a2a2a', activeforeground='white',
                                  font=('Segoe UI', 10))
        test_cb.pack(side='left')

        # === Action Section ===
        action_frame = tk.Frame(main_frame, bg='#1a1a1a')
        action_frame.pack(fill='x')

        # Print button
        self.print_btn = ttk.Button(action_frame, text='Print All Documents',
                                     command=self.print_all,
                                     style='Green.TButton')
        self.print_btn.pack(side='left')

        # Status label
        self.status_var = tk.StringVar(value='Ready')
        status_label = tk.Label(action_frame, textvariable=self.status_var,
                                font=('Segoe UI', 10), bg='#1a1a1a', fg='#888888')
        status_label.pack(side='left', padx=(16, 0))

        # Info text
        info_frame = tk.Frame(main_frame, bg='#1a1a1a')
        info_frame.pack(fill='x', pady=(12, 0))

        info_text = "• Prints duplex (both sides, flip on long edge)"
        tk.Label(info_frame, text=info_text, font=('Segoe UI', 9),
                 bg='#1a1a1a', fg='#666666', justify='left').pack(anchor='w')

    def refresh_file_list(self):
        """Refresh the listbox with current file list, sorted by filename."""
        self.listbox.delete(0, 'end')

        # Sort by filename (basename), case-insensitive
        sorted_files = sorted(self.file_list, key=lambda x: os.path.basename(x).lower())
        self.file_list = sorted_files  # Keep sorted

        for path in sorted_files:
            # Show just the filename, with full path on hover (via tooltip)
            filename = os.path.basename(path)
            self.listbox.insert('end', f"  {filename}")

        # Update count
        count = len(self.file_list)
        self.file_count_var.set(f'{count} file{"s" if count != 1 else ""}')

        # Auto-save
        self.save_file_list()

    def add_files(self):
        """Add files via file picker."""
        # macOS needs different filetype format
        import platform
        if platform.system() == 'Darwin':
            filetypes = [('Word Documents', '*.docx *.doc'), ('All Files', '*')]
        else:
            filetypes = [('Word Documents', '*.doc;*.docx'), ('All Files', '*.*')]

        files = filedialog.askopenfilenames(
            title='Select Word Documents',
            filetypes=filetypes
        )
        if files:
            added = 0
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
                    added += 1
            if added > 0:
                self.refresh_file_list()
                self.status_var.set(f'Added {added} file{"s" if added != 1 else ""}')

    def remove_selected(self):
        """Remove selected files from list."""
        selections = list(self.listbox.curselection())
        if not selections:
            return

        # Remove in reverse order to maintain indices
        for i in reversed(selections):
            if i < len(self.file_list):
                self.file_list.pop(i)

        self.refresh_file_list()
        self.status_var.set(f'Removed {len(selections)} file{"s" if len(selections) != 1 else ""}')

    def clear_all(self):
        """Clear all files from list."""
        if not self.file_list:
            return

        if messagebox.askyesno('Clear All', 'Remove all files from the list?'):
            self.file_list = []
            self.refresh_file_list()
            self.status_var.set('List cleared')

    def save_file_list(self):
        """Auto-save file list."""
        save_json(FILELIST_PATH, self.file_list)

    def save_config(self):
        """Save configuration."""
        self.config_data['test_mode'] = self.test_mode_var.get()
        # Save printer (empty string for default)
        printer = self.printer_var.get()
        self.config_data['printer'] = '' if printer == 'Default Printer' else printer
        save_json(CONFIG_PATH, self.config_data)

    def get_selected_date(self):
        """Get the date selected in the UI."""
        try:
            month_name = self.month_var.get()
            day = int(self.day_var.get())
            year = int(self.year_var.get())

            # Convert month name to number
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            month = months.index(month_name) + 1

            return datetime.date(year, month, day)
        except Exception:
            return datetime.date.today() + datetime.timedelta(days=1)

    def print_all(self):
        """Process and print all documents."""
        if not self.file_list:
            messagebox.showwarning('No Files', 'Please add some Word documents first.')
            return

        # Get selected date
        selected_date = self.get_selected_date()
        formatted_date = format_date_for_word(selected_date)
        test_mode = self.test_mode_var.get()

        # Confirm
        msg = f"Ready to process {len(self.file_list)} document(s).\n\n"
        msg += f"Date: {formatted_date}\n"
        msg += f"Printer: {self.printer_var.get()}\n\n"
        if test_mode:
            msg += "TEST MODE:\n"
            msg += "  • Documents WILL print\n"
            msg += "  • Changes will NOT be saved"
        else:
            msg += "PRODUCTION MODE:\n"
            msg += "  • Documents WILL print\n"
            msg += "  • Changes WILL be saved"

        if not messagebox.askyesno('Confirm Print', msg):
            return

        # Disable button during processing
        self.print_btn.config(state='disabled')
        self.print_btn_original_text = 'Print All Documents'
        self.status_var.set('Processing documents...')
        self.update()

        # Get selected printer
        selected_printer = self.printer_var.get()
        printer_name = None if selected_printer == 'Default Printer' else selected_printer

        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.run_print_job,
                                   args=(formatted_date, test_mode, printer_name))
        thread.start()

    def run_print_job(self, formatted_date, test_mode, printer_name):
        """Run the print job (in background thread)."""
        try:
            from word_printer import process_files

            config = {
                'printer_name': printer_name,  # None = default printer
                'duplex': {'enabled': True, 'mode': 'long-edge'},
                'test_mode': test_mode,
                'formatted_date': formatted_date,
            }

            process_files(self.file_list, config)

            # Update UI on main thread
            self.after(0, self.print_complete, True, len(self.file_list))

        except Exception as e:
            self.after(0, self.print_complete, False, str(e))

    def print_complete(self, success, result):
        """Called when print job completes."""
        self.print_btn.config(state='normal')

        if success:
            self.status_var.set(f'Completed: {result} document(s) processed')
            messagebox.showinfo('Complete', f'Successfully processed {result} document(s).')
        else:
            self.status_var.set('Error occurred')
            messagebox.showerror('Error', f'An error occurred:\n\n{result}')


def main():
    app = ScatterplotPrinterApp()
    app.mainloop()


if __name__ == '__main__':
    main()

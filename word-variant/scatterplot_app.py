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
    "last_date": None,
}


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
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')

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

        add_btn = tk.Button(file_btns, text='+ Add Files', command=self.add_files,
                            bg='#4a90a4', fg='white', font=('Segoe UI', 10, 'bold'),
                            padx=12, pady=6, borderwidth=0, cursor='hand2')
        add_btn.pack(side='left')

        remove_btn = tk.Button(file_btns, text='Remove Selected', command=self.remove_selected,
                               bg='#3a3a3a', fg='white', font=('Segoe UI', 10),
                               padx=12, pady=6, borderwidth=0, cursor='hand2')
        remove_btn.pack(side='left', padx=(8, 0))

        clear_btn = tk.Button(file_btns, text='Clear All', command=self.clear_all,
                              bg='#3a3a3a', fg='white', font=('Segoe UI', 10),
                              padx=12, pady=6, borderwidth=0, cursor='hand2')
        clear_btn.pack(side='left', padx=(8, 0))

        # === Settings Section ===
        settings_frame = tk.Frame(main_frame, bg='#2a2a2a', padx=12, pady=12)
        settings_frame.pack(fill='x', pady=(0, 12))

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
        test_cb = tk.Checkbutton(options_row, text='Test Mode (preview only, no printing)',
                                  variable=self.test_mode_var, command=self.save_config,
                                  bg='#2a2a2a', fg='white', selectcolor='#3a3a3a',
                                  activebackground='#2a2a2a', activeforeground='white',
                                  font=('Segoe UI', 10))
        test_cb.pack(side='left')

        # === Action Section ===
        action_frame = tk.Frame(main_frame, bg='#1a1a1a')
        action_frame.pack(fill='x')

        # Print button
        self.print_btn = tk.Button(action_frame, text='▶  Print All Documents',
                                    command=self.print_all,
                                    bg='#27ae60', fg='white', font=('Segoe UI', 12, 'bold'),
                                    padx=24, pady=12, borderwidth=0, cursor='hand2')
        self.print_btn.pack(side='left')

        # Status label
        self.status_var = tk.StringVar(value='Ready')
        status_label = tk.Label(action_frame, textvariable=self.status_var,
                                font=('Segoe UI', 10), bg='#1a1a1a', fg='#888888')
        status_label.pack(side='left', padx=(16, 0))

        # Info text
        info_frame = tk.Frame(main_frame, bg='#1a1a1a')
        info_frame.pack(fill='x', pady=(12, 0))

        info_text = "• Documents print duplex (both sides, flip on long edge)\n• Uses your default printer"
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
        files = filedialog.askopenfilenames(
            title='Select Word Documents',
            filetypes=[('Word Documents', '*.doc;*.docx'), ('All Files', '*.*')]
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
        action = "preview" if test_mode else "print"
        msg = f"This will {action} {len(self.file_list)} document(s).\n\n"
        msg += f"Date to write: {formatted_date}\n"
        if test_mode:
            msg += "\n(Test mode: documents won't actually print or save)"
        else:
            msg += "\nDocuments will be printed and saved with the new date."

        if not messagebox.askyesno(f'Confirm {action.title()}', msg):
            return

        # Disable button during processing
        self.print_btn.config(state='disabled', text='Processing...')
        self.status_var.set('Processing documents...')
        self.update()

        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.run_print_job,
                                   args=(formatted_date, test_mode))
        thread.start()

    def run_print_job(self, formatted_date, test_mode):
        """Run the print job (in background thread)."""
        try:
            from word_printer import process_files

            config = {
                'printer_name': None,  # Use default printer
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
        self.print_btn.config(state='normal', text='▶  Print All Documents')

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

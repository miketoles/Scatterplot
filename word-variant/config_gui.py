import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
FILELIST_PATH = os.path.join(BASE_DIR, 'file-list.json')


def load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


class ConfigGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Scatterplot Printer — Config Editor')
        self.geometry('700x480')

        self.config_data = load_json(CONFIG_PATH, {})
        self.file_list = load_json(FILELIST_PATH, [])

        # Left: config fields
        left = tk.Frame(self)
        left.pack(side='left', fill='both', expand=True, padx=8, pady=8)

        # Printer name
        tk.Label(left, text='Printer Name:').pack(anchor='w')
        self.printer_entry = tk.Entry(left)
        self.printer_entry.pack(fill='x')

        # Copies and collate
        f = tk.Frame(left)
        f.pack(fill='x', pady=6)
        tk.Label(f, text='Copies:').pack(side='left')
        self.copies_var = tk.IntVar(value=1)
        tk.Entry(f, width=4, textvariable=self.copies_var).pack(side='left', padx=6)
        self.collate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(f, text='Collate', variable=self.collate_var).pack(side='left', padx=6)

        # Duplex
        tk.Label(left, text='Duplex:').pack(anchor='w')
        duplex_frame = tk.Frame(left)
        duplex_frame.pack(fill='x')
        self.duplex_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(duplex_frame, text='Enable duplex enforcement', variable=self.duplex_enabled).pack(side='left')
        tk.Label(duplex_frame, text='Mode:').pack(side='left', padx=6)
        self.duplex_mode_var = tk.StringVar(value='long-edge')
        tk.OptionMenu(duplex_frame, self.duplex_mode_var, 'long-edge', 'short-edge').pack(side='left')

        # Page range
        tk.Label(left, text='Page range (leave blank for all):').pack(anchor='w', pady=(8,0))
        self.page_range_entry = tk.Entry(left)
        self.page_range_entry.pack(fill='x')

        # Test mode
        self.test_mode_var = tk.BooleanVar(value=True)
        tk.Checkbutton(left, text='Test mode (do not print)', variable=self.test_mode_var).pack(anchor='w', pady=6)

        # Save buttons
        btn_frame = tk.Frame(left)
        btn_frame.pack(fill='x', pady=8)
        tk.Button(btn_frame, text='Load config', command=self.load_config).pack(side='left')
        tk.Button(btn_frame, text='Save config', command=self.save_config).pack(side='left', padx=6)

        # Right: file list
        right = tk.Frame(self)
        right.pack(side='right', fill='both', expand=True, padx=8, pady=8)
        tk.Label(right, text='File list (document paths):').pack(anchor='w')
        self.listbox = tk.Listbox(right, selectmode='extended')
        self.listbox.pack(fill='both', expand=True)
        self.refresh_file_list()

        file_btns = tk.Frame(right)
        file_btns.pack(fill='x', pady=6)
        tk.Button(file_btns, text='Add files', command=self.add_files).pack(side='left')
        tk.Button(file_btns, text='Remove selected', command=self.remove_selected).pack(side='left', padx=6)
        tk.Button(file_btns, text='Save file list', command=self.save_file_list).pack(side='left', padx=6)

        bottom = tk.Frame(self)
        bottom.pack(fill='x', padx=8, pady=8)
        tk.Button(bottom, text='Open config folder', command=self.open_folder).pack(side='left')
        tk.Button(bottom, text='Quit', command=self.quit).pack(side='right')

        self.load_config()

    def open_folder(self):
        import subprocess, sys
        path = BASE_DIR
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', path])
        else:
            messagebox.showinfo('Open folder', path)

    def refresh_file_list(self):
        self.listbox.delete(0, 'end')
        for p in self.file_list:
            self.listbox.insert('end', p)

    def add_files(self):
        files = filedialog.askopenfilenames(title='Select Word files', filetypes=[('Word','*.doc;*.docx'),('All','*.*')])
        if files:
            for f in files:
                if f not in self.file_list:
                    self.file_list.append(f)
            self.refresh_file_list()

    def remove_selected(self):
        sels = list(self.listbox.curselection())
        sels.reverse()
        for i in sels:
            try:
                self.file_list.pop(i)
            except Exception:
                pass
        self.refresh_file_list()

    def load_config(self):
        cfg = load_json(CONFIG_PATH, {})
        self.config_data = cfg
        self.printer_entry.delete(0, 'end')
        self.printer_entry.insert(0, cfg.get('printer_name', ''))
        self.copies_var.set(cfg.get('copies', 1))
        self.collate_var.set(cfg.get('collate', True))
        self.duplex_enabled.set(cfg.get('duplex', {}).get('enabled', True))
        self.duplex_mode_var.set(cfg.get('duplex', {}).get('mode', 'long-edge'))
        self.page_range_entry.delete(0, 'end')
        self.page_range_entry.insert(0, cfg.get('page_range', ''))
        self.test_mode_var.set(cfg.get('test_mode', True))
        # load file list too
        self.file_list = load_json(FILELIST_PATH, [])
        self.refresh_file_list()

    def save_config(self):
        cfg = dict(self.config_data)
        cfg['printer_name'] = self.printer_entry.get()
        cfg['copies'] = int(self.copies_var.get())
        cfg['collate'] = bool(self.collate_var.get())
        cfg['duplex'] = { 'enabled': bool(self.duplex_enabled.get()), 'mode': self.duplex_mode_var.get() }
        cfg['page_range'] = self.page_range_entry.get()
        cfg['test_mode'] = bool(self.test_mode_var.get())
        save_json(CONFIG_PATH, cfg)
        messagebox.showinfo('Saved', f'Saved config to {CONFIG_PATH}')

    def save_file_list(self):
        save_json(FILELIST_PATH, self.file_list)
        messagebox.showinfo('Saved', f'Saved file list to {FILELIST_PATH}')


if __name__ == '__main__':
    app = ConfigGUI()
    app.mainloop()

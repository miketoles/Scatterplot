# 🖨️ Scatterplot Printer - Windows Setup Guide
## For Users WITHOUT Admin Privileges

---

## 📋 **What You're Building:**
A standalone `.exe` file that you can:
- Run on your work computer (no admin needed)
- Share with your 12 team members
- Double-click to use (no installation required)

---

## 🎯 **Quick Start (Recommended Method)**

### **Option A: Use Portable Python (NO ADMIN REQUIRED)**

This is the easiest method and requires zero admin privileges.

#### **Step 1: Download Portable Python**

1. Go to: https://www.python.org/downloads/windows/
2. Download **"Windows embeddable package (64-bit)"** for Python 3.11 or 3.12
   - Look for: `python-3.11.x-embed-amd64.zip` or similar
3. Extract the ZIP to a folder like: `C:\Users\YourName\PortablePython`

#### **Step 2: Get the Files**

1. Download `scatterplot_printer_v2.py` from this project
2. Put it in the same folder as your portable Python

#### **Step 3: Install pip (Package Manager)**

1. Download `get-pip.py` from: https://bootstrap.pypa.io/get-pip.py
2. Save it to your PortablePython folder
3. Open Command Prompt (Win+R, type `cmd`, press Enter)
4. Navigate to your folder:
   ```
   cd C:\Users\YourName\PortablePython
   ```
5. Run:
   ```
   python.exe get-pip.py
   ```

#### **Step 4: Fix Python Path (Important!)**

1. In your PortablePython folder, find `python311._pth` (or similar)
2. Right-click → Open with Notepad
3. Uncomment the line with `import site` (remove the `#` at the start)
4. Save and close

#### **Step 5: Install Required Packages**

In Command Prompt (still in your PortablePython folder):

```batch
python.exe -m pip install PyQt5
python.exe -m pip install openpyxl
python.exe -m pip install pywin32
python.exe -m pip install pyinstaller
```

**If pywin32 fails**, try:
```batch
python.exe -m pip install pypiwin32
```

#### **Step 6: Build the EXE**

Still in Command Prompt:

```batch
python.exe -m PyInstaller --onefile --windowed --name "ScatterplotPrinter" scatterplot_printer_v2.py
```

**This will take 2-5 minutes. You'll see lots of output. That's normal!**

#### **Step 7: Find Your EXE**

Look in: `C:\Users\YourName\PortablePython\dist\ScatterplotPrinter.exe`

**This is your finished program!** 🎉

---

## 🎯 **Option B: If You Already Have Python Installed**

### **Step 1: Check if Python is Installed**

Open Command Prompt and type:
```
python --version
```

If you see "Python 3.x.x", you're good! If not, use Option A above.

### **Step 2: Install Packages**

```batch
python -m pip install --user PyQt5 openpyxl pywin32 pyinstaller
```

**Note:** The `--user` flag installs without admin privileges.

### **Step 3: Build the EXE**

Navigate to where you saved `scatterplot_printer_v2.py`:

```batch
cd C:\Users\YourName\Downloads
python -m PyInstaller --onefile --windowed --name "ScatterplotPrinter" scatterplot_printer_v2.py
```

### **Step 4: Get Your EXE**

Find it in: `C:\Users\YourName\Downloads\dist\ScatterplotPrinter.exe`

---

## 📦 **Sharing with Your Team**

### **Step 1: Copy the EXE**

The `.exe` file is completely standalone. Just copy `ScatterplotPrinter.exe` to:
- A network drive (e.g., `L:\Tools\ScatterplotPrinter.exe`)
- Or email it to your team
- Or put it on a USB drive

### **Step 2: Create Desktop Shortcuts (Optional)**

For each team member:

1. Right-click on their desktop → New → Shortcut
2. Browse to `L:\Tools\ScatterplotPrinter.exe` (or wherever you put it)
3. Click Next → Name it "Scatterplot Printer" → Finish

Now everyone can just double-click the desktop icon!

---

## 🧪 **First Time Testing**

### **IMPORTANT: Start in Test Mode!**

1. Double-click `ScatterplotPrinter.exe`
2. **Test Mode should already be checked** (it's the default)
3. Click "Add Excel Files"
4. Browse to `L:\Behavior Plans`
5. Select ONE scatterplot file to start
6. Set tomorrow's date
7. Click "Print Selected Files"

**What happens:**
- File opens
- Date gets updated in memory
- File is sent to printer
- **File is NOT saved** (because Test Mode is ON)
- Original file is untouched

**Check the file manually** to make sure the date would have been correct!

### **When You're Confident:**

1. Uncheck "Test Mode"
2. Now files WILL be saved with the new date
3. Run a real print job!

---

## 🐛 **Troubleshooting**

### **Problem: "Python not found"**

**Solution:** Use Option A (Portable Python) - it doesn't require Python to be installed system-wide.

---

### **Problem: "pip is not recognized"**

**Solution:** Use the full path:
```batch
python -m pip install --user PyQt5
```

The `-m pip` tells Python to run pip as a module.

---

### **Problem: "Access Denied" or "Permission Error"**

**Solution:** Make sure you're installing to your user directory:
```batch
python -m pip install --user [package_name]
```

Or use Option A (Portable Python in your Documents/Downloads).

---

### **Problem: PyInstaller says "Cannot find PyQt5"**

**Solution:** Make sure you installed in the same Python environment:

1. Check which Python:
   ```
   where python
   ```
2. Use that exact path when installing:
   ```
   C:\Users\YourName\PortablePython\python.exe -m pip install PyQt5
   ```

---

### **Problem: EXE is flagged by antivirus**

**Solution:** This is normal for PyInstaller executables.

**Options:**
1. Add an exception in Windows Defender for the file
2. Have your IT department whitelist it
3. Or just run the Python script directly (see Alternative Method below)

---

### **Problem: The EXE doesn't find printers**

**Cause:** pywin32 didn't install properly.

**Solution:**
1. The app will still work! 
2. You'll need to type the printer name manually
3. Or you can still browse files and print manually

**To fix:**
```batch
python -m pip uninstall pywin32
python -m pip install pypiwin32
```

Then rebuild the EXE.

---

## 🔄 **Alternative Method: Run Python Script Directly**

If building an EXE is too complicated, you can just run the Python script!

### **Step 1: Install Python Portable (same as Option A above)**

### **Step 2: Install Packages**
```batch
python.exe -m pip install PyQt5 openpyxl pywin32
```

### **Step 3: Create a Batch File**

Create a text file called `RunScatterplotPrinter.bat` with:

```batch
@echo off
C:\Users\YourName\PortablePython\python.exe scatterplot_printer_v2.py
pause
```

**Adjust the path to match where you put Portable Python!**

### **Step 4: Double-Click the .bat File**

Now you (and your team) can just double-click `RunScatterplotPrinter.bat` to run the app!

**Put both files on the network drive:**
- `L:\Tools\scatterplot_printer_v2.py`
- `L:\Tools\RunScatterplotPrinter.bat`

---

## 📁 **Recommended Folder Structure**

On your network drive:

```
L:\Tools\
├── ScatterplotPrinter.exe          (The standalone app)
├── ScatterplotPrinter - Instructions.txt
└── Shortcuts for Desktop.txt
```

Or if using the script method:

```
L:\Tools\ScatterplotPrinter\
├── scatterplot_printer_v2.py
├── RunScatterplotPrinter.bat
└── PortablePython\
    └── (all the portable python files)
```

---

## ⚙️ **Configuration Tips**

### **Pre-Configure Settings for Your Team**

Before sharing, you can create a `scatterplot_config_v2.json` file:

```json
{
  "base_path": "L:\\Behavior Plans",
  "date_cell": "A1",
  "printer_name": "\\\\SERVER\\YourPrinterName",
  "test_mode": true
}
```

Put this file in the SAME folder as the .exe

Now when team members first open the app, these settings are already configured!

---

## 🎯 **Quick Reference Card for Team Members**

**Print this out for your team:**

```
═══════════════════════════════════════════
  SCATTERPLOT PRINTER - QUICK GUIDE
═══════════════════════════════════════════

1. OPEN: Double-click ScatterplotPrinter.exe

2. TEST FIRST: 
   ✓ Leave "Test Mode" checked
   ✓ Try with 1 file first

3. ADD FILES:
   ✓ Click "Add Excel Files"
   ✓ Browse to L:\Behavior Plans
   ✓ Select all scatterplots you want to print
   ✓ Click Open

4. SET DATE:
   ✓ Select tomorrow's date
   ✓ Or click "Tomorrow" button

5. PRINT:
   ✓ Click "Print Selected Files"
   ✓ Check one file manually to verify
   ✓ If correct, uncheck "Test Mode"
   ✓ Run again for real

═══════════════════════════════════════════
IMPORTANT: Always check Test Mode results
before unchecking it!
═══════════════════════════════════════════
```

---

## 📊 **Expected File Sizes**

- **Python script:** ~20 KB
- **EXE file:** 50-100 MB (includes all dependencies)
- **PortablePython folder:** ~30 MB

The EXE is large because it includes Python + all packages in one file.

---

## ✅ **Success Checklist**

Before sharing with team:

- [ ] EXE runs on your computer
- [ ] Test Mode works (doesn't save files)
- [ ] Can select multiple files
- [ ] Date format looks correct
- [ ] Files print successfully
- [ ] Live Mode saves files correctly
- [ ] Created instructions for team
- [ ] Set up network location
- [ ] Tested on second computer

---

## 🆘 **Need Help?**

If you run into issues:

1. Check which step failed
2. Read the error message carefully
3. Try the Alternative Method (batch file + Python script)
4. Check that you're not running from a restricted folder

**Most common issue:** Trying to install in C:\Program Files (requires admin)

**Solution:** Install everything in your user folder: `C:\Users\YourName\`

---

## 🚀 **You're Ready!**

Follow Option A (Portable Python) if you want the simplest path.

The whole process takes about 15-20 minutes the first time.

Good luck! 🎉
```

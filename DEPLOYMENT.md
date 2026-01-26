# NRT Scatterplot Creator - Deployment Guide

This guide covers deploying NRT Scatterplot Creator to Windows machines without requiring administrator rights.

## Package Options

Two deployment packages are available:

| Package | Best For | Installation |
|---------|----------|--------------|
| **Portable ZIP** | Network shares, USB drives, quick testing | Extract and run |
| **NSIS Installer** | Individual workstations, desktop shortcuts | Run installer |

Both packages work without administrator privileges.

---

## Building the Packages

### Prerequisites
- Node.js 18+ installed
- Windows machine (or cross-compilation setup)

### Build Commands

```bash
# Install dependencies (includes electron-builder)
npm install

# Build both portable and installer
npm run build:all

# Or build individually:
npm run build:portable    # Creates ZIP only
npm run build:installer   # Creates EXE installer only
```

### Output Location

Built packages appear in the `dist/` folder:
- `NRT Scatterplot Creator-Portable-1.0.0.zip` - Portable version
- `NRT Scatterplot Creator Setup 1.0.0.exe` - NSIS installer

---

## Deployment Option 1: Portable ZIP (Recommended)

### Quick Install (Recommended)

The ZIP includes an installer script that handles everything automatically:

1. **Extract** `NRT Scatterplot Creator-Portable-1.0.0.zip` (right-click → Extract All)

2. **Open** the extracted folder

3. **Double-click** `install.bat`

4. **Done!** A desktop shortcut is created automatically

The installer:
- Copies the app to `%LOCALAPPDATA%\Programs\NRT Scatterplot Creator\`
- Creates a desktop shortcut
- Prompts before overwriting existing installations
- Data is stored on the network share (not locally)

**Note:** Each user needs to run the installer once on their machine. After that, the app runs locally but reads/writes data from the shared network location.

### Manual Installation

If you prefer to install manually:

1. Extract the ZIP

2. Copy all files (except `install.bat`) to:
   ```
   %LOCALAPPDATA%\Programs\NRT Scatterplot Creator\
   ```

   This typically resolves to:
   ```
   C:\Users\YourName\AppData\Local\Programs\NRT Scatterplot Creator\
   ```

3. Create a desktop shortcut pointing to:
   ```
   %LOCALAPPDATA%\Programs\NRT Scatterplot Creator\NRT Scatterplot Creator.exe
   ```

### Why Local Installation?

Electron apps (like this one) don't run reliably from network shares due to GPU process restrictions in Chromium. Installing locally ensures:
- Reliable startup every time
- Better performance
- No GPU process errors

The app still reads/writes all data from the network share - only the application files are local.

---

## Deployment Option 2: NSIS Installer

### Running the Installer

1. Double-click `NRT Scatterplot Creator Setup 1.0.0.exe`
2. If SmartScreen warning appears, click "More info" then "Run anyway"
3. Choose installation directory (default: `%LOCALAPPDATA%\Programs\NRT Scatterplot Creator`)
4. Select shortcut options:
   - Desktop shortcut
   - Start Menu shortcut
5. Click Install

### Default Installation Paths
- **Application**: `%LOCALAPPDATA%\Programs\NRT Scatterplot Creator\`
- **User Data**: `%APPDATA%\nrt-scatterplot-creator\`

### Uninstalling
- Use "Add or Remove Programs" in Windows Settings
- Or run the uninstaller from the installation directory

---

## First-Run Configuration

The application comes pre-configured with default paths for NRT deployment:

| Setting | Default Path |
|---------|-------------|
| **Data Location** | `L:\BI Program Behavior Plans\Scatterplot Creator Data\data` |
| **PDF Export** | `L:\BI Program Behavior Plans\Scatterplot Creator Data\pdf output` |

**For most users, no configuration is needed.** The app will automatically use these paths.

### Changing Paths (If Needed)

If you need to use different paths:

1. Click the **Settings** (⚙️) button in the top right
2. Click **Browse...** next to the path you want to change
3. Select the new folder
4. The change takes effect immediately

### Configuration Storage

User settings are stored locally in:
```
%APPDATA%\nrt-scatterplot-creator\settings.json
```

This means each user can have their own data path configuration if needed, even when running from a shared network location.

### Resetting to Defaults

To reset paths to the built-in defaults, delete the settings file:
```
%APPDATA%\nrt-scatterplot-creator\settings.json
```

---

## Network Share Setup

### NRT Folder Structure

The application expects this folder structure on the L: drive:

```
L:\BI Program Behavior Plans\
├── Scatterplot Creator\              # Application files
│   ├── NRT Scatterplot Creator.exe   # Main executable
│   ├── resources\
│   ├── locales\
│   └── ... (other app files)
│
└── Scatterplot Creator Data\         # Shared data
    ├── data\                         # JSON data files
    │   ├── patients.json
    │   ├── doctors.json
    │   ├── bcbas.json
    │   └── config.json
    │
    └── pdf output\                   # Generated PDFs
        └── (exported scatterplots)
```

### Share Permissions

| Folder | Users Need |
|--------|------------|
| `Scatterplot Creator\` | Read & Execute |
| `Scatterplot Creator Data\data\` | Read, Write, Modify |
| `Scatterplot Creator Data\pdf output\` | Read, Write, Modify |

### Creating the Folder Structure

If setting up for the first time:

1. Create the folders on the network share:
   ```
   L:\BI Program Behavior Plans\Scatterplot Creator\
   L:\BI Program Behavior Plans\Scatterplot Creator Data\data\
   L:\BI Program Behavior Plans\Scatterplot Creator Data\pdf output\
   ```

2. Extract the portable ZIP and copy `win-unpacked` contents to the `Scatterplot Creator` folder

3. The app will automatically create the JSON data files on first run

### Network Performance Notes

- The app loads entirely into memory on startup
- PDF generation happens locally; only the output file is written to the network
- Large data files may take longer to load over slow network connections

---

## Updating the Application

### Portable Version (Network Share)
1. Close the application on all machines
2. Replace files on the network share with new version
3. Users get the update on next launch

### Installed Version
1. Distribute new installer to users
2. Users run installer (will upgrade in place)
3. Or uninstall old version first, then install new

---

## Troubleshooting

### SmartScreen Warning
**Issue**: Windows SmartScreen blocks the application

**Solution**:
1. Click "More info" on the warning dialog
2. Click "Run anyway"
3. This only happens on first run

### Application Won't Start from Network Share
**Issue**: App fails to launch or shows security error

**Solutions**:
- Ensure the network path is in the Windows "Trusted Sites" or Intranet zone
- Try mapping the network share to a drive letter (e.g., `Z:\`)
- Check that users have Execute permissions on the share

### "Path Not Found" Errors
**Issue**: App can't find data files

**Solutions**:
- Verify the configured data path exists and is accessible
- Check network connectivity to the data share
- Re-run the data path configuration from the app menu

### PDF Generation Fails
**Issue**: PDF files aren't created or are corrupted

**Solutions**:
- Verify write permissions to the output directory
- Ensure sufficient disk space
- Check that the output path doesn't contain invalid characters

### Settings Not Persisting
**Issue**: Configuration resets on each launch

**Solutions**:
- Verify `%APPDATA%` folder exists and is writable
- Check for roaming profile issues
- Settings file location: `%APPDATA%\nrt-scatterplot-creator\settings.json`

---

## IT Administration: Eliminating SmartScreen Warnings

Since the application is not code-signed, Windows SmartScreen will display a warning on first run. IT administrators can use the following methods to whitelist the application for a smoother user experience.

### Option 1: Group Policy (Recommended for Domain Environments)

Add the application to SmartScreen exceptions via Group Policy:

1. Open **Group Policy Management Console**
2. Navigate to: `Computer Configuration > Administrative Templates > Windows Components > Windows Defender SmartScreen > Explorer`
3. Configure **"Configure App Install Control"** to allow apps from anywhere, OR
4. Use **"Configure Windows Defender SmartScreen"** to set to "Warn" instead of "Block"

Alternatively, whitelist by publisher or file hash:
1. Navigate to: `Computer Configuration > Windows Settings > Security Settings > Application Control Policies > AppLocker`
2. Create a new rule to allow the application by path or file hash

### Option 2: Microsoft Intune / Endpoint Manager

For organizations using Intune:

1. Go to **Microsoft Endpoint Manager admin center**
2. Navigate to: `Devices > Configuration profiles`
3. Create a new profile with **Settings catalog**
4. Search for "SmartScreen" and configure:
   - `Smart Screen Enabled` = Off (not recommended), OR
   - Deploy the app as a **Win32 app** with Intune, which marks it as trusted

### Option 3: Windows Defender Exclusions

Add the application folder to Windows Defender exclusions:

**Via Group Policy:**
1. Navigate to: `Computer Configuration > Administrative Templates > Windows Components > Microsoft Defender Antivirus > Exclusions`
2. Configure **"Path Exclusions"**
3. Add the application path: `L:\BI Program Behavior Plans\Scatterplot Creator\`

**Via PowerShell (run as Administrator):**
```powershell
Add-MpPreference -ExclusionPath "L:\BI Program Behavior Plans\Scatterplot Creator"
```

### Option 4: Network Location in Intranet Zone

If deploying from a network share, add the share to the Local Intranet zone:

1. Open **Internet Options** (via Control Panel or Group Policy)
2. Go to **Security** tab > **Local intranet** > **Sites** > **Advanced**
3. Add the server: `file://server` or `\\server`

This reduces security prompts for applications run from that location.

### Option 5: Code Signing Certificate (Permanent Solution)

For a permanent solution that works for all users without IT configuration:

| Certificate Type | Cost | Result |
|-----------------|------|--------|
| Standard Code Signing | ~$70-200/year | Reduced warnings (reputation builds over time) |
| EV Code Signing | ~$300-500/year | Immediate trust, no SmartScreen warnings |

Providers: DigiCert, Sectigo, SSL.com

Contact the application maintainer if code signing is required.

---

## System Requirements

- **OS**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4 GB minimum
- **Disk**: 200 MB for application
- **Network**: Required only if using network shares

---

## Support

For issues not covered in this guide, contact your IT administrator or the application maintainer.

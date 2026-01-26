const { app, BrowserWindow, ipcMain, dialog, shell } = require("electron");
const fs = require("fs");
const os = require("os");
const path = require("path");

const SETTINGS_FILE = path.join(app.getPath("userData"), "settings.json");
const TEMPLATES_DIR = path.join(__dirname, "data-templates");

// ─────────────────────────────────────────────────────────────────────────────
// HTML-to-PDF Generation using Electron's printToPDF
// ─────────────────────────────────────────────────────────────────────────────

async function generatePDFFromHTML(patientsData, outputPath) {
  return new Promise((resolve, reject) => {
    // Create a hidden window to render the HTML
    const pdfWindow = new BrowserWindow({
      width: 1056,  // 11 inches at 96 DPI
      height: 816,  // 8.5 inches at 96 DPI
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true
      }
    });

    // Load the template file
    const templatePath = path.join(__dirname, "pdf-template.html");
    pdfWindow.loadFile(templatePath);

    pdfWindow.webContents.on("did-finish-load", async () => {
      try {
        // Inject the patient data into the page
        const dataJson = JSON.stringify(patientsData);
        await pdfWindow.webContents.executeJavaScript(`
          try {
            const patientsData = ${dataJson};
            renderAllPatients(patientsData);
          } catch (e) {
            console.error('Failed to render:', e);
          }
        `);

        // Wait for images to load and rendering to complete
        await new Promise(r => setTimeout(r, 800));

        const pdfData = await pdfWindow.webContents.printToPDF({
          landscape: true,
          pageSize: "Letter",
          printBackground: true,
          margins: {
            top: 0,
            bottom: 0,
            left: 0,
            right: 0
          }
        });

        fs.writeFileSync(outputPath, pdfData);
        pdfWindow.close();
        resolve(outputPath);
      } catch (error) {
        pdfWindow.close();
        reject(error);
      }
    });

    pdfWindow.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
      pdfWindow.close();
      reject(new Error(`Failed to load PDF template: ${errorDescription}`));
    });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Utility Functions
// ─────────────────────────────────────────────────────────────────────────────

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function readJson(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch (e) {
    console.error(`Error reading ${filePath}:`, e);
    return fallback;
  }
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function copyTemplateIfMissing(filename) {
  const destPath = path.join(getDataRoot(), filename);
  if (!fs.existsSync(destPath)) {
    const templatePath = path.join(TEMPLATES_DIR, filename);
    if (fs.existsSync(templatePath)) {
      fs.copyFileSync(templatePath, destPath);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Data Root / Settings
// ─────────────────────────────────────────────────────────────────────────────

// Default paths for NRT deployment
const DEFAULT_DATA_ROOT = "L:\\BI Program Behavior Plans\\Scatterplot Creator Data\\data";
const DEFAULT_PDF_ROOT = "L:\\BI Program Behavior Plans\\Scatterplot Creator Data\\pdf output";

function getDataRoot() {
  const settings = readJson(SETTINGS_FILE, {});
  return settings.dataRoot || DEFAULT_DATA_ROOT;
}

function setDataRoot(root) {
  const settings = readJson(SETTINGS_FILE, {});
  settings.dataRoot = root;
  writeJson(SETTINGS_FILE, settings);
}

function getPdfExportRoot() {
  const settings = readJson(SETTINGS_FILE, {});
  return settings.pdfExportRoot || DEFAULT_PDF_ROOT;
}

function setPdfExportRoot(root) {
  const settings = readJson(SETTINGS_FILE, {});
  settings.pdfExportRoot = root;
  writeJson(SETTINGS_FILE, settings);
}

function ensureDataDirs() {
  const root = getDataRoot();
  const pdfRoot = getPdfExportRoot();
  ensureDir(root);
  ensureDir(pdfRoot);

  // Copy template files if they don't exist
  copyTemplateIfMissing("patients.json");
  copyTemplateIfMissing("doctors.json");
  copyTemplateIfMissing("bcbas.json");
  copyTemplateIfMissing("config.json");

  return root;
}

function getConfigFile() {
  return path.join(getDataRoot(), "config.json");
}

function loadConfig() {
  return readJson(getConfigFile(), { maxBehaviors: 4 });
}

// ─────────────────────────────────────────────────────────────────────────────
// File Paths
// ─────────────────────────────────────────────────────────────────────────────

function getPatientsFile() {
  return path.join(getDataRoot(), "patients.json");
}

function getDoctorsFile() {
  return path.join(getDataRoot(), "doctors.json");
}

function getBcbasFile() {
  return path.join(getDataRoot(), "bcbas.json");
}

// ─────────────────────────────────────────────────────────────────────────────
// User Identity
// ─────────────────────────────────────────────────────────────────────────────

function getUserIdentity() {
  const envUser = process.env.USERNAME || process.env.USER || process.env.LOGNAME || "";
  let username = "";
  try {
    username = os.userInfo().username || envUser;
  } catch (error) {
    username = envUser;
  }
  const domain = process.env.USERDOMAIN || process.env.USERDNSDOMAIN || "";
  return { username, domain };
}

function getUserDisplayName() {
  const { username, domain } = getUserIdentity();
  return domain ? `${domain}\\${username}` : username;
}

// ─────────────────────────────────────────────────────────────────────────────
// Date Utilities
// ─────────────────────────────────────────────────────────────────────────────

function getTomorrowDate() {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split("T")[0]; // YYYY-MM-DD
}

function dateStamp(value) {
  if (!value) {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${now.getFullYear()}${month}${day}`;
  }
  const isoPrefix = value.match(/^(\d{4}-\d{2}-\d{2})/);
  if (isoPrefix) return isoPrefix[1].replace(/-/g, "");
  const parsed = Date.parse(value);
  if (!Number.isNaN(parsed)) {
    const dateObj = new Date(parsed);
    const month = String(dateObj.getMonth() + 1).padStart(2, "0");
    const day = String(dateObj.getDate()).padStart(2, "0");
    return `${dateObj.getFullYear()}${month}${day}`;
  }
  return dateStamp("");
}

// ─────────────────────────────────────────────────────────────────────────────
// Patients Data with Concurrency
// ─────────────────────────────────────────────────────────────────────────────

let cachedPatientsData = null;
let cachedLastModified = null;

function loadPatientsData() {
  const file = getPatientsFile();
  let data = readJson(file, { lastModified: null, modifiedBy: null, patients: [] });

  // Handle old format (raw array)
  if (Array.isArray(data)) {
    console.log("Migrating old patients.json format...");
    const oldPatients = data;
    data = {
      lastModified: null,
      modifiedBy: null,
      patients: oldPatients.map(p => ({
        id: p.id || generatePatientId(),
        displayId: p.patient || p.displayId || "",
        doctor: p.doctor || "",
        bcba: p.bcba || "",
        behaviors: p.behaviors || [{ title: "", description: "" }],
        createdAt: p.createdAt || new Date().toISOString(),
        updatedAt: p.updatedAt || new Date().toISOString()
      }))
    };
    // Save migrated data
    savePatientsData(data);
  }

  // Ensure structure
  if (!data.patients) data.patients = [];
  if (!data.lastModified) data.lastModified = null;
  if (!data.modifiedBy) data.modifiedBy = null;

  // Ensure each patient has required fields
  data.patients = data.patients.map(p => ({
    id: p.id || generatePatientId(),
    displayId: p.displayId || p.patient || "",
    doctor: p.doctor || "",
    bcba: p.bcba || "",
    behaviors: p.behaviors || [{ title: "", description: "" }],
    createdAt: p.createdAt || new Date().toISOString(),
    updatedAt: p.updatedAt || new Date().toISOString()
  }));

  return data;
}

function generatePatientId() {
  return 'patient-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

function savePatientsData(data) {
  data.lastModified = new Date().toISOString();
  data.modifiedBy = getUserDisplayName();
  writeJson(getPatientsFile(), data);
  cachedPatientsData = data;
  cachedLastModified = data.lastModified;
}

function checkConcurrency() {
  const currentData = loadPatientsData();
  if (cachedLastModified && currentData.lastModified &&
      cachedLastModified !== currentData.lastModified) {
    return {
      conflict: true,
      modifiedBy: currentData.modifiedBy,
      modifiedAt: currentData.lastModified,
      currentData
    };
  }
  return { conflict: false, currentData };
}

function mergePatientChanges(localData, remoteData, localChangedIds, remoteChangedIds) {
  // Find conflicts (same patient edited by both)
  const conflicts = localChangedIds.filter(id => remoteChangedIds.includes(id));

  if (conflicts.length === 0) {
    // No conflicts - auto-merge
    const merged = { ...remoteData };

    // Apply local changes to patients not in remote changes
    localChangedIds.forEach(id => {
      const localPatient = localData.patients.find(p => p.id === id);
      const remoteIdx = merged.patients.findIndex(p => p.id === id);

      if (localPatient) {
        if (remoteIdx >= 0) {
          merged.patients[remoteIdx] = localPatient;
        } else {
          merged.patients.push(localPatient);
        }
      } else {
        // Patient was deleted locally
        if (remoteIdx >= 0) {
          merged.patients.splice(remoteIdx, 1);
        }
      }
    });

    return { merged, conflicts: [] };
  }

  return { merged: null, conflicts };
}

// ─────────────────────────────────────────────────────────────────────────────
// Window Creation
// ─────────────────────────────────────────────────────────────────────────────

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true
    }
  });
  win.loadFile(path.join(__dirname, "index.html"));
}

app.whenReady().then(() => {
  ensureDataDirs();
  createWindow();
});

// ─────────────────────────────────────────────────────────────────────────────
// IPC Handlers
// ─────────────────────────────────────────────────────────────────────────────

// Load all patients
ipcMain.handle("loadPatients", () => {
  const data = loadPatientsData();
  cachedPatientsData = data;
  cachedLastModified = data.lastModified;
  return data;
});

// Save patients (with concurrency check)
ipcMain.handle("savePatients", async (_event, { patients, changedIds }) => {
  const { conflict, modifiedBy, modifiedAt, currentData } = checkConcurrency();

  if (conflict) {
    return {
      ok: false,
      conflict: true,
      modifiedBy,
      modifiedAt,
      currentData
    };
  }

  const data = loadPatientsData();
  data.patients = patients;
  savePatientsData(data);

  return { ok: true };
});

// Force save (overwrite conflicts)
ipcMain.handle("forceSavePatients", (_event, patients) => {
  const data = loadPatientsData();
  data.patients = patients;
  savePatientsData(data);
  return { ok: true };
});

// Load doctors list
ipcMain.handle("loadDoctors", () => {
  const data = readJson(getDoctorsFile(), { doctors: [] });
  return data.doctors || [];
});

// Load BCBAs list
ipcMain.handle("loadBcbas", () => {
  const data = readJson(getBcbasFile(), { bcbas: [] });
  return data.bcbas || [];
});

// Generate PDF and return path (using HTML-to-PDF)
ipcMain.handle("generatePdf", async (_event, { patient, date }) => {
  const outputDir = getPdfExportRoot();
  ensureDir(outputDir);

  const safeName = (patient.displayId || "patient").replace(/[^a-z0-9]+/gi, "_");
  const stamp = dateStamp(date);
  const outputPath = path.join(outputDir, `scatterplot_${safeName}_${stamp}.pdf`);

  const patientsData = [{
    patient: patient.displayId,
    doctor: patient.doctor,
    bcba: patient.bcba,
    date: date,
    behaviors: patient.behaviors
  }];

  await generatePDFFromHTML(patientsData, outputPath);
  return outputPath;
});

// Export PDF with save dialog (using HTML-to-PDF)
ipcMain.handle("exportPdf", async (_event, { patient, date }) => {
  const safeName = (patient.displayId || "patient").replace(/[^a-z0-9]+/gi, "_");
  const stamp = dateStamp(date);
  const defaultName = `scatterplot_${safeName}_${stamp}.pdf`;

  const result = await dialog.showSaveDialog({
    defaultPath: defaultName,
    filters: [{ name: "PDF Files", extensions: ["pdf"] }]
  });

  if (result.canceled || !result.filePath) {
    return { ok: false, canceled: true };
  }

  const patientsData = [{
    patient: patient.displayId,
    doctor: patient.doctor,
    bcba: patient.bcba,
    date: date,
    behaviors: patient.behaviors
  }];

  await generatePDFFromHTML(patientsData, result.filePath);
  return { ok: true, path: result.filePath };
});

// Generate combined PDF for printing (using HTML-to-PDF)
ipcMain.handle("generatePdfsForPrint", async (_event, { patients, date }) => {
  const tempDir = path.join(app.getPath("temp"), "nrt-scatterplot-print");
  ensureDir(tempDir);

  const timestamp = Date.now();
  const outputPath = path.join(tempDir, `scatterplots_${timestamp}.pdf`);

  const patientsData = patients.map(patient => ({
    patient: patient.displayId,
    doctor: patient.doctor,
    bcba: patient.bcba,
    date: date,
    behaviors: patient.behaviors
  }));

  await generatePDFFromHTML(patientsData, outputPath);

  return [outputPath];
});

// Open PDF folder
ipcMain.handle("openPdfFolder", () => {
  const outputDir = getPdfExportRoot();
  ensureDir(outputDir);
  shell.openPath(outputDir);
});

// Open data folder
ipcMain.handle("openDataFolder", () => {
  const dataDir = getDataRoot();
  ensureDir(dataDir);
  shell.openPath(dataDir);
});

// Get PDF export root
ipcMain.handle("getPdfExportRoot", () => {
  return getPdfExportRoot();
});

// Choose PDF export root
ipcMain.handle("choosePdfExportRoot", async () => {
  const current = getPdfExportRoot();
  const result = await dialog.showOpenDialog({
    defaultPath: current,
    properties: ["openDirectory"]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return { changed: false, path: current };
  }

  setPdfExportRoot(result.filePaths[0]);
  ensureDir(result.filePaths[0]);

  return { changed: true, path: result.filePaths[0] };
});

// Get data root
ipcMain.handle("getDataRoot", () => {
  return getDataRoot();
});

// Choose data root
ipcMain.handle("chooseDataRoot", async () => {
  const current = getDataRoot();
  const result = await dialog.showOpenDialog({
    defaultPath: current,
    properties: ["openDirectory"]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return { changed: false, path: current };
  }

  setDataRoot(result.filePaths[0]);
  ensureDataDirs();

  // Reset cache since we changed location
  cachedPatientsData = null;
  cachedLastModified = null;

  return { changed: true, path: getDataRoot() };
});

// Get user identity
ipcMain.handle("getUserIdentity", () => {
  return getUserIdentity();
});

// Get tomorrow's date
ipcMain.handle("getTomorrowDate", () => {
  return getTomorrowDate();
});

// Load config
ipcMain.handle("loadConfig", () => {
  return loadConfig();
});

// Print PDF file - opens in default viewer for user to print
ipcMain.handle("printPdf", async (_event, pdfPath) => {
  // Open PDF in default application (Preview on macOS, default PDF viewer on Windows)
  // User can then use the print dialog from there
  try {
    await shell.openPath(pdfPath);
    return { ok: true };
  } catch (error) {
    return { ok: false, error: error?.message };
  }
});

// Show confirmation dialog
ipcMain.handle("showConfirmDialog", async (_event, { title, message, detail }) => {
  const result = await dialog.showMessageBox({
    type: "warning",
    buttons: ["Cancel", "Delete"],
    defaultId: 0,
    cancelId: 0,
    title: title || "Confirm",
    message: message || "Are you sure?",
    detail: detail || ""
  });

  return result.response === 1; // true if "Delete" clicked
});

// Show conflict dialog
ipcMain.handle("showConflictDialog", async (_event, { patientId, modifiedBy }) => {
  const result = await dialog.showMessageBox({
    type: "question",
    buttons: ["Keep My Version", "Use Their Version", "Cancel"],
    defaultId: 2,
    cancelId: 2,
    title: "Edit Conflict",
    message: `Another user modified "${patientId}"`,
    detail: `${modifiedBy} made changes to this patient. Which version do you want to keep?`
  });

  return result.response; // 0 = keep mine, 1 = use theirs, 2 = cancel
});

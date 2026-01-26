const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  // Patient data
  loadPatients: () => ipcRenderer.invoke("loadPatients"),
  savePatients: (data) => ipcRenderer.invoke("savePatients", data),
  forceSavePatients: (patients) => ipcRenderer.invoke("forceSavePatients", patients),

  // Dropdown lists
  loadDoctors: () => ipcRenderer.invoke("loadDoctors"),
  loadBcbas: () => ipcRenderer.invoke("loadBcbas"),

  // PDF generation
  generatePdf: (data) => ipcRenderer.invoke("generatePdf", data),
  exportPdf: (data) => ipcRenderer.invoke("exportPdf", data),
  generatePdfsForPrint: (data) => ipcRenderer.invoke("generatePdfsForPrint", data),
  printPdf: (pdfPath) => ipcRenderer.invoke("printPdf", pdfPath),

  // Folders
  openPdfFolder: () => ipcRenderer.invoke("openPdfFolder"),
  openDataFolder: () => ipcRenderer.invoke("openDataFolder"),

  // Settings
  getDataRoot: () => ipcRenderer.invoke("getDataRoot"),
  chooseDataRoot: () => ipcRenderer.invoke("chooseDataRoot"),
  getPdfExportRoot: () => ipcRenderer.invoke("getPdfExportRoot"),
  choosePdfExportRoot: () => ipcRenderer.invoke("choosePdfExportRoot"),

  // User info
  getUserIdentity: () => ipcRenderer.invoke("getUserIdentity"),

  // Date helpers
  getTomorrowDate: () => ipcRenderer.invoke("getTomorrowDate"),

  // Config
  loadConfig: () => ipcRenderer.invoke("loadConfig"),

  // Dialogs
  showConfirmDialog: (data) => ipcRenderer.invoke("showConfirmDialog", data),
  showConflictDialog: (data) => ipcRenderer.invoke("showConflictDialog", data)
});

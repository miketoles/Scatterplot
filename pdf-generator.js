const fs = require("fs");
const path = require("path");
const PDFDocument = require("pdfkit");

// Page dimensions (matching UI CSS variables)
const INCH = 72;
const PAGE_WIDTH = 11 * INCH;   // 792pt
const PAGE_HEIGHT = 8.5 * INCH; // 612pt
const MARGIN = 0.5 * INCH;      // 36pt

// UI-matched styling constants
const BORDER_COLOR = "#666666";  // Lighter gray to match UI's thin borders
const LIGHT_BG = "#f2f2f2";
const HEADER_BG = "#f6f6f6";
const STROKE_WIDTH = 0.35;       // Very thin strokes to match CSS 1px borders at screen res

// Row height: UI uses 18px. At 96 DPI screen -> 72 DPI PDF conversion:
// 18px * (72/96) = 13.5pt, but we want visual match so use 13pt
const ROW_HEIGHT = 13;
const HEADER_ROW_HEIGHT = 26;  // Increased to fit multi-line behavior titles

// Font sizes (converted from CSS px to PDF pt, roughly 0.75 ratio)
const FONT_SIZE_HEADER = 9;      // Was 11pt, UI uses ~12px
const FONT_SIZE_LABEL = 8;       // UI uses ~10-11px
const FONT_SIZE_TIME = 7;        // UI uses 9px
const FONT_SIZE_DIRECTIONS = 8;  // UI uses 10px
const FONT_SIZE_FOOTER = 9;      // UI uses 12px
const FONT_SIZE_DESC_TITLE = 8;  // UI uses 9px
const FONT_SIZE_DESC_TEXT = 8;   // Increased for readability

function formatTime(hour24, minute) {
  const period = hour24 >= 12 ? "PM" : "AM";
  let hour12 = hour24 % 12;
  if (hour12 === 0) hour12 = 12;
  return `${hour12}:${String(minute).padStart(2, "0")} ${period}`;
}

function timeRows(startHour) {
  const rows = [];
  let hour = startHour;
  let minute = 0;
  for (let i = 0; i < 32; i++) {
    const startHourVal = hour;
    const startMin = minute;
    const endTotal = startMin + 14;
    const endHour = (startHourVal + Math.floor(endTotal / 60)) % 24;
    const endMin = endTotal % 60;
    const start = formatTime(startHourVal, startMin);
    const end = formatTime(endHour, endMin);
    rows.push(`${start} - ${end}`);
    minute += 15;
    if (minute >= 60) {
      minute = 0;
      hour = (hour + 1) % 24;
    }
  }
  return rows;
}

function formatDateDisplay(value) {
  const formatParts = (dateObj) => {
    const monthName = dateObj.toLocaleDateString("en-US", { month: "long" });
    const dayNum = dateObj.getDate();
    const yearNum = dateObj.getFullYear();
    return `${monthName} ${dayNum}, ${yearNum}`;
  };
  if (!value) {
    return formatParts(new Date());
  }
  const isoPrefix = value.match(/^(\d{4}-\d{2}-\d{2})/);
  if (isoPrefix) {
    const [year, month, day] = isoPrefix[1].split("-").map(Number);
    return formatParts(new Date(year, month - 1, day));
  }
  const parsed = Date.parse(value);
  if (!Number.isNaN(parsed)) {
    return formatParts(new Date(parsed));
  }
  return value;
}

function setStroke(doc) {
  doc.strokeColor(BORDER_COLOR).lineWidth(STROKE_WIDTH);
}

function drawHeader(doc, data, y, contentWidth) {
  // Match UI grid-template-columns: repeat(4, 1fr) 1.6fr
  const colWidths = [1, 1, 1, 1, 1.6];
  const colTotal = colWidths.reduce((a, b) => a + b, 0);
  const colUnit = contentWidth / colTotal;
  const cols = colWidths.map((w) => w * colUnit);

  const date = formatDateDisplay(data.date);
  const headerText = [
    `Date: ${date}`,
    `Doctor: ${data.doctor || ""}`,
    `Patient: ${data.patient || ""}`,
    `BCBA: ${data.bcba || ""}`
  ];

  doc.fontSize(FONT_SIZE_HEADER).font("Helvetica-Bold").fillColor("#000000");
  let x = MARGIN;
  headerText.forEach((text, idx) => {
    doc.text(text, x, y, { width: cols[idx], align: "left", lineBreak: false });
    x += cols[idx];
  });

  // Right column with Observer and Shift (stacked)
  const rightX = MARGIN + cols.slice(0, 4).reduce((a, b) => a + b, 0);
  const rightWidth = cols[4];
  doc.text("Observer: ____________________", rightX, y, { width: rightWidth, align: "right", lineBreak: false });
  doc.text("Shift: Day  Evening  Night", rightX, y + 12, { width: rightWidth, align: "right", lineBreak: false });

  return y + 28;
}

function drawBehaviorList(doc, behaviors, y) {
  const contentWidth = PAGE_WIDTH - 2 * MARGIN;
  const list = behaviors.map((beh, idx) => `${idx + 1}.) ${beh.title}`).join("   ");

  doc.fontSize(FONT_SIZE_LABEL).font("Helvetica-Bold").fillColor("#000000");
  doc.text(`Behaviors for data collection: ${list}`, MARGIN, y, {
    width: contentWidth,
    align: "left",
    lineBreak: false
  });

  doc.font("Helvetica-Bold").fontSize(FONT_SIZE_DIRECTIONS);
  doc.text("Directions: Please shade in the box, if one or all behavior occurs in 15-minute increments.", MARGIN, y + 11, {
    width: contentWidth,
    align: "center",
    lineBreak: false
  });

  return y + 24;
}

function drawGrid(doc, behaviors, startHour, yStart) {
  const contentWidth = PAGE_WIDTH - 2 * MARGIN;
  const behaviorsCount = behaviors.length;

  // Column widths matching UI: time 10%, check 4%, behaviors split remaining
  const timeWidth = contentWidth * 0.10;
  const checkWidth = contentWidth * 0.04;
  const remaining = contentWidth - timeWidth - checkWidth;
  const blockWidth = remaining / behaviorsCount;
  const dataWidth = blockWidth / 2;
  const descWidth = blockWidth / 2;

  // Calculate grid dimensions
  const gridTop = yStart;
  const totalRows = 32;
  const gridHeight = HEADER_ROW_HEIGHT + (totalRows * ROW_HEIGHT);
  const footerSpace = 16;

  const rows = timeRows(startHour);
  setStroke(doc);

  // Draw header row background
  doc.rect(MARGIN, gridTop, contentWidth, HEADER_ROW_HEIGHT).fill(HEADER_BG);
  setStroke(doc);
  doc.rect(MARGIN, gridTop, contentWidth, HEADER_ROW_HEIGHT).stroke();

  // Draw header text (vertically centered in taller header)
  const headerTextY = gridTop + (HEADER_ROW_HEIGHT - FONT_SIZE_LABEL) / 2;
  doc.fontSize(FONT_SIZE_LABEL).font("Helvetica-Bold").fillColor("#333333");
  doc.text("Time", MARGIN + 2, headerTextY, { width: timeWidth - 4, align: "center", lineBreak: false });

  // Checkmark symbol
  doc.font("ZapfDingbats").fontSize(9).fillColor("#333333");
  doc.text("4", MARGIN + timeWidth + 1, headerTextY, { width: checkWidth - 2, align: "center", lineBreak: false });

  // Behavior headers (allow wrapping for long titles)
  doc.font("Helvetica-Bold").fontSize(FONT_SIZE_DESC_TITLE).fillColor("#333333");
  for (let i = 0; i < behaviorsCount; i++) {
    const bx = MARGIN + timeWidth + checkWidth + i * blockWidth;
    doc.text(`${i + 1}. ${behaviors[i].title}`, bx + 2, gridTop + 3, {
      width: dataWidth - 4,
      height: HEADER_ROW_HEIGHT - 4,
      align: "center",
      lineBreak: true
    });
  }

  // Draw vertical lines for columns
  setStroke(doc);
  let x = MARGIN + timeWidth;
  doc.moveTo(x, gridTop).lineTo(x, gridTop + gridHeight).stroke();
  x += checkWidth;
  doc.moveTo(x, gridTop).lineTo(x, gridTop + gridHeight).stroke();

  for (let i = 0; i < behaviorsCount; i++) {
    const dataStart = MARGIN + timeWidth + checkWidth + i * blockWidth;
    doc.moveTo(dataStart, gridTop).lineTo(dataStart, gridTop + gridHeight).stroke();
    // Don't draw description column vertical lines here - they're drawn after the gray background
  }

  // Draw outer border
  setStroke(doc);
  doc.rect(MARGIN, gridTop, contentWidth, gridHeight).stroke();

  // Draw horizontal row lines and time labels
  doc.fontSize(FONT_SIZE_TIME).font("Helvetica").fillColor("#222222");
  for (let i = 0; i < totalRows; i++) {
    const y = gridTop + HEADER_ROW_HEIGHT + i * ROW_HEIGHT;
    const yLine = y + ROW_HEIGHT;

    // Horizontal lines only under time and check columns, and data columns (not desc)
    setStroke(doc);
    doc.moveTo(MARGIN, yLine).lineTo(MARGIN + timeWidth + checkWidth, yLine).stroke();
    for (let b = 0; b < behaviorsCount; b++) {
      const dataStart = MARGIN + timeWidth + checkWidth + b * blockWidth;
      doc.moveTo(dataStart, yLine).lineTo(dataStart + dataWidth, yLine).stroke();
    }

    // Time label - vertically centered in row
    const textY = y + (ROW_HEIGHT - FONT_SIZE_TIME) / 2;
    doc.text(rows[i], MARGIN + 2, textY, {
      width: timeWidth - 4,
      align: "left",
      lineBreak: false
    });
  }

  // Draw description column backgrounds (gray) - AFTER grid lines to cover any bleed
  for (let i = 0; i < behaviorsCount; i++) {
    const descX = MARGIN + timeWidth + checkWidth + i * blockWidth + dataWidth;
    // Draw slightly wider to cover the left border line
    doc.rect(descX + 0.5, gridTop + HEADER_ROW_HEIGHT, descWidth - 1, gridHeight - HEADER_ROW_HEIGHT).fill(LIGHT_BG);
  }

  // Redraw vertical lines for description columns (on top of gray background)
  setStroke(doc);
  for (let i = 0; i < behaviorsCount; i++) {
    const descX = MARGIN + timeWidth + checkWidth + i * blockWidth + dataWidth;
    doc.moveTo(descX, gridTop).lineTo(descX, gridTop + gridHeight).stroke();
    if (i === behaviorsCount - 1) {
      doc.moveTo(descX + descWidth, gridTop).lineTo(descX + descWidth, gridTop + gridHeight).stroke();
    }
  }

  // Draw description text in gray columns (centered, smaller font for long titles)
  for (let i = 0; i < behaviorsCount; i++) {
    const descColX = MARGIN + timeWidth + checkWidth + i * blockWidth + dataWidth;
    const descColY = gridTop + HEADER_ROW_HEIGHT;
    const descX = descColX + 3;
    const descY = descColY + 4;

    // Use smaller font (6pt) for description column title to prevent overflow
    doc.font("Helvetica-Bold").fontSize(6).fillColor("#222222");
    doc.text(behaviors[i].title, descX, descY, {
      width: descWidth - 6,
      align: "center",
      lineBreak: true
    });

    doc.font("Helvetica").fontSize(FONT_SIZE_DESC_TEXT).fillColor("#333333");
    const defY = descY + 18;  // Fixed offset after title
    doc.text(behaviors[i].description || "", descX, defY, {
      width: descWidth - 6,
      align: "center",
      lineBreak: true
    });
  }

  // Footer note
  const footerY = gridTop + gridHeight + 3;
  doc.font("Helvetica-Bold").fontSize(FONT_SIZE_FOOTER).fillColor("#000000");
  doc.text("Please look at last page for instructions.", MARGIN, footerY, {
    width: contentWidth,
    align: "center",
    lineBreak: false
  });
}

function drawNotesPage(doc, data, behaviors) {
  const contentWidth = PAGE_WIDTH - 2 * MARGIN;
  let y = MARGIN;

  y = drawHeader(doc, data, y, contentWidth);
  y = drawBehaviorList(doc, behaviors, y);

  // Notes grid
  const notesTop = y + 2;
  const headerRowHeight = 28;
  const dataRowHeight = 100;
  const notesGridHeight = headerRowHeight + (3 * dataRowHeight);
  const colWidths = [contentWidth * 0.2, contentWidth * 0.2, contentWidth * 0.6];

  setStroke(doc);

  // Header row background
  doc.rect(MARGIN, notesTop, contentWidth, headerRowHeight).fill(LIGHT_BG);
  setStroke(doc);
  doc.rect(MARGIN, notesTop, contentWidth, headerRowHeight).stroke();

  // Header labels
  doc.font("Helvetica-Bold").fontSize(FONT_SIZE_LABEL).fillColor("#000000");
  let x = MARGIN;
  ["Shift", "Observer (First/Last)", "Notes"].forEach((label, idx) => {
    doc.text(label, x + 6, notesTop + 9, { width: colWidths[idx] - 12, align: "left", lineBreak: false });
    x += colWidths[idx];
  });

  // Vertical column lines
  setStroke(doc);
  x = MARGIN + colWidths[0];
  doc.moveTo(x, notesTop).lineTo(x, notesTop + notesGridHeight).stroke();
  x += colWidths[1];
  doc.moveTo(x, notesTop).lineTo(x, notesTop + notesGridHeight).stroke();

  // Data rows
  const labels = ["Day", "Evening", "Night"];
  for (let i = 0; i < 3; i++) {
    const rowY = notesTop + headerRowHeight + i * dataRowHeight;
    setStroke(doc);
    doc.moveTo(MARGIN, rowY).lineTo(MARGIN + contentWidth, rowY).stroke();
    doc.font("Helvetica-Bold").fontSize(FONT_SIZE_LABEL).fillColor("#000000");
    doc.text(labels[i], MARGIN + 6, rowY + 8, { width: colWidths[0] - 12, align: "left", lineBreak: false });
  }

  // Outer border for notes grid
  setStroke(doc);
  doc.rect(MARGIN, notesTop, contentWidth, notesGridHeight).stroke();

  // Instructions section
  const instructionsTop = notesTop + notesGridHeight + 8;
  const instructionsHeight = 140;  // Increased for larger image

  setStroke(doc);
  doc.rect(MARGIN, instructionsTop, contentWidth, instructionsHeight).stroke();

  doc.font("Helvetica-Bold").fontSize(FONT_SIZE_LABEL).fillColor("#000000");
  doc.text("DATA MUST BE COLLECTED HOURLY", MARGIN, instructionsTop + 6, {
    width: contentWidth,
    align: "center",
    lineBreak: false
  });

  doc.font("Helvetica").fontSize(FONT_SIZE_TIME);
  doc.text(
    "Data taken later is often incorrect. Please take data as soon as you are able. " +
    "If you are unable to collect data within the hour, please \"X\" out the time slots (as if you were not with the patient).",
    MARGIN + 10,
    instructionsTop + 18,
    { width: contentWidth - 20, align: "center" }
  );

  // Instructions image (larger)
  const imgPath = path.join(__dirname, "scatterplot_bottom.png");
  if (fs.existsSync(imgPath)) {
    const imgY = instructionsTop + 42;
    const imgHeight = instructionsHeight - 50;
    doc.image(imgPath, MARGIN + 40, imgY, { height: imgHeight, fit: [contentWidth - 80, imgHeight] });
  }
}

async function generatePDF(data, outputPath) {
  return new Promise((resolve, reject) => {
    const behaviors = (data.behaviors || []).slice(0, 4);
    if (behaviors.length === 0) {
      behaviors.push({ title: "Behavior", description: "" });
    }

    const doc = new PDFDocument({
      size: [PAGE_WIDTH, PAGE_HEIGHT],
      margin: MARGIN,
      bufferPages: true
    });
    const stream = fs.createWriteStream(outputPath);
    doc.pipe(stream);

    // Page 1: 7:00 AM - 2:59 PM
    const contentWidth = PAGE_WIDTH - 2 * MARGIN;
    let y = drawHeader(doc, data, MARGIN, contentWidth);
    y = drawBehaviorList(doc, behaviors, y);
    drawGrid(doc, behaviors, 7, y);

    // Page 2: 3:00 PM - 10:59 PM
    doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
    y = drawHeader(doc, data, MARGIN, contentWidth);
    y = drawBehaviorList(doc, behaviors, y);
    drawGrid(doc, behaviors, 15, y);

    // Page 3: 11:00 PM - 6:59 AM
    doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
    y = drawHeader(doc, data, MARGIN, contentWidth);
    y = drawBehaviorList(doc, behaviors, y);
    drawGrid(doc, behaviors, 23, y);

    // Page 4: Notes
    doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
    drawNotesPage(doc, data, behaviors);

    doc.end();
    stream.on("finish", resolve);
    stream.on("error", reject);
  });
}

// Generate a combined PDF with multiple patients (for batch printing)
async function generateCombinedPDF(patientsData, outputPath) {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: [PAGE_WIDTH, PAGE_HEIGHT],
      margin: MARGIN,
      bufferPages: true
    });
    const stream = fs.createWriteStream(outputPath);
    doc.pipe(stream);

    const contentWidth = PAGE_WIDTH - 2 * MARGIN;
    let isFirstPatient = true;

    for (const data of patientsData) {
      const behaviors = (data.behaviors || []).slice(0, 4);
      if (behaviors.length === 0) {
        behaviors.push({ title: "Behavior", description: "" });
      }

      // Add page break before each patient (except the first)
      if (!isFirstPatient) {
        doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
      }
      isFirstPatient = false;

      // Page 1: 7:00 AM - 2:59 PM
      let y = drawHeader(doc, data, MARGIN, contentWidth);
      y = drawBehaviorList(doc, behaviors, y);
      drawGrid(doc, behaviors, 7, y);

      // Page 2: 3:00 PM - 10:59 PM
      doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
      y = drawHeader(doc, data, MARGIN, contentWidth);
      y = drawBehaviorList(doc, behaviors, y);
      drawGrid(doc, behaviors, 15, y);

      // Page 3: 11:00 PM - 6:59 AM
      doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
      y = drawHeader(doc, data, MARGIN, contentWidth);
      y = drawBehaviorList(doc, behaviors, y);
      drawGrid(doc, behaviors, 23, y);

      // Page 4: Notes
      doc.addPage({ size: [PAGE_WIDTH, PAGE_HEIGHT], margin: MARGIN });
      drawNotesPage(doc, data, behaviors);
    }

    doc.end();
    stream.on("finish", resolve);
    stream.on("error", reject);
  });
}

module.exports = { generatePDF, generateCombinedPDF };

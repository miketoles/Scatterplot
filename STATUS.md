# STATUS.md - ScatterplotCreator

---

**Project:** NRT Scatterplot Creator
**Last worked on:** January 26, 2026
**GitHub:** https://github.com/miketoles/Scatterplot

---

## Current Status

**Overall:** In stakeholder review - gathering feedback

---

## What I Just Did

- [x] Fixed grey backgrounds not printing (printer was skipping light colors, darkened from #f2f2f2 to #e0e0e0)
- [x] Fixed Print All PDF sorting (now sorts by patient ID alphabetically)
- [x] Increased font sizes for better print readability:
  - Behavior headers: 12px
  - Description text: 12px
  - Directions line: 11px
  - Instructions section (page 4): 12px
- [x] Removed "Behaviors for data collection" line from output
- [x] Pushed to GitHub repository

---

## What's Next

- [ ] Continue gathering stakeholder feedback **START HERE**
- [ ] Address any additional feedback
- [ ] Deploy to additional workstations if approved

---

## Blockers / Questions

- None - actively collecting feedback from stakeholders

---

## Notes for Next Session

Recent stakeholder feedback addressed:
- Font sizes increased for better readability on printed output
- Grey backgrounds now print correctly (Xerox printers were skipping very light greys)
- Print All output now properly sorted by patient ID

Deployment options:
- NSIS installer: `dist/NRT Scatterplot Creator Setup 1.0.0.exe`
- Portable ZIP: `dist/NRT Scatterplot Creator-Portable-1.0.0.zip`
- Unpacked: `dist/win-unpacked/`

---

## Context Dump

This is a real production app being deployed to a hospital behavioral health unit. BCBAs use it to create standardized scatterplot documents for patient behavior tracking.

Key deployment notes:
- App must run from local install (not network share) due to Chromium GPU process issues
- Data files can live on network share for multi-user access
- Default paths point to hospital L: drive
- NSIS installer recommended for easy deployment

---

*Last updated: January 26, 2026*

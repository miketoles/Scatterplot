# 🧪 Test Mode Guide - Scatterplot Printer

## What is Test Mode?

Test Mode allows you to **safely test the printing workflow WITHOUT modifying any actual files**. 

When Test Mode is enabled:
- ✅ The app opens Excel files
- ✅ Updates the date in memory (you'll see it on the printout)
- ✅ Sends the file to the printer
- ❌ **DOES NOT SAVE** the Excel file
- ❌ Original files remain completely unchanged

---

## 🎯 Why Use Test Mode?

### Perfect For:
- **First-time testing** - Make sure everything works before going live
- **Training new staff** - Let them practice without risk
- **Verifying printer settings** - Test duplex printing, margins, etc.
- **Checking file locations** - Make sure the app finds the right files
- **Testing date formatting** - Verify the date appears correctly

### Safety Benefits:
- 🛡️ **Zero risk** of overwriting production files
- 🛡️ **No accidental changes** to network files
- 🛡️ **Safe experimentation** with settings
- 🛡️ **Reversible testing** - nothing is permanent

---

## 📋 How to Enable Test Mode

### Step 1: Open Settings Tab
Click the "⚙️ Settings" tab at the top

### Step 2: Find Test Mode Section
Scroll to the "🧪 Test Mode" section

### Step 3: Enable Test Mode
Check the box: ☑️ "Enable Test Mode"

### Step 4: Save Settings
Click "💾 Save Settings" at the bottom

### Step 5: Verify
Go back to the Print tab - you should see a yellow banner:
```
🧪 TEST MODE ACTIVE - Files will NOT be saved
```

---

## 🖨️ Using Test Mode

### When Printing with Test Mode ON:

1. **Select patients and date** (same as normal)
2. **Click "Print Selected"**
3. **Confirmation dialog** will show:
   ```
   🧪 TEST MODE ENABLED
   
   Print 3 scatterplot(s) for 01/02/2025?
   
   ⚠️ Files will be opened and printed but NOT SAVED.
   The original files will remain unchanged.
   
   This is safe for testing.
   ```

4. **Click "Yes"** to proceed
5. **Watch the progress** - same as normal printing
6. **Completion message** will show:
   ```
   🧪 TEST MODE: Successfully printed 3 of 3 scatterplots
   
   ⚠️ NO FILES WERE SAVED - Original files are unchanged
   ```

### What Happens:
1. ✅ App finds each patient's scatterplot file
2. ✅ Opens the Excel file
3. ✅ Updates the date cell (A1 or configured cell) **in memory only**
4. ✅ Sends to printer with updated date
5. ✅ Closes Excel file **WITHOUT saving**
6. ✅ Original file is exactly as it was before

---

## 🔄 Switching to Live Mode

### When You're Ready to Go Live:

1. **Go to Settings tab**
2. **Uncheck Test Mode**: ☐ "Enable Test Mode"
3. **Click "Save Settings"**
4. **Go to Print tab** - the yellow banner should be gone
5. **Print normally** - files will now be saved

### Live Mode Confirmation:
When Test Mode is OFF, the confirmation dialog will say:
```
Print 3 scatterplot(s) for 01/02/2025?

✅ Files WILL BE SAVED with the updated date.

Proceed?
```

This reminds you that files will actually be modified.

---

## 🧪 Testing Workflow Example

### Day 1: Initial Testing
```
Settings → ☑️ Enable Test Mode → Save
Print Tab → Select 1-2 patients → Print
Check printouts:
  - Is date correct?
  - Is duplex working?
  - Does it look right?
Go back to network folder:
  - Verify files are unchanged ✅
```

### Day 2: Full Team Test
```
Test Mode still ON
Print Tab → Select all patients → Print
Team reviews printouts
Confirm everything looks good
Files still unchanged ✅
```

### Day 3: Go Live
```
Settings → ☐ Disable Test Mode → Save
Print Tab → Now files WILL be saved
Use for real daily workflow
```

---

## 📊 Test Mode vs Live Mode Comparison

| Action | Test Mode 🧪 | Live Mode ✅ |
|--------|-------------|-------------|
| Open Excel file | Yes | Yes |
| Update date in memory | Yes | Yes |
| Print file | Yes | Yes |
| **Save Excel file** | **NO** | **YES** |
| Modify network file | **NO** | **YES** |
| Original file changed | **NO** | **YES** |
| Safe for testing | **YES** | **NO** |
| Safe for production | **NO** | **YES** |

---

## ⚠️ Important Notes

### Test Mode Limitations:

1. **Printout shows updated date**
   - Even though file isn't saved, the printout will show the new date
   - This is correct - you're testing that the date displays properly

2. **If you manually open the file after printing**
   - You'll see the OLD date (because it wasn't saved)
   - This is expected behavior

3. **Test Mode is saved**
   - The setting persists between app restarts
   - Always check if Test Mode is ON before daily use
   - Look for the yellow banner on Print tab

### Best Practices:

✅ **Enable Test Mode** for all initial testing  
✅ **Keep it ON** during training period  
✅ **Test with real files** (since nothing is saved, it's safe)  
✅ **Disable it** only when ready for production  
✅ **Double-check** the banner before printing  

---

## 🐛 Troubleshooting

### "I enabled Test Mode but don't see the yellow banner"
- Make sure you clicked "Save Settings"
- Close and reopen the app
- Check Settings tab - is the checkbox still checked?

### "I printed in Test Mode but the file was still changed"
- Make sure Test Mode checkbox was checked
- Make sure you clicked "Save Settings"
- Check the completion message - does it say "TEST MODE"?
- If files are still changing, there may be a bug - contact support

### "I forgot to disable Test Mode and printed for real"
- No problem! The files weren't modified
- Just go print again with Test Mode OFF

### "Can I have Test Mode on for some users but not others?"
- No, Test Mode is saved in the config file on each computer
- Each computer has its own setting
- Some computers can have Test Mode ON, others OFF

---

## 💡 Pro Tips

1. **Keep Test Mode ON for training computers**
   - Have dedicated training machines
   - New staff can practice safely

2. **Test before major changes**
   - Changing printers? Turn on Test Mode
   - New network path? Turn on Test Mode
   - Updated Excel templates? Turn on Test Mode

3. **Verify after updates**
   - If you update the app, test with Test Mode first
   - Make sure everything still works

4. **Color-code computers**
   - Green sticker = Live Mode (saves files)
   - Yellow sticker = Test Mode (safe testing)

---

## 🎓 Training Script

Use this when training new staff:

```
"First, we're going to practice in TEST MODE.

This means you can click anything, print anything, 
and you won't break anything. The real files are 
completely safe.

See this yellow banner? That means Test Mode is ON.

Let's select a few patients and print them.
[Demo the process]

Now, let's check the network folder.
See? The files haven't changed at all.

When you're comfortable and ready to do this for real,
we'll turn OFF Test Mode. Then the files will actually
be saved with the new dates.

But for now, practice as much as you want!"
```

---

## 📈 Recommended Timeline

### Week 1: Full Test Mode
- All computers in Test Mode
- Everyone practices
- Work out any issues
- No real files modified

### Week 2: Partial Live
- Production computer goes Live
- Training computers stay in Test Mode
- Monitor for issues

### Week 3: Full Live
- All production computers go Live
- Keep 1 training computer in Test Mode
- Normal daily operations

---

**Test Mode gives you confidence to experiment safely!** 🧪✨

Turn it ON for testing, turn it OFF for production.
Simple, safe, effective.

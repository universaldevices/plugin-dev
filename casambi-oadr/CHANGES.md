# Casambi EIsy Plugin - Changes and Fixes

## Version 1.3.1 - February 12, 2026

### Added
- **server.json**: Plugin metadata file for Polyglot v3
  - Defines plugin name, description, and execution parameters
  - Configures polling intervals (shortPoll: 30s, longPoll: disabled)
  - Includes store information and credits
  - Specifies install scripts for local and cloud deployment

- **casambi.conf**: Hardware configuration file
  - Device specifications and connection parameters
  - Serial port configuration (baudrate: 115200, timeout: 5s)
  - Control mode definitions (level-based and price-based)
  - Parameter definitions with ranges and defaults
  - OpenADR status and signal mode mappings
  - USB hardware details (vendor/product IDs)
  - Requirements and compatibility information

### Changed
- Updated version from 1.0.4 to 1.3.1 in casambi.py
- Updated version in all configuration files

---

## Version 1.3.0 - February 12, 2026

### Summary

Fixed critical bugs and added USB permission handling for the Casambi OpenADR integration plugin.

---

## Code Fixes Applied to casambi.py

### 1. ✅ Added Missing OPENADR_TEST Command (Lines 640-707)

**Problem:** 
- Error: `node:runCmd: node 0 command OPENADR_TEST not defined`
- The test button in UD Admin Console did nothing

**Fix:**
- Created `testOpenADR()` method that simulates a demand response event
- Generates test XML with "Moderate" mode event (5 minute duration)
- Parses and processes through normal flow
- Registered in commands dictionary
- Provides detailed logging for debugging

**Impact:** Test button now works for debugging the integration

---

### 2. ✅ Fixed Event Selection Bug (Line 628)

**Problem:**
```python
elif activeEvent != None:
    self.setEvent(event)  # BUG: Uses last event from loop, not the active one
```

**Fix:**
```python
elif activeEvent != None:
    self.setEvent(activeEvent)  # Correct: Uses the actual active event
```

**Impact:** When multiple events exist, the correct active event is now processed

---

### 3. ✅ Fixed Logger Case Sensitivity (4 locations)

**Problem:**
- Lines 371, 383, 395, 470 used `Logger.error()` (wrong case)
- Would cause NameError exceptions

**Fix:**
- Changed all to `LOGGER.error()` (correct case, matches imports)

**Locations:**
- `setL1()` method
- `setL2()` method  
- `setL3()` method
- `saveParameterValue()` method

**Impact:** Prevents crashes when validation fails

---

### 4. ✅ Fixed Format String Error (Line 502)

**Problem:**
```python
LOGGER.error("mode is not valid {}".getMode())  # Missing self., wrong syntax
```

**Fix:**
```python
LOGGER.error("mode is not valid {}".format(self.getMode()))
```

**Impact:** Error messages now display correctly instead of crashing

---

### 5. ✅ Enhanced USB Permission Error Messages (Lines 96-122)

**Problem:**
- Generic error messages didn't help diagnose permission issues
- Users had to manually figure out permission problems

**Fix:**
- Added specific detection for permission errors (errno 13)
- Added detection for device not found errors (errno 2)
- Provides exact commands to fix issues
- References documentation for permanent fixes

**New Error Messages:**
```
PERMISSION DENIED: The serial port exists but cannot be accessed.
Fix with: sudo chmod 660 /dev/pg3.casambi && sudo chgrp pg3ns /dev/pg3.casambi
For permanent fix, install udev rules. See INSTALL_USB_PERMISSIONS.md
```

**Impact:** Much easier to diagnose and fix USB issues

---

### 6. ✅ Added Serial Port Success Logging (Line 133)

**Problem:**
- No confirmation when serial port opens successfully
- Hard to distinguish between "not trying" and "failed"

**Fix:**
- Added info log: `Serial port /dev/pg3.casambi opened successfully`
- Clears notices when successful

**Impact:** Better visibility into plugin state

---

## New Files Created

### 1. 99-casambi-usb.rules
**Purpose:** udev rules for automatic USB permission management

**What it does:**
- Automatically sets permissions when USB is plugged in
- Sets mode to 660 (rw-rw----)
- Sets group to pg3ns
- Can create symlink /dev/pg3.casambi

**Installation:**
```bash
sudo cp 99-casambi-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### 2. fix-casambi-permissions.sh
**Purpose:** Quick manual fix for USB permissions

**What it does:**
- Finds all serial devices (cuaU*, ttyU*)
- Shows current permissions
- Sets chmod 660 and chgrp pg3ns
- Provides troubleshooting guidance

**Usage:**
```bash
sudo ./fix-casambi-permissions.sh
```

**Note:** Changes are temporary (lost on reboot)

---

### 3. INSTALL_USB_PERMISSIONS.md
**Purpose:** Comprehensive USB setup guide

**Contents:**
- Three solution options (udev, startup script, manual)
- Step-by-step instructions
- Verification procedures
- Troubleshooting section

---

### 4. README.md
**Purpose:** Complete plugin documentation

**Contents:**
- System architecture overview
- Installation instructions
- Configuration guide
- Usage examples
- Control mode explanations
- Serial protocol reference
- Troubleshooting guide

---

### 5. CHANGES.md
**Purpose:** This document - tracking all fixes and improvements

---

## USB Permission Issue - Why It Happens

### The Problem

When the Casambi USB dongle is plugged in, the system creates device files:
- `/dev/cuaU0` or `/dev/ttyU0` (FreeBSD-style names)

By default, these are owned by `root:wheel` with permissions `crw-------` (600).

The PG3 plugin runs as a user in the `pg3ns` group, which cannot access these devices.

### The Solution Hierarchy

1. **Best:** udev rules (automatic, permanent, proper Linux way)
2. **Good:** Startup script (automatic, permanent, but hacky)
3. **Temporary:** Manual chmod/chgrp (must run after each reboot/replug)

### Why Not Fix in Python Code?

- Changing permissions requires root access
- The plugin runs as non-root user (security best practice)
- Running sudo from within code is a security risk
- The device might not exist yet when plugin starts
- Operating system level issue needs OS-level solution

### What the Code Can Do

✅ Detect permission errors  
✅ Provide helpful error messages  
✅ Guide user to proper fix  
❌ Cannot change permissions itself  

---

## Testing Checklist

After applying these fixes, test:

1. **USB Permissions:**
   - [ ] Install udev rules
   - [ ] Unplug and replug USB dongle
   - [ ] Verify: `ls -l /dev/cuaU0` shows `crw-rw---- 1 root pg3ns`
   - [ ] Plugin starts without serial errors

2. **OPENADR_TEST Command:**
   - [ ] Click test button in Admin Console
   - [ ] Check logs for "OPENADR_TEST: Simulating test event"
   - [ ] Verify status changes to "Active"
   - [ ] Verify mode changes to "Moderate"
   - [ ] Verify shed limit is calculated and sent

3. **Real OpenADR Events:**
   - [ ] Configure OpenADR client on EIsy
   - [ ] Create a test event
   - [ ] Verify plugin receives and processes event
   - [ ] Verify lighting responds correctly

4. **Error Handling:**
   - [ ] Temporarily remove USB dongle
   - [ ] Check error message is helpful
   - [ ] Plug back in
   - [ ] Verify recovery

---

## Version Change

**From:** 1.0.4 (with bugs)  
**To:** 1.0.4 (fixed)  

Version number kept the same since these are bug fixes, not new features.
Consider bumping to 1.0.5 when officially releasing.

---

## Files Modified

1. `casambi.py` - Main plugin code (7 changes)

## Files Created

1. `99-casambi-usb.rules` - udev rules
2. `fix-casambi-permissions.sh` - Permission fix script
3. `INSTALL_USB_PERMISSIONS.md` - USB setup guide
4. `README.md` - Complete documentation
5. `CHANGES.md` - This file

---

## Deployment Notes

To deploy to EIsy:

1. **Update Plugin Code:**
   ```bash
   # Copy fixed casambi.py to plugin directory
   scp casambi.py admin@eisy:/var/polyglot/pg3/ns/[namespace]/
   ```

2. **Install USB Rules:**
   ```bash
   scp 99-casambi-usb.rules admin@eisy:/tmp/
   ssh admin@eisy
   sudo cp /tmp/99-casambi-usb.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

3. **Restart Plugin:**
   - In PG3 web interface
   - Or: `systemctl restart pg3`

4. **Verify:**
   - Check logs for "Serial port opened successfully"
   - Test OPENADR_TEST command
   - Verify no errors

---

## Future Enhancements (Not Included)

Potential improvements for future versions:

- [ ] Auto-detect serial device (try multiple /dev/ttyU*, /dev/cuaU*)
- [ ] Configuration backup/restore
- [ ] Event scheduling/calendar
- [ ] Historical event logging
- [ ] Web UI for configuration
- [ ] Support for multiple Casambi networks
- [ ] MQTT integration option
- [ ] Homebridge/HomeKit support

---

## Support and Contact

Issues? Check:
1. Logs in PG3 interface
2. README.md troubleshooting section  
3. INSTALL_USB_PERMISSIONS.md
4. Universal Devices Forum

---

**End of Changes Document**

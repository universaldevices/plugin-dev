# Casambi USB Dongle - Permission Setup for EIsy

## Problem
The Casambi USB dongle creates serial device files (`/dev/cuaU0`, `/dev/ttyU0`) that by default are not accessible to the pg3 plugin system.

## Solution Options

### Option 1: udev Rules (Recommended - Permanent Solution)

This sets permissions automatically whenever the USB device is plugged in.

**Steps:**

1. **Find your USB device IDs** (optional but recommended for more specific rules):
   ```bash
   lsusb
   ```
   Look for your Casambi device and note the Vendor:Product IDs (e.g., `10c4:ea60`)

2. **Copy the udev rules file to the system:**
   ```bash
   sudo cp 99-casambi-usb.rules /etc/udev/rules.d/
   ```

3. **Reload udev rules:**
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

4. **Unplug and replug the Casambi USB dongle**

5. **Verify permissions:**
   ```bash
   ls -l /dev/cuaU0 /dev/ttyU0
   ```
   You should see: `crw-rw---- 1 root pg3ns ...`

### Option 2: Startup Script (Alternative)

If udev rules don't work on your system, create a startup script.

**Create `/usr/local/bin/fix-casambi-permissions.sh`:**
```bash
#!/bin/sh
# Fix Casambi USB permissions on boot

# Wait for device to appear
sleep 5

# Set permissions
if [ -e /dev/cuaU0 ]; then
    chmod 660 /dev/cuaU0
    chgrp pg3ns /dev/cuaU0
fi

if [ -e /dev/ttyU0 ]; then
    chmod 660 /dev/ttyU0
    chgrp pg3ns /dev/ttyU0
fi
```

**Make it executable and run at boot:**
```bash
sudo chmod +x /usr/local/bin/fix-casambi-permissions.sh
```

Then add to your system's startup (method depends on your EIsy system).

### Option 3: Manual Fix (Temporary - After Each Reboot)

If you need a quick fix:
```bash
sudo chmod 660 /dev/cuaU0 /dev/ttyU0
sudo chgrp pg3ns /dev/cuaU0 /dev/ttyU0
```

**Note:** This needs to be run after each reboot or USB replug.

## Verifying the Fix

After applying any solution, verify:

1. **Check device permissions:**
   ```bash
   ls -l /dev/cuaU0 /dev/ttyU0
   ```
   Should show: `crw-rw---- 1 root pg3ns`

2. **Check the symlink:**
   ```bash
   ls -l /dev/pg3.casambi
   ```
   Should point to one of the serial devices

3. **Test the plugin:**
   - Restart the Casambi plugin in PG3
   - Check the logs for serial port errors

## Troubleshooting

**Device names change after reboot:**
- Use udev rules with USB Vendor/Product IDs
- This creates a stable `/dev/pg3.casambi` symlink

**Permission denied errors:**
- Verify the pg3 process runs as a user in the `pg3ns` group:
  ```bash
  groups <pg3-user>
  ```

**Device not found:**
- Check if device appears:
  ```bash
  dmesg | grep -i tty
  ```
- May appear as different name (cuaU1, ttyU1, etc.)

# Casambi EIsy OpenADR Plugin

Polyglot v3 node server for communicating with Casambi USB dongle for demand response via OpenADR on Universal Devices EIsy controller.

## Overview

This plugin enables OpenADR (Open Automated Demand Response) integration with Casambi lighting control systems via USB dongle on the EIsy platform. It allows the EIsy to control lighting levels based on demand response events and electricity pricing signals.

## Features

- **OpenADR Integration**: Receives demand response events from EIsy's OpenADR client
- **Mode-Based Control**: Supports Normal, Moderate, High, and Special modes
- **Price-Based Control**: Adjusts lighting based on electricity pricing thresholds
- **Serial Communication**: Controls Casambi network via UART over USB
- **Test Function**: Built-in `OPENADR_TEST` command for debugging

## System Architecture

```
EIsy OpenADR Client
    ↓ (REST API /rest/oadr)
Casambi Plugin (casambi.py)
    ↓ (Serial UART)
Casambi USB Dongle (/dev/pg3.casambi)
    ↓ (Wireless)
Casambi Lighting Network
```

## Files

- `casambi.py` - Main plugin code
- `oadr.py` - OpenADR XML parser classes
- `oadr.xml` - Sample OpenADR event XML
- `99-casambi-usb.rules` - udev rules for automatic USB permissions
- `fix-casambi-permissions.sh` - Script to manually fix USB permissions
- `INSTALL_USB_PERMISSIONS.md` - Detailed USB setup instructions

## Installation

### 1. Install Plugin Files

Copy the plugin files to your EIsy PG3 plugin directory.

### 2. Fix USB Permissions

The Casambi USB dongle requires proper permissions to be accessed by the plugin.

**Quick Fix (Temporary):**
```bash
sudo ./fix-casambi-permissions.sh
```

**Permanent Fix (Recommended):**
```bash
sudo cp 99-casambi-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug the USB dongle.

See `INSTALL_USB_PERMISSIONS.md` for detailed instructions.

### 3. Configure Serial Port

The default serial port is `/dev/pg3.casambi`. You can customize this in the plugin configuration if your device appears at a different location (e.g., `/dev/cuaU0`, `/dev/ttyU0`).

## Configuration

### Plugin Parameters

- **Serial Port**: Path to the Casambi USB device (default: `/dev/pg3.casambi`)

### Casambi Parameters

Configure these in the Casambi USB dongle:

- **Control Mode**: 
  - `0` = Level-based (uses mode)
  - `1` = Price-based (uses electricity price)

- **Level Thresholds** (0-255):
  - `L1` = Moderate mode dimming level
  - `L2` = High mode dimming level
  - `L3` = Special mode dimming level

- **Price Thresholds** ($/kWh):
  - `P1` = Price threshold for L1 dimming
  - `P2` = Price threshold for L2 dimming
  - `P3` = Price threshold for L3 dimming

## Usage

### Testing the Integration

Use the `OPENADR_TEST` command in the UD Admin Console to simulate a demand response event:

1. Open the UD Admin Console
2. Navigate to the Casambi node
3. Click "OPENADR_TEST"

This will simulate a "Moderate" mode demand response event for 5 minutes.

### Normal Operation

The plugin automatically:
1. Polls the EIsy OpenADR endpoint (`/rest/oadr`) every short poll interval
2. Retrieves active or pending demand response events
3. Parses the event signals (mode and/or price)
4. Calculates the appropriate shed limit based on configuration
5. Sends commands to the Casambi dongle via serial
6. Updates the lighting network

## Control Modes

### Mode-Based Control (Control Mode = 0)

The shed limit is set based on the OpenADR mode signal:

| Mode | Shed Limit |
|------|------------|
| Normal | 0 (no dimming) |
| Moderate | L1 |
| High | L2 |
| Special | L3 |

### Price-Based Control (Control Mode = 1)

The shed limit is set based on electricity price thresholds:

| Price Range | Shed Limit |
|-------------|------------|
| < P1 | 0 (no dimming) |
| P1 ≤ price < P2 | L1 |
| P2 ≤ price < P3 | L2 |
| ≥ P3 | L3 |

## Serial Protocol

The plugin communicates with the Casambi dongle using custom opcodes:

| Opcode | Name | Description |
|--------|------|-------------|
| 0x01 | PING | Ping request |
| 0x02 | PONG | Pong response |
| 0x03 | INIT | Initialization |
| 0x05 | SET_CHANNEL_0 | Set channel 0 level |
| 0x18 | GET_SENSOR_VAL | Get sensor value |
| 0x19 | SET_SENSOR_VAL | Set sensor value |
| 0x1A | SET_PARAM | Set parameter |
| 0x1B | PARAM_COMP | Parameter complete |

## Troubleshooting

### Error: "Unable to open serial port"

**Permission denied:**
```bash
sudo chmod 660 /dev/cuaU0 /dev/ttyU0
sudo chgrp pg3ns /dev/cuaU0 /dev/ttyU0
```

Or install udev rules for permanent fix.

**Device not found:**
- Check USB connection: `lsusb`
- Find device name: `ls -l /dev/tty* /dev/cua*`
- Check kernel messages: `dmesg | grep -i tty`

### Error: "node:runCmd: node 0 command OPENADR_TEST not defined"

This error has been fixed in the updated version. Make sure you're using the latest `casambi.py` with the `OPENADR_TEST` command handler.

### No Response from Dongle

- Check serial port configuration in plugin settings
- Verify dongle is properly initialized: check logs for INIT opcode
- Ensure parameters are loaded: look for PARAM_COMP in logs

### Lighting Not Responding to Events

1. Verify OpenADR events are being received:
   - Check `/rest/oadr` endpoint on EIsy
   - Look for "Active" events in logs

2. Check control mode configuration matches event type:
   - Mode signals require Control Mode = 0
   - Price signals require Control Mode = 1

3. Verify thresholds are configured:
   - Check L1, L2, L3 values (should be 0-255)
   - Check P1, P2, P3 values ($/kWh)

4. Monitor shed limit updates in logs:
   - Look for "sendShedLevel" messages
   - Verify values are being sent to dongle

## Version History

- **1.0.4** - Current version
  - Added OPENADR_TEST command
  - Fixed event selection bug (activeEvent vs event)
  - Fixed Logger case sensitivity issues
  - Improved error messages and USB permission guidance
  - Fixed format string error in updateLoadShedLimit()

## Support

For issues and questions:
- Check the logs in PG3 for detailed error messages
- Review `INSTALL_USB_PERMISSIONS.md` for USB setup help
- Universal Devices Forum: https://forum.universal-devices.com/

## License

Copyright (C) 2023 Universal Devices

## Developer Resources

- [UD Developer Docs](https://developer.isy.io/docs/getstarted/dev_env)
- [OpenADR Specification](https://www.openadr.org/)
- [Casambi API Documentation](https://developer.casambi.com/)

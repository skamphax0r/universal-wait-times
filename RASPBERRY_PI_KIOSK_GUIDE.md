# Universal Parks Wait Times Smart Box - Raspberry Pi Kiosk Setup Guide

This guide walks through setting up a dedicated physical display box using a Raspberry Pi and any LCD screen (e.g., Raspberry Pi Touch Display, Waveshare HDMI screen, or standard small monitor) that automatically boots directly into full-screen Kiosk mode displaying your Universal Parks Wait Times web application.

---

## 1. Hardware Requirements

- **Raspberry Pi**: Raspberry Pi 3B+, 4, 5, or Pi Zero 2 W.
- **MicroSD Card**: 16 GB+ (Class 10 or A1/A2 recommended).
- **Display**: 
  - Official 7" Raspberry Pi Touchscreen (DSI cable), OR
  - 3.5" / 5" / 7" HDMI LCD (Waveshare, Elecrow, etc.), OR
  - Any standard HDMI miniature monitor.
- **Power Supply**: Official 5V USB-C (Pi 4/5) or Micro-USB (Pi 3/Zero 2).
- **Enclosure (Optional)**: 3D-printed theme box enclosure (Wizarding World, Stark HUD, or Mario Question Block).

---

## 2. Raspberry Pi OS Installation

1. Download and run the **Raspberry Pi Imager** on your computer:
   `https://www.raspberrypi.com/software/`
2. **Choose OS**:
   - Recommended: **Raspberry Pi OS (64-bit)** (Desktop recommended for easiest display driver support).
   - Alternatively: **Raspberry Pi OS Lite (64-bit)** if you want minimal RAM usage with `cage`.
3. **Edit OS Customization Settings** (Gear icon in Imager):
   - **Hostname**: `universalbox` (or `universal-clock`)
   - **Username & Password**: Set your username (e.g. `pi`) and a secure password.
   - **Wi-Fi**: Configure your local SSID and Wi-Fi password.
   - **Services**: Check **Enable SSH** (use password authentication or add your SSH key).
   - **Timezone**: Set to `America/Chicago` (CST) or your local timezone.
4. Flash the MicroSD card, insert it into the Pi, connect your display, and power on.

---

## 3. Option A: Raspberry Pi OS with Desktop (Recommended & Simplest)

Raspberry Pi OS Bookworm uses Wayland (Wayfire or Labwc) by default. Setting up Chromium Kiosk mode takes only a few minutes.

### Step 3.1: Update & Install Utilities
Open a terminal (or SSH into `pi@universalbox.local`):
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y unclutter x11-xserver-utils
```

### Step 3.2: Disable Screen Blanking (Sleep Mode)
Prevent the display from turning off or going black after inactivity:

1. Open Raspberry Pi Configuration:
   ```bash
   sudo raspi-config
   ```
2. Navigate to **Display Options** -> **Screen Blanking** -> Select **No** (Disable screen blanking).
3. Finish and reboot when prompted.

Alternatively, via command line:
```bash
sudo sed -i 's/$/ consoleblank=0/' /boot/firmware/cmdline.txt
```

### Step 3.3: Configure Kiosk Autostart Script

Create an autostart launch script:
```bash
mkdir -p ~/scripts
nano ~/scripts/kiosk.sh
```

Paste the following content:
```bash
#!/bin/bash
# Wait for network connection and DNS resolution
while ! ping -c 1 -W 1 universal.skamphax0r.local >/dev/null 2>&1; do
    echo "Waiting for network and universal.skamphax0r.local..."
    sleep 1
done

# Hide mouse cursor when inactive
unclutter -idle 0.5 -root &

# Disable screen blanking & power management
xset s noblank
xset s off
xset -dpms

# Prevent Chromium crash restore balloons
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/Default/Preferences 2>/dev/null
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences 2>/dev/null

# Launch Chromium in dedicated full-screen kiosk mode
/usr/bin/chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --check-for-update-interval=31536000 \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --no-first-run \
  --fast \
  --fast-start \
  --disable-features=Translate \
  --password-store=basic \
  http://universal.skamphax0r.local
```

Make the script executable:
```bash
chmod +x ~/scripts/kiosk.sh
```

### Step 3.4: Configure Desktop Autostart

For standard desktop autostart, create the desktop entry:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/kiosk.desktop
```

Paste:
```ini
[Desktop Entry]
Type=Application
Name=Universal Kiosk
Exec=/home/pi/scripts/kiosk.sh
X-GNOME-Autostart-enabled=true
```
*(Replace `/home/pi/` with your actual home directory username if different).*

If your Pi runs **Wayfire** (Bookworm default on Pi 4/5):
Edit `~/.config/wayfire.ini` and add under `[autostart]`:
```ini
[autostart]
kiosk = /home/pi/scripts/kiosk.sh
```

If your Pi runs **Labwc** (Pi 3 / Zero 2 on Bookworm):
Edit `~/.config/labwc/autostart` and add:
```bash
/home/pi/scripts/kiosk.sh &
```

---

## 4. Option B: Ultra-Fast Lightweight Kiosk (Raspberry Pi OS Lite with Cage)

If you installed Raspberry Pi OS Lite and want ultra-fast booting with zero desktop bloat:

### Step 4.1: Install Cage & Chromium
```bash
sudo apt update
sudo apt install -y cage chromium-browser fonts-dejavu-core fonts-freefont-ttf
```

### Step 4.2: Create Systemd Kiosk Service
```bash
sudo nano /etc/systemd/system/universal-kiosk.service
```

Paste:
```ini
[Unit]
Description=Universal Wait Times Wayland Kiosk
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=WLR_LIBINPUT_NO_DEVICES=1
ExecStartPre=/bin/sh -c 'while ! ping -c 1 -W 1 universal.skamphax0r.local >/dev/null 2>&1; do sleep 1; done'
ExecStart=/usr/bin/cage -s -- /usr/bin/chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 --disable-pinch --overscroll-history-navigation=0 --no-first-run http://universal.skamphax0r.local
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now universal-kiosk.service
```

---

## 5. Screen Orientation & Rotation (Portrait vs Landscape)

If your kiosk enclosure is oriented vertically or upside-down:

### On Pi 4 / 5 / Bookworm (Wayland):
Run:
```bash
wlr-randr
```
To see your output name (e.g. `HDMI-A-1` or `DSI-1`). Then rotate:
```bash
# 90 degrees (Portrait):
wlr-randr --output HDMI-A-1 --transform 90

# 180 degrees (Inverted):
wlr-randr --output HDMI-A-1 --transform 180

# 270 degrees:
wlr-randr --output HDMI-A-1 --transform 270
```
To make it permanent, add to `~/.config/wayfire.ini`:
```ini
[output:HDMI-A-1]
transform = 90
```

---

## 6. Scheduled Display Sleep (Auto On/Off Overnight)

To turn off the screen at night (e.g., 11:00 PM) and turn back on in the morning (e.g., 7:00 AM) to preserve display life:

Run `crontab -e`:
```cron
# Turn display off at 11:00 PM every night
0 23 * * * wlr-randr --output HDMI-A-1 --off 2>/dev/null || xset dpms force off

# Turn display back on at 7:00 AM every morning
0 7 * * * wlr-randr --output HDMI-A-1 --on 2>/dev/null || xset dpms force on
```

---

## 7. Useful Shortcut & Maintenance Commands

- **Exit Kiosk Mode / Access Terminal**:
  Press `Ctrl + Alt + F2` to open a TTY terminal, or `Alt + F4` / `Ctrl + W` if keyboard is connected.
- **Remote SSH Access**:
  Connect via terminal from another machine:
  ```bash
  ssh pi@universalbox.local
  ```
- **Force Refresh Kiosk Page**:
  From SSH, restart the service or send reload:
  ```bash
  pkill -HUP -f chromium
  ```

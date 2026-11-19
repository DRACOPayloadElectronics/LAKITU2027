# Raspberry Pi 5 Setup Guide

Setup for: **Raspberry Pi 5 (2GB)** · **Raspberry Pi OS (64-bit, Desktop)** booting from a **USB drive** · **Pi Camera Module**

The plan: develop and test on the Desktop version (easier for the team), then move to **Pi OS Lite (headless)** once everything works.

## 1. Hardware Checklist

| Item | Notes |
|---|---|
| Raspberry Pi 5 (2GB) | |
| Official 27W USB-C power supply (5V/5A) | Needed for full USB power to the boot drive |
| USB 3.0 drive (boot drive) | Plug into a **blue** USB 3 port |
| Pi Camera Module | Any official module (v2, v3, HQ, etc.) |
| **Pi 5 camera cable (22-pin to 15-pin)** | The Pi 5 has smaller camera connectors. The standard cable that comes with most cameras **does not fit**. |
| Separate 5–6V power supply for servos | **Never power servos from the Pi's 5V pin** |
| Micro HDMI → HDMI cable, monitor, keyboard, mouse | For desktop setup |
| (Recommended) Cooling (active cooler or case with fan) | Recommended; CV workloads heat the CPU |

---

## 2. Flash the OS

> Already done? Skip to [Section 3](#3-assemble-the-hardware). Keep this section for re-flashing or setting up a second Pi.

1. Download **Raspberry Pi Imager** from https://www.raspberrypi.com/software/
2. Plug the USB drive **directly** into your computer (not a hub).
3. On Windows: right-click Imager → **Run as administrator**.
4. In Imager:
   - **Device:** Raspberry Pi 5
   - **OS:** Raspberry Pi OS (64-bit) *(the Desktop version)*
   - **Storage:** your USB drive (double-check the size!)
5. When asked to apply **OS customisation**, choose **Edit settings** and set:
   - **Hostname:** e.g. `cvpi` (you'll connect with `cvpi.local`)
   - **Username / password:** pick something the whole team knows
   - **Wi-Fi:** network name, password, and **Wireless LAN country**
   - **Locale / timezone / keyboard layout**
   - **Services tab → Enable SSH** (password authentication)
6. Write and wait for **writing + verifying** to finish completely.

### Expected result (Windows Disk Management)
| Partition | Meaning |
|---|---|
| ~8 MB unallocated | Normal spacing |
| `bootfs` 512 MB FAT32 | Boot partition (the only one Windows can read) |
| ~5–6 GB partition | The Linux system (Windows can't read it) |
| Large unallocated space | Normal; Pi OS expands into it on first boot |

> ⚠️ If Windows pops up **"You need to format the disk"**, click **Cancel**. Formatting would erase the OS.

### If the write fails
- Try a different USB port (directly on the computer).
- Close all File Explorer windows.
- Temporarily turn off **Controlled folder access** (Windows Security → Virus & threat protection → Ransomware protection).
- If the drive disappears from File Explorer after a failed write, wipe it with `diskpart` (admin Command Prompt):
  ```
  diskpart
  list disk
  select disk X        <-- X = the USB drive. CHECK THE SIZE. Never select your main disk!
  clean
  create partition primary
  format fs=exfat quick
  assign
  exit
  ```
  Then try Imager again.

---

## 3. Assemble the Hardware

> ⚠️ Do all wiring with the Pi **powered off and unplugged**. Cameras are not hot-pluggable.

### 3.1 Camera
1. On the Pi 5, find the camera connector labelled **CAM/DISP 0** (use this one first; software defaults to camera 0).
2. Gently lift the black latch, insert the **narrow (22-pin) end** of the Pi 5 camera cable fully and straight, then press the latch down.
3. Connect the wide (15-pin) end to the camera module the same way.
4. If the camera isn't detected later, the cable is most likely reversed or not fully seated. Check the contact orientation against the [official camera docs](https://www.raspberrypi.com/documentation/accessories/camera.html).

### 3.2 Boot drive, display, and power
1. Plug the USB boot drive into a **blue USB 3 port**. Make sure **no microSD card** is inserted.
2. Connect the monitor to the **micro HDMI port next to the USB-C power port** (HDMI0).
3. Connect keyboard and mouse.
4. **Plug in power last.**

---

## 4. First Boot

- The first boot takes a few minutes and may **restart once** while it expands the filesystem. This is normal.
- You should land on the desktop (or a login screen; use the username/password from Imager).
- Confirm the drive expanded:
  ```bash
  df -h /
  ```
  Expected: roughly **110 GB** total for a 128 GB drive.

---

## 5. Update the System

Open a terminal (top-left menu → Accessories → Terminal):

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Update the bootloader firmware (improves USB boot and stability):

```bash
sudo rpi-eeprom-update -a
sudo reboot
```

---

## 6. Enable Interfaces (SSH, I2C, VNC)

```bash
sudo raspi-config
```

Go to **Interface Options** and enable:

| Interface | Why |
|---|---|
| **SSH** | Remote terminal access from laptops (likely already on from Imager) |
| **I2C** | Required for the PCA9685 servo driver |
| **VNC** | Lets teammates see and control the Pi desktop from their laptops (and screen-record it) |

Finish → reboot when asked.

Install I2C tools:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

> **Optional:** [Raspberry Pi Connect](https://www.raspberrypi.com/software/connect/) gives browser-based remote access to the desktop without configuring VNC clients. It's handy for a team.

---

## 7. Test the Camera

```bash
# List detected cameras
rpicam-hello --list-cameras

# 5-second live preview on the monitor
rpicam-hello -t 5000

# Take a still photo
rpicam-still -o test.jpg

# Record a 5-second video
rpicam-vid -t 5000 -o test.h264
```

If `--list-cameras` shows **"No cameras available"**:
1. Power off, re-seat the cable at both ends (check orientation), power on.
2. Make sure you're using the Pi 5 (22-pin) cable.
3. Run `sudo apt full-upgrade -y` and reboot.

> Note: old commands like `raspistill` and `libcamera-hello` are outdated. Use the `rpicam-*` commands.

---

## 8. Python Environment

### 8.1 Install system packages

Picamera2 and OpenCV are installed from **apt** (not pip). This avoids version conflicts. Picamera2 depends on the system NumPy, and pip-installed OpenCV can pull in an incompatible NumPy and break it.

```bash
sudo apt install -y python3-picamera2 python3-opencv python3-numpy python3-lgpio python3-venv git htop
```

*(Picamera2 is usually preinstalled on the Desktop version. This command just makes sure.)*

### 8.2 Create the project and virtual environment

The venv **must** use `--system-site-packages` so it can see Picamera2 and OpenCV from apt.

```bash
mkdir -p ~/cv-project
cd ~/cv-project
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

> Run `source ~/cv-project/.venv/bin/activate` every time you open a new terminal for the project. Your prompt will show `(.venv)`.

### 8.3 Install pip packages (inside the venv)

```bash
pip install -r requirements.txt
```

### 8.4 Record your setup (do this as you go!)

Create `requirements.txt`

**Every time someone installs something new, add it to `requirements.txt`.**
---

## 9. Team Workflow and Remote Development

### Connect from laptops
```bash
ssh <username>@cvpi.local
```
(If `.local` doesn't resolve, find the Pi's IP with `hostname -I` on the Pi and use that.)

### VS Code Remote-SSH (recommended)
1. Install **VS Code** + the **Remote - SSH** extension on your laptop.
2. `Ctrl+Shift+P` → **Remote-SSH: Connect to Host** → `<username>@cvpi.local`
3. Open the `~/cv-project` folder. You can now edit and run code on the Pi from your laptop.
4. Select the interpreter: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv/bin/python`

### Remote desktop (VNC)
- Use **RealVNC Viewer** (or Raspberry Pi Connect) on your laptop to see the Pi desktop, including OpenCV windows.
- Screen-record the VNC window on your laptop to capture demos.

### Version control with Git
Push to a shared GitHub repo so everyone works from the same code.

### Suggested project layout
```
code/
├── .venv/                # virtual environment (not in git)
├── setup.sh              # one-command rebuild
├── requirements.txt      # pip packages
├── config.py             # SHOW_WINDOW, frame size, servo limits, etc.
├── servo_test.py
├── camera_test.py
├── record_test.py
├── main.py               # the real tracking program
├── models/               # detection model files (if needed)
└── snapshots/            # saved detections (not in git, this is used for testing purposes, try to keep this folder lean)
```

---
### Run automatically on boot (systemd service)
Create `/etc/systemd/system/cvtracker.service`:
```ini
[Unit]
Description=Pan-tilt CV tracker
After=network.target

[Service]
User=<username>
WorkingDirectory=/home/<username>/cv-project
ExecStart=/home/<username>/cv-project/.venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cvtracker
journalctl -u cvtracker -f      # view live logs
```

---
## 10. Monitoring and Performance

| Command | Shows |
|---|---|
| `htop` | CPU and RAM usage (quit with `q`) |
| `free -h` | Memory summary |
| `vcgencmd measure_temp` | CPU temperature (keep under ~80 °C) |
| `vcgencmd get_throttled` | `throttled=0x0` = all good; anything else = power or heat problems |
| `df -h` | Disk space |

**Tips for the 2GB Pi:**
- **Avoid running Chromium on the Pi** during tests; it uses the most RAM. Look things up on your laptops.
- Keep frames small (**640×480** or less) for detection.
- Use lightweight models (e.g. MobileNet-SSD, YOLO "nano" variants, or classic OpenCV methods).
- If RAM usage stays under ~1.5 GB during a full test run, you're fine.

## 11. Final Checklist

- [ ] Pi boots to the desktop from the USB drive
- [ ] `df -h /` shows ~110 GB
- [ ] System updated (`apt full-upgrade`) and bootloader updated
- [ ] SSH, I2C, and VNC enabled
- [ ] `rpicam-hello --list-cameras` lists the camera
- [ ] `i2cdetect -y 1` shows `40`
- [ ] venv created with `--system-site-packages`; all imports OK
- [ ] Teammates can connect via SSH / VS Code Remote-SSH / VNC
- [ ] Code in a shared Git repo with `setup.sh` and `requirements.txt`
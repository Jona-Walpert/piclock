# 🤖 100% AI GENERATED CODEBASE 🤖

> # ⚠️ IMPORTANT NOTICE / WICHTIGER HINWEIS:
> **ALL CODE IN THIS REPOSITORY IS 100% ARTIFICIAL INTELLIGENCE GENERATED (GOOGLE ANTIGRAVITY). NO HUMAN CODE WAS WRITTEN MANUALLY.**
> 
> **DIESER GESAMTE CODE UND DIESES REPOSITORY WURDEN VOLLSTÄNDIG VON KÜNSTLICHER INTELLIGENZ (GOOGLE ANTIGRAVITY) GENERIERT. ES WURDE KEINE MANUELLE ZEILE CODE GESCHRIEBEN.**
> 
> **DISCLAIMER OF LIABILITY / HAFTUNGSAUSSCHLUSS ("AS IS"):**
> The software is provided "AS IS", without warranty of any kind. The author assumes no liability or responsibility for any damages, hardware failures, or malfunctions. Feel free to use, modify, and distribute it however you want under the [MIT License](LICENSE).
> 
> *Der Autor übernimmt keinerlei Haftung oder Gewährleistung für die Funktion, Sicherheit oder eventuelle Schäden ("AS IS"). Macht damit, was ihr wollt! (Siehe [MIT LICENSE](LICENSE)).*

---

<p align="center">
  <b>Language / Sprache:</b>
  <a href="#english"><b>English</b></a> | <a href="#deutsch"><b>Deutsch</b></a>
</p>

---

<a name="english"></a>
# PiClock - E-Paper Digital Clock for Raspberry Pi Zero 2 W

[![Architecture diagram](https://gitdiagram.com/diagram-badge.svg)](https://gitdiagram.com/jona-walpert/piclock?utm_source=readme&utm_medium=badge)

A modern, highly efficient E-Paper digital clock designed for Raspberry Pi Zero 2 W and Waveshare 2.13-inch E-Paper displays (V4, V3, V2).

## Key Features
* **Modern Typography:** Crisp, large-scale digital clock display (Roboto Bold) showing time (HH:MM), day of the week, and date.
* **Partial Refresh:** Fast, flicker-free minute updates without flashing the entire screen.
* **Anti-Ghosting Deep Clean:** Configurable black/white inversion cycles every 30 to 60 minutes to eliminate e-paper particle ghosting.
* **Precise Time Synchronization:** Background hourly synchronization with NTP time servers (`pool.ntp.org`) and `systemd-timesyncd`.
* **Midnight New-Day Celebration (`feature/midnight-new-day`):** Prominently displays the new day name across the entire screen from 00:00:00 to 00:00:29, then switches back to the regular clock at 00:00:30.
* **Power Optimization (`feature/power-saving`):** Software power-saving mode disabling HDMI circuitry and the onboard ACT LED, reducing current draw by over 60%.
* **Autostart & Reliability:** Runs as a standalone background `systemd` service (`piclock.service`) with automatic recovery and restart on boot.
* **Modular Driver Architecture:** Out-of-the-box support for Waveshare 2.13" V4, V3, and V2 panels, as well as a mock simulator driver for testing.

---

## Hardware Wiring & Pinout
Connect the Waveshare 2.13" E-Paper display module to the Raspberry Pi 40-pin GPIO header:

| E-Paper Pin | Raspberry Pi Pin | GPIO Header Pin | Function |
|---|---|---|---|
| **VCC** | 3.3V Power | **Pin 1** (or Pin 17) | 3.3V Power Supply |
| **GND** | Ground | **Pin 6** (or Pin 9, 14, 20) | Ground |
| **DIN** | MOSI | **Pin 19** (GPIO 10) | SPI Data In |
| **CLK** | SCLK | **Pin 23** (GPIO 11) | SPI Clock |
| **CS** | CE0 | **Pin 24** (GPIO 8) | Chip Select (Active Low) |
| **DC** | GPIO 25 | **Pin 22** (GPIO 25) | Data (High) / Command (Low) |
| **RST** | GPIO 17 | **Pin 11** (GPIO 17) | Hardware Reset |
| **BUSY**| GPIO 24 | **Pin 18** (GPIO 24) | Busy Signal Input |

---

## Installation & Setup Instructions

### Option A: One-Step Automated Setup (Recommended)
On your Raspberry Pi, clone the repository and run the automated installer:

```bash
git clone https://github.com/Jona-Walpert/piclock.git ~/piclock
cd ~/piclock
sudo ./install.sh
```
The installer automatically:
1. Enables the SPI hardware interface and loads kernel modules.
2. Installs required system packages (`python3-pil`, `python3-spidev`, `python3-rpi-lgpio`, fonts).
3. Adds the user to necessary hardware groups (`spi`, `gpio`).
4. Installs and enables the `piclock.service` systemd daemon.
5. Starts the clock immediately in the background.

---

### Option B: Manual Step-by-Step Installation

#### 1. Enable SPI Hardware Interface
Run `raspi-config`:
```bash
sudo raspi-config nonint do_spi 0
```
*Or manually ensure `dtparam=spi=on` is present in `/boot/firmware/config.txt` (or `/boot/config.txt`).*

#### 2. Install Required System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pil python3-spidev python3-rpi-lgpio fonts-dejavu-core
```

#### 3. Clone Repository
```bash
git clone https://github.com/Jona-Walpert/piclock.git ~/piclock
cd ~/piclock
```

#### 4. Run Hardware Self-Test
Verify that your display hardware and wiring work properly:
```bash
python3 test_clock.py
```
*(Use `python3 test_clock.py --mock` for simulation without hardware).*

#### 5. Configure Autostart (systemd)
```bash
sudo cp piclock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now piclock.service
```

---

## Systemd Service Management
```bash
# Check service status
sudo systemctl status piclock.service

# View live log output
journalctl -u piclock.service -f

# Restart or stop the service
sudo systemctl restart piclock.service
sudo systemctl stop piclock.service
```

---

## Configuration (`config.py`)
All parameters can be configured directly in `config.py` or overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `DISPLAY_DRIVER` | `epd2in13_V4` | Driver to use (`epd2in13_V4`, `epd2in13_V3`, `epd2in13_V2`, `mock`) |
| `DISPLAY_WIDTH` | `250` | Display width in pixels (Landscape) |
| `DISPLAY_HEIGHT` | `122` | Display height in pixels (Landscape) |
| `DISPLAY_ROTATION` | `0` | Rotation angle (`0` or `180` for upside-down landscape) |
| `FULL_REFRESH_INTERVAL_MINUTES` | `30` | Interval for full anti-ghosting refresh cycles (30-60 min) |
| `CLEANING_CYCLES` | `2` | Number of black/white inversion flashes before full refresh |
| `TIMEZONE` | `Europe/Berlin` | Clock timezone |
| `NTP_SYNC_INTERVAL_HOURS` | `1` | Interval for background NTP time checks |
| `ENABLE_POWER_SAVING` | `true` | Turns off HDMI and ACT LED to conserve power |

---

## Project Structure
```
piclock/
├── main.py                 # Main loop (minute ticks, event scheduling, signal handling)
├── display.py              # DisplayManager (layout engine, typography, refresh cycles)
├── time_sync.py            # Background NTP and systemd-timesyncd synchronizer
├── power.py                # Power management (HDMI off, LED off, CPU governor)
├── config.py               # Central configuration (intervals, fonts, timezones, rotation)
├── install.sh              # Automated 1-step installation script
├── piclock.service         # Systemd service unit for autostart
├── test_clock.py           # Automated hardware & component self-test script
├── LICENSE                 # MIT License (Zero liability, open usage)
├── README.md               # Documentation
├── drivers/
│   ├── base.py             # Abstract display driver interface
│   ├── driver_waveshare.py # Waveshare 2.13" adapter (V4, V3, V2)
│   ├── mock.py             # Mock display simulator driver
│   └── waveshare/          # Low-level Waveshare hardware drivers & epdconfig
└── fonts/                  # TrueType fonts (Roboto-Bold, Roboto-Regular)
```

---

<a name="deutsch"></a>
# PiClock - E-Paper Digitaluhr (Deutsche Dokumentation)

[![Architecture diagram](https://gitdiagram.com/diagram-badge.svg)](https://gitdiagram.com/jona-walpert/piclock?utm_source=readme&utm_medium=badge)

Eine moderne, energieeffiziente E-Paper-Digitaluhr für den Raspberry Pi Zero 2 W und Waveshare 2.13 Zoll E-Paper Displays (V4, V3, V2).

## Kernfunktionen
* **Moderne Typografie:** Großflächige, gestochen scharfe Anzeige (Roboto Bold) mit Uhrzeit (HH:MM), Wochentag und Datum.
* **Partial Refresh:** Sekundenschnelle Aktualisierung beim regulären Minutensprung ohne Bildschirmflackern.
* **Anti-Ghosting Deep Clean:** Konfigurierbare Schwarz/Weiß-Invertierungszyklen alle 30 bis 60 Minuten zur vollständigen Beseitigung von Ghosting-Artefakten.
* **Präzise Zeitsynchronisation:** Stündlicher Hintergrundabgleich mit NTP-Servern (`pool.ntp.org`) und `systemd-timesyncd`.
* **Neuer-Tag-Anzeige um Mitternacht (`feature/midnight-new-day`):** Zeigt von 00:00:00 bis 00:00:29 groß den neuen Wochentag an und schaltet um 00:00:30 wieder auf die reguläre Uhrzeit zurück.
* **Stromspar-Modus (`feature/power-saving`):** Deaktiviert HDMI und Status-LEDs (senkt den Stromverbrauch um über 60%).
* **Autostart & Zuverlässigkeit:** Autarker Hintergrundbetrieb via `systemd` (`piclock.service`) mit automatischem Neustart.

---

## Hardware-Verkabelung (Pinbelegung)
Verbinde das Waveshare 2.13" Display wie folgt mit der 40-Pin-GPIO-Leiste des Raspberry Pi:

| Display-Pin | Pi Pin-Name | GPIO Pin-Nummer | Funktion |
|---|---|---|---|
| **VCC** | 3.3V | **Pin 1** (oder 17) | Stromversorgung 3.3V |
| **GND** | Masse | **Pin 6** (oder 9, 14, 20) | Masse (Ground) |
| **DIN** | MOSI | **Pin 19** (GPIO 10) | SPI Datenleitung |
| **CLK** | SCLK | **Pin 23** (GPIO 11) | SPI Taktleitung |
| **CS** | CE0 | **Pin 24** (GPIO 8) | Chip-Auswahl |
| **DC** | GPIO 25 | **Pin 22** (GPIO 25) | Daten / Befehlsumschaltung |
| **RST** | GPIO 17 | **Pin 11** (GPIO 17) | Reset-Pin |
| **BUSY**| GPIO 24 | **Pin 18** (GPIO 24) | Status-Rückmeldung (Busy) |

---

## Installation & Einrichtung

### Automatische 1-Klick-Installation (Empfohlen)
```bash
git clone https://github.com/Jona-Walpert/piclock.git ~/piclock
cd ~/piclock
sudo ./install.sh
```

### Manuelle Installation Schritt für Schritt
1. **SPI aktivieren:**
   ```bash
   sudo raspi-config nonint do_spi 0
   ```
2. **Abhängigkeiten installieren:**
   ```bash
   sudo apt update
   sudo apt install -y python3-pil python3-spidev python3-rpi-lgpio fonts-dejavu-core
   ```
3. **Repository klonen:**
   ```bash
   git clone https://github.com/Jona-Walpert/piclock.git ~/piclock
   cd ~/piclock
   ```
4. **Hardware-Selbsttest ausführen:**
   ```bash
   python3 test_clock.py
   ```
5. **Autostart-Dienst einrichten:**
   ```bash
   sudo cp piclock.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now piclock.service
   ```

---

## Lizenz
MIT License (c) 2026 Jona Walpert - siehe [LICENSE](LICENSE).
Alle Quelltexte sind 100% KI-generiert.

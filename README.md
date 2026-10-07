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
* **Autostart & Reliability:** Runs as a standalone background `systemd` service (`piclock.service`) with automatic recovery and restart on boot.
* **Modular Driver Architecture:** Out-of-the-box support for Waveshare 2.13" V4, V3, and V2 panels, as well as a mock simulator driver for testing.

---

## Project Structure
```
piclock/
├── main.py                 # Main loop (minute ticks, event scheduling, signal handling)
├── display.py              # DisplayManager (layout engine, typography, refresh cycles)
├── time_sync.py            # Background NTP and systemd-timesyncd synchronizer
├── config.py               # Central configuration (intervals, fonts, timezones, rotation)
├── piclock.service         # Systemd service unit for autostart
├── test_clock.py           # Automated hardware & component self-test script
├── LICENSE                 # MIT License (Zero liability, open usage)
├── README.md               # Documentation
├── drivers/
│   ├── base.py             # Abstract display driver interface
│   ├── driver_waveshare.py # Waveshare 2.13" adapter (V4, V3, V2)
│   ├── mock.py             # Mock display simulator driver
│   └── waveshare/          # Original Waveshare low-level hardware drivers & epdconfig
└── fonts/                  # TrueType fonts (Roboto-Bold, Roboto-Regular)
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

---

## Systemd Service Management
The clock is managed via `systemd`:
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

## Hardware Self-Test
You can run the built-in self-test directly on the Pi:
```bash
# Run test with physical display hardware
python3 test_clock.py

# Run test in simulation mode (offline / without hardware)
python3 test_clock.py --mock
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
* **Autostart & Zuverlässigkeit:** Autarker Hintergrundbetrieb via `systemd` (`piclock.service`) mit automatischem Neustart.
* **Modulare Treiberarchitektur:** Waveshare 2.13" V4, V3, V2 sowie Mock-Simulator für Offline-Tests.

---

## Lizenz
MIT License (c) 2026 Jona Walpert - siehe [LICENSE](LICENSE).
Alle Quelltexte sind 100% KI-generiert.

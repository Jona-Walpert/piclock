# 🤖 100% AI GENERATED CODEBASE 🤖

> # ⚠️ WICHTIGER HINWEIS / IMPORTANT NOTICE:
> **DIESER GESAMTE CODE UND DIESES REPOSITORY WURDEN VOLLSTÄNDIG VON KÜNSTLICHER INTELLIGENZ (AI / GOOGLE ANTIGRAVITY) ERSTELLT.**
> 
> **ALL CODE IN THIS REPOSITORY IS 100% ARTIFICIAL INTELLIGENCE GENERATED.**
> 
> **HAFTUNGSAUSSCHLUSS (NO LIABILITY):**
> Der Code wird ohne jegliche Gewährleistung oder Haftung zur Verfügung gestellt ("AS IS"). Der Autor übernimmt keinerlei Verantwortung für eventuelle Schäden, Hardwaredefekte oder Fehlfunktionen. Macht damit, was ihr wollt! (Siehe [MIT LICENSE](LICENSE)).

---

# PiClock - E-Paper Digitaluhr für Raspberry Pi Zero 2 W

Moderne, energieeffiziente E-Paper-Digitaluhr für Raspberry Pi Zero 2 W und Waveshare 2.13 Zoll E-Paper Displays (V4, V3, V2).

## Features
* **Display-Optimierung:** Großflächige, moderne Typografie (Roboto Bold) mit Uhrzeit (HH:MM), Wochentag und Datum.
* **Partial Refresh:** Sekundenschnelle, flackerfreie Aktualisierung beim regulären Minutensprung.
* **Anti-Ghosting Deep Clean:** Konfigurierbare Schwarz/Weiß-Invertierungszyklen (alle 30-60 Minuten), um E-Ink Ghosting vollständig zu entfernen.
* **Präzise Zeitsynchronisation:** Stündlicher automatischer Abgleich mit NTP-Servern / `systemd-timesyncd`.
* **Autostart & Zuverlässigkeit:** Verwaltet als `systemd`-Dienst (`piclock.service`) mit automatischem Neustart bei Fehlern.
* **Modulare Treiberarchitektur:** Unterstützt Waveshare 2.13" V4, V3, V2 sowie einen Mock-Treiber für Entwicklung und Tests.

---

## Projektstruktur
```
piclock/
├── main.py                 # Hauptschleife (Minutentakt, Scheduler, Signal-Handling)
├── display.py              # DisplayManager (Layout, Typography, Refresh-Logik)
├── time_sync.py            # NTP- & systemd-timesyncd Synchronisation
├── config.py               # Zentrale Konfiguration (Intervalle, Schriftarten, Formate)
├── piclock.service         # Systemd-Service Unit
├── test_clock.py           # Automatisierter Hardware- & Komponententest
├── LICENSE                 # MIT License (Zero Liability)
├── drivers/
│   ├── base.py             # Abstraktes Treiber-Interface
│   ├── driver_waveshare.py # Waveshare 2.13" Adapter (V4, V3, V2)
│   ├── mock.py             # Simulator-Treiber für Tests
│   └── waveshare/          # Original Waveshare Hardware-Treiber & epdconfig
└── fonts/                  # TrueType Schriftarten (Roboto-Bold, Roboto-Regular)
```

---

## Konfiguration (`config.py`)
Alle Parameter können in `config.py` oder über Umgebungsvariablen angepasst werden:
* `FULL_REFRESH_INTERVAL_MINUTES`: Intervall für Voll-Refresh (Standard: `30` Minuten).
* `CLEANING_CYCLES`: Anzahl der Schwarz/Weiß-Flackerzyklen vor dem Voll-Refresh (Standard: `2`).
* `DISPLAY_ROTATION`: Drehung um 180 Grad (`0` oder `180`).
* `TIMEZONE`: Zeitzone (Standard: `Europe/Berlin`).
* `NTP_SYNC_INTERVAL_HOURS`: Intervall für NTP-Synchronisation (Standard: `1` Stunde).

---

## Systemd Dienst-Verwaltung
```bash
# Status prüfen
sudo systemctl status piclock.service

# Live-Logs ansehen
journalctl -u piclock.service -f

# Dienst neu starten / stoppen
sudo systemctl restart piclock.service
sudo systemctl stop piclock.service
```

---

## Lizenz
MIT License (c) 2026 Jona Walpert - siehe [LICENSE](LICENSE).
Code ist 100% KI-generiert.

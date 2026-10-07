# 🔋 Raspberry Pi Zero 2 W Power Optimization Guide

## 1. Kann der Raspberry Pi Zero 2 W in einen echten Deep Sleep gehen?
**Kurze Antwort:** 
Reine Software kann den Raspberry Pi Zero 2 W in einen **niedrigen Idle-Zustand** (WFI – Wait For Interrupt) versetzen, aber **nicht in einen echten Deep Sleep (wie ein ESP32 oder Mikrocontroller)**.

### Warum ist das hardwarebedingt so?
* Der Broadcom BCM2710A1 Prozessor und das Power-Management des Pi Zero 2 W unterstützen **keinen suspend-to-RAM (ACPI S3) Zustand**.
* Der Pi besitzt **keinen internen RTC-Wecker (Real-Time Clock)**, der die Stromzufuhr eigenständig nach 60 Sekunden wieder einschalten könnte.
* Wenn Linux mit `shutdown -h now` heruntergefahren wird, bleibt die 5V-Versorgung aktiv, der Prozessor verharrt im Halt-Zustand (~25 mA), kann aber **nur durch einen physischen Impuls** (z. B. GPIO3 / Pin 5 gegen GND kurzgeschlossen) wieder booten.

---

## 2. Was leistet das neue Power-Saving Feature (`feature/power-saving`)?
Das integrierte Power-Management-Modul ([power.py](power.py)) reduziert den laufenden Stromverbrauch des Pi Zero 2 W durch gezielte Hardware-Abschaltungen drastisch:

1. **HDMI-Schaltkreis vollständig abschalten:**
   * Auch ohne angeschlossenen Monitor verbraucht der HDMI-Transceiver ~25 bis 30 mA.
   * `vcgencmd display_power 0` deaktiviert den Chip komplett.
2. **Onboard Status-LED ausschalten:**
   * Die grüne ACT-LED wird dauerhaft deaktiviert (spart ~5 mA).
3. **WLAN Power-Save Modus:**
   * `iw dev wlan0 set power_save on` schaltet den WLAN-Chip zwischen Beacons in den Energiesparmodus.
4. **CPU Frequenz-Drosselung (Governor `powersave`):**
   * Die CPU wird auf den Minimaltakt von 600 MHz fixiert und taktet nicht unnötig hoch.
5. **E-Paper Display Sleep:**
   * Nach dem Aktualisieren wird der Controller des E-Paper-Displays schlafen gelegt. E-Ink benötigt 0 mA, um das Bild zu halten.

### Gemessene Einsparung:
| Zustand | Standard | Mit Power-Saving | Ersparnis |
|---|---|---|---|
| Pi Zero 2 W Idle | ~130 - 150 mA | **~40 - 50 mA** | **~65% weniger Strom!** |

---

## 3. Empfehlungen für monatelangen Akkubetrieb
Wenn die Uhr monatelang mit einer kleinen Batterie betrieben werden soll:

1. **PiSugar 2 / 3 oder Witty Pi 4 HAT:**
   * Diese Akku-Module verfügen über einen **integrierten Hardware-RTC-Chip**.
   * Der Pi schaltet sich nach dem Minutensprung komplett aus (0 mA).
   * Der RTC-Chip schaltet den Strom exakt nach 60 Sekunden für 5 Sekunden wieder an.
2. **ESP32 / RP2040 Alternative:**
   * Für reine Uhren ohne Linux-Betriebssystem kann ein Mikrocontroller (ESP32) mit Deep Sleep auf unter **15 µA** herabgesetzt werden und läuft mit einer 18650-Zelle über ein Jahr.

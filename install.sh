#!/usr/bin/env bash
# ==============================================================================
# PiClock - Automated Installation & Setup Script
# ==============================================================================
set -e

echo "============================================================"
echo "          PiClock - Installation & Setup Script             "
echo "============================================================"

# Check for root / sudo
if [ "$EUID" -ne 0 ]; then
    echo ">> Elevating privileges using sudo..."
    exec sudo "$0" "$@"
fi

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="piclock.service"
CURRENT_USER="${SUDO_USER:-pi}"

echo ">> Target Directory: $INSTALL_DIR"
echo ">> Running User:     $CURRENT_USER"

# 1. Enable SPI Hardware Interface
echo ""
echo "[1/5] Enabling SPI interface..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_spi 0
    echo " -> SPI enabled via raspi-config."
else
    # Direct fallback for config.txt
    for CFG in /boot/firmware/config.txt /boot/config.txt; do
        if [ -f "$CFG" ]; then
            if ! grep -q "^dtparam=spi=on" "$CFG"; then
                echo "dtparam=spi=on" >> "$CFG"
                echo " -> Added dtparam=spi=on to $CFG."
            fi
        fi
    done
fi

# Load kernel modules dynamically if not already present
modprobe spi_bcm2835 2>/dev/null || true
modprobe spidev 2>/dev/null || true

# 2. Install System Dependencies
echo ""
echo "[2/5] Installing required apt packages..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    python3-pil \
    python3-spidev \
    python3-rpi-lgpio \
    fonts-dejavu-core \
    fonts-freefont-ttf

# Add user to required hardware groups
usermod -aG spi,gpio,i2c "$CURRENT_USER" || true

# 3. Configure Timezone
echo ""
echo "[3/5] Verifying timezone and timesyncd..."
if command -v timedatectl >/dev/null 2>&1; then
    systemctl enable --now systemd-timesyncd 2>/dev/null || true
    echo " -> Current time: $(date)"
fi

# 4. Install Systemd Service
echo ""
echo "[4/5] Installing and enabling systemd service ($SERVICE_NAME)..."
cp "$INSTALL_DIR/$SERVICE_NAME" "/etc/systemd/system/$SERVICE_NAME"

# Update WorkingDirectory and User in service file dynamically
sed -i "s|^User=.*|User=$CURRENT_USER|" "/etc/systemd/system/$SERVICE_NAME"
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|" "/etc/systemd/system/$SERVICE_NAME"
sed -i "s|^ExecStart=.*|ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py|" "/etc/systemd/system/$SERVICE_NAME"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# 5. Service Status Verification
echo ""
echo "[5/5] Checking service status..."
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo " -> SUCCESS: $SERVICE_NAME is active and running!"
else
    echo " -> WARNING: $SERVICE_NAME failed to start. View logs with: journalctl -u $SERVICE_NAME -n 30"
fi

echo ""
echo "============================================================"
echo "          PiClock Installation Completed Successfully!       "
echo "============================================================"
echo "Useful commands:"
echo "  Check Status:  sudo systemctl status $SERVICE_NAME"
echo "  Live Logs:     journalctl -u $SERVICE_NAME -f"
echo "  Hardware Test: python3 $INSTALL_DIR/test_clock.py"
echo "============================================================"

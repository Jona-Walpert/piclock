"""Time synchronization module using systemd-timesyncd and standalone SNTP query.
"""

import logging
import socket
import struct
import subprocess
import threading
import time
from datetime import datetime, timezone
from typing import Optional

import config

logger = logging.getLogger(__name__)

# NTP timestamp base: January 1, 1900
NTP_DELTA = 2208988800


class TimeSynchronizer:
    """Manages periodic background time synchronization."""

    def __init__(self, interval_hours: int = None, servers: list = None):
        self.interval_hours = interval_hours or config.NTP_SYNC_INTERVAL_HOURS
        self.servers = servers or config.NTP_SERVERS
        self.last_sync: Optional[datetime] = None
        self.is_synced = False
        self.last_offset_ms: Optional[float] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def query_ntp_server(self, host: str, timeout: float = 3.0) -> Optional[float]:
        """Queries an NTP server directly via RFC 5905 UDP socket.

        Returns:
            Offset in milliseconds relative to local system clock, or None if failed.
        """
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.settimeout(timeout)

            # 48-byte NTP request packet: LI=0, VN=3, Mode=3 (Client) -> 0x1B
            data = b"\x1b" + 47 * b"\0"
            t1 = time.time()
            client.sendto(data, (host, 123))
            response, _ = client.recvfrom(1024)
            t4 = time.time()

            if len(response) >= 48:
                # Unpack transmit timestamp (bytes 40-48)
                seconds, fraction = struct.unpack("!II", response[40:48])
                ntp_time = (seconds - NTP_DELTA) + (fraction / (2**32))
                # Round-trip delay and clock offset
                offset = ntp_time - ((t1 + t4) / 2)
                offset_ms = offset * 1000.0
                logger.debug("NTP reply from %s: offset=%.2f ms", host, offset_ms)
                return offset_ms
        except Exception as e:
            logger.debug("NTP query to %s failed: %s", host, e)
            return None
        finally:
            client.close()

        return None

    def sync_now(self) -> bool:
        """Triggers active time synchronization."""
        logger.info("Starting active time synchronization...")
        sync_success = False

        # 1. Trigger systemd-timesyncd resync if available
        try:
            res = subprocess.run(
                ["systemctl", "restart", "systemd-timesyncd"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                logger.info("Triggered systemd-timesyncd restart successfully")
                sync_success = True
            else:
                logger.debug("systemd-timesyncd restart returned code %d", res.returncode)
        except Exception as e:
            logger.debug("Could not restart systemd-timesyncd: %s", e)

        # 2. Query NTP servers directly for verification and offset check
        for host in self.servers:
            offset = self.query_ntp_server(host, timeout=3.0)
            if offset is not None:
                self.last_offset_ms = offset
                sync_success = True
                logger.info("NTP synchronized via %s (offset: %.2f ms)", host, offset)
                break

        if sync_success:
            self.last_sync = datetime.now(timezone.utc)
            self.is_synced = True
        else:
            logger.warning("Time synchronization attempt failed for all sources")

        return sync_success

    def _worker(self):
        """Background thread executing sync periodically."""
        # Initial sync on startup
        self.sync_now()

        while not self._stop_event.is_set():
            # Wait for next interval or stop event
            wait_seconds = self.interval_hours * 3600
            if self._stop_event.wait(timeout=wait_seconds):
                break
            self.sync_now()

    def start(self):
        """Starts background periodic synchronization thread."""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._worker, name="TimeSyncWorker", daemon=True)
            self._thread.start()
            logger.info("TimeSyncWorker started (Interval: %dh)", self.interval_hours)

    def stop(self):
        """Stops background synchronization thread."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=2.0)
            logger.info("TimeSyncWorker stopped")

    def is_recently_synced(self, max_age_hours: int = 3) -> bool:
        """Returns True if a successful sync occurred within max_age_hours."""
        if not self.last_sync:
            return False
        age_seconds = (datetime.now(timezone.utc) - self.last_sync).total_seconds()
        return age_seconds <= (max_age_hours * 3600)


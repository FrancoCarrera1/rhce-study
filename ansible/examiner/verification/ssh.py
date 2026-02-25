"""AsyncSSH connection pool for Vagrant VMs."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

import asyncssh


# Default Vagrant directory — override with EXAMINER_VAGRANT_DIR env var
_DEFAULT_VAGRANT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "Mac",
)

CONNECT_TIMEOUT = 10
COMMAND_TIMEOUT = 30
STALE_SECONDS = 300  # re-connect after 5 minutes idle


def _vagrant_dir() -> Path:
    return Path(os.environ.get("EXAMINER_VAGRANT_DIR", _DEFAULT_VAGRANT_DIR))


def _find_vagrant_key(node_name: str) -> str | None:
    """Try to find the Vagrant-generated private key for a VM."""
    for provider in ("vmware_desktop", "virtualbox", "libvirt"):
        key_path = _vagrant_dir() / ".vagrant" / "machines" / node_name / provider / "private_key"
        if key_path.exists():
            return str(key_path)
    return None


class SSHConnectionPool:
    """Manages persistent AsyncSSH connections to Vagrant VMs."""

    def __init__(self) -> None:
        self._connections: dict[str, asyncssh.SSHClientConnection] = {}
        self._timestamps: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def _connect(self, host: str, ip: str, user: str = "vagrant") -> asyncssh.SSHClientConnection:
        """Open a new SSH connection, trying Vagrant key then password."""
        key_path = _find_vagrant_key(host)
        known_hosts = None  # Vagrant VMs have ephemeral host keys

        try:
            if key_path:
                conn = await asyncio.wait_for(
                    asyncssh.connect(
                        ip,
                        username=user,
                        client_keys=[key_path],
                        known_hosts=known_hosts,
                    ),
                    timeout=CONNECT_TIMEOUT,
                )
                return conn
        except Exception:
            pass

        # Fallback to password auth
        conn = await asyncio.wait_for(
            asyncssh.connect(
                ip,
                username=user,
                password="vagrant",
                known_hosts=known_hosts,
            ),
            timeout=CONNECT_TIMEOUT,
        )
        return conn

    async def get(self, host: str, ip: str, user: str = "vagrant") -> asyncssh.SSHClientConnection:
        """Get or create a connection. Re-connects if stale."""
        async with self._lock:
            conn = self._connections.get(host)
            ts = self._timestamps.get(host, 0)

            if conn is not None and (time.time() - ts) < STALE_SECONDS:
                try:
                    # Quick liveness check
                    await asyncio.wait_for(conn.run("true", check=True), timeout=5)
                    self._timestamps[host] = time.time()
                    return conn
                except Exception:
                    try:
                        conn.close()
                    except Exception:
                        pass

            # New connection needed
            conn = await self._connect(host, ip, user)
            self._connections[host] = conn
            self._timestamps[host] = time.time()
            return conn

    async def run_command(
        self, host: str, ip: str, command: str, user: str = "vagrant"
    ) -> tuple[int, str]:
        """Run a command on a host, return (exit_code, stdout)."""
        conn = await self.get(host, ip, user)
        result = await asyncio.wait_for(
            conn.run(command, check=False),
            timeout=COMMAND_TIMEOUT,
        )
        rc = result.exit_status if result.exit_status is not None else -1
        stdout = result.stdout or ""
        return rc, stdout

    async def test_connectivity(self, host: str, ip: str, user: str = "vagrant") -> tuple[bool, str]:
        """Test if we can connect and run a command. Returns (ok, message)."""
        try:
            conn = await self.get(host, ip, user)
            result = await asyncio.wait_for(
                conn.run("hostname", check=False),
                timeout=COMMAND_TIMEOUT,
            )
            return True, f"Connected — hostname: {(result.stdout or '').strip()}"
        except asyncio.TimeoutError:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Connection failed: {e}"

    async def close_all(self) -> None:
        """Close all connections."""
        async with self._lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except Exception:
                    pass
            self._connections.clear()
            self._timestamps.clear()

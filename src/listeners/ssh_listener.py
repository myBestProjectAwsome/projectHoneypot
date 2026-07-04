import asyncio
import asyncssh
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("logs/auth_attempts.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)

def log_event(event: dict):
    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

class HoneypotServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self._conn = conn
        peer = conn.get_extra_info("peername")
        self._peer_ip = peer[0] if peer else "unknown"
        log_event({"event": "connection", "src_ip": self._peer_ip})

    def connection_lost(self, exc):
        log_event({"event": "disconnect", "src_ip": self._peer_ip})

    def begin_auth(self, username):
        # True = auth requise (on veut voir les tentatives)
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        log_event({
            "event": "auth_attempt",
            "src_ip": self._peer_ip,
            "username": username,
            "password": password,
        })
        # Phase 1 : on refuse toujours
        return False

async def start_server():
    await asyncssh.create_server(
        HoneypotServer,
        "0.0.0.0",
        2222,
        server_host_keys=["keys/ssh_host_key"],
    )
    logging.info("Honeypot SSH en écoute sur :2222")

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_server()
    await asyncio.Event().wait()  # tourne indéfiniment

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

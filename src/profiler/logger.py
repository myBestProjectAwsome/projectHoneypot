import json
from datetime import datetime, timezone
from pathlib import Path

def build_event(event: dict, now = None) -> dict:
    """la methode enrichit un evenement d'un timestamp UTC"""

    if now is None:
        now = datetime.now(timezone.utc)

    enriched = dict(event)
    enriched["timestamp"] = now.isoformat()
    return enriched

def write_event(event:dict,log_file:Path, now = None) ->None:
    """la methode serialise et ecrit un evenement en JSON Lines"""

    log_file.parent.mkdir(parents=True, exist_ok=True)
    enriched = build_event(event, now=now)
    with open(log_file, "a") as f:
        f.write(json.dumps(enriched) + "\n")

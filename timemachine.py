#!/usr/bin/env python3
"""Time Machine configuration helpers for Satoshi Mirror."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class TimeMachineConfig:
    timeline_id: str
    snapshot_version: str
    mode: str
    wormhole_seed: str
    app_bindings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeline_id": self.timeline_id,
            "snapshot_version": self.snapshot_version,
            "mode": self.mode,
            "wormhole_seed": self.wormhole_seed,
            "app_bindings": self.app_bindings,
        }


def load_timemachine_config(config_path: str | Path) -> TimeMachineConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open("r") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Time machine config must be an object")

    required_fields = ["timeline_id", "snapshot_version", "mode", "wormhole_seed"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    app_bindings = payload.get("app_bindings") or {}
    if not isinstance(app_bindings, dict):
        raise ValueError("app_bindings must be a dictionary")

    return TimeMachineConfig(
        timeline_id=str(payload["timeline_id"]),
        snapshot_version=str(payload["snapshot_version"]),
        mode=str(payload["mode"]),
        wormhole_seed=str(payload["wormhole_seed"]),
        app_bindings=app_bindings,
    )

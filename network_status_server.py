#!/usr/bin/env python3

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

import requests


RPC_URL = os.getenv("BITCOIN_RPC_URL", "").strip()
RPC_USER = os.getenv("BITCOIN_RPC_USER", "").strip()
RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD", "").strip()
RPC_TIMEOUT = float(os.getenv("BITCOIN_RPC_TIMEOUT", "5"))
SERVER_HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("PORT", "8080"))


def rpc_call(method: str, params: list | None = None) -> Tuple[Any, float]:
    if not RPC_URL:
        raise RuntimeError("Configura BITCOIN_RPC_URL para consultar la red.")
    payload = {
        "jsonrpc": "1.0",
        "id": "satoshi-mirror",
        "method": method,
        "params": params or [],
    }
    auth = (RPC_USER, RPC_PASSWORD) if (RPC_USER or RPC_PASSWORD) else None
    start = time.perf_counter()
    response = requests.post(RPC_URL, json=payload, auth=auth, timeout=RPC_TIMEOUT)
    latency_ms = (time.perf_counter() - start) * 1000
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    return data.get("result"), latency_ms


def fetch_network_status() -> Dict[str, Any]:
    chain_info, chain_latency = rpc_call("getblockchaininfo")
    network_info, network_latency = rpc_call("getnetworkinfo")
    latency_ms = max(chain_latency, network_latency)
    progress = chain_info.get("verificationprogress")
    return {
        "block_height": chain_info.get("blocks"),
        "sync_progress": progress,
        "sync_progress_percent": progress * 100 if isinstance(progress, (int, float)) else None,
        "peers": network_info.get("connections"),
        "latency_ms": latency_ms,
    }


def json_response(handler: BaseHTTPRequestHandler, payload: Dict[str, Any], status: int = 200) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class NetworkStatusHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/network/status":
                status = fetch_network_status()
                json_response(self, {"ok": True, **status})
                return
            if parsed.path == "/api/network/height":
                chain_info, _ = rpc_call("getblockchaininfo")
                json_response(self, {"ok": True, "block_height": chain_info.get("blocks")})
                return
            if parsed.path == "/api/network/sync":
                chain_info, _ = rpc_call("getblockchaininfo")
                progress = chain_info.get("verificationprogress")
                json_response(
                    self,
                    {
                        "ok": True,
                        "sync_progress": progress,
                        "sync_progress_percent": progress * 100 if isinstance(progress, (int, float)) else None,
                    },
                )
                return
            if parsed.path == "/api/network/peers":
                network_info, _ = rpc_call("getnetworkinfo")
                json_response(self, {"ok": True, "peers": network_info.get("connections")})
                return
            if parsed.path == "/api/network/latency":
                _, latency_ms = rpc_call("getnetworkinfo")
                json_response(self, {"ok": True, "latency_ms": latency_ms})
                return
        except Exception as error:
            json_response(self, {"ok": False, "error": str(error)}, status=503)
            return

        json_response(self, {"ok": False, "error": "Endpoint no encontrado"}, status=404)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = HTTPServer((SERVER_HOST, SERVER_PORT), NetworkStatusHandler)
    print(f"Network status API escuchando en http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# satoshi_mirror.py - Unified Python-C++ Bridge
# Unifies all Python scripts and the Qubist-C++ core

import json
import os
import sys
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# ==================== UNIFIED CONFIGURATION ====================
class UnifiedConfig:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_path = self.root_dir / "Qubist_config.json"
        self.data = self.load_config()
        self.bridge = self.data["satoshi_mirror"]
        self.qubist = self.data.get("qubist_config", {})
        self.config = self.bridge

    def _merge_defaults(self, config: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(config)
        for key, value in defaults.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_defaults(merged[key], value)
        return merged
       
    def load_config(self) -> Dict:
        defaults = {
            "python_scripts": {
                "export_report": "export_report.py",
                "mirror_miner": "mirror_miner.py",
                "mirror_supply": "mirror_supply.py",
                "retro_pastnet": "retro_pastnet.py",
                "show_chain": "show_chain.py",
                "show_mirror_chain": "show_mirror_chain.py"
            },
            "qubist_layer": {
                "binary": "satoshi_mirror",
                "modes": ["mine", "ai_cycle", "energy", "quantum_synthesis"],
                "source_file": "satoshi_mirror.qub.cpp",
                "make_target": "qubist"
            },
            "data_files": {
                "mirror_chain": "mirror_chain.jsonl",
                "retro_chain": "retro_chain.jsonl",
                "retro_identity": "retro_identity.json",
                "timeline_report": "timeline_report.md"
            },
            "data_sync": {
                "mirror_chain": {
                    "python": "mirror_chain.jsonl",
                    "qubist": "data/mirror_chain.quantum.jsonl",
                    "sync_strategy": "bidirectional"
                },
                "retro_chain": {
                    "python": "retro_chain.jsonl",
                    "qubist": "data/retro_chain.quantum.jsonl",
                    "sync_strategy": "python_to_qubist"
                }
            },
            "quantum_modes": {
                "python_only": False,
                "cpp_only": False,
                "hybrid": True
            },
            "execution_modes": {
                "default": "python",
                "high_performance": "qubist",
                "quantum_synthesis": "hybrid"
            },
            "requirements": ["requests"]
        }
        raw_config = {}
        if self.config_path.exists():
            with open(self.config_path) as f:
                raw_config = json.load(f)
        bridge_config = raw_config.get("satoshi_mirror", {})
        if "python_scripts" not in bridge_config and "python_layer" in bridge_config:
            bridge_config = dict(bridge_config)
            bridge_config["python_scripts"] = bridge_config.get("python_layer", {}).get("scripts", {})
        merged_bridge = self._merge_defaults(bridge_config, defaults)
        return {
            "satoshi_mirror": merged_bridge,
            "qubist_config": raw_config.get("qubist_config", {})
        }
   
    def save_config(self):
        self.data["satoshi_mirror"] = self.bridge
        config_path = self.config_path
        config_path = self.root_dir / "Qubist_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.data, f, indent=2)

# ==================== PYTHON SCRIPT RUNNER ====================
class PythonScriptRunner:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.root = config.root_dir
       
    def run_script(self, script_name: str, args: List[str] = None) -> Dict:
        """Runs a Python script and returns results"""
        if args is None:
            args = []
           
        script = self.config.bridge["python_scripts"].get(script_name)
        if not script:
            return {"error": f"Script {script_name} not found"}
        script_path = self.root / script
        if not script_path.exists():
            return {"error": f"Script {script_name} not found"}
       
        try:
            # Build command
            cmd = [sys.executable, str(script_path)] + args
           
            # Run
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root
            )
           
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
   
    def run_export_report(self) -> Dict:
        """Genera timeline report"""
        return self.run_script("export_report")
   
    def run_mirror_miner(self, blocks: int = 1) -> Dict:
        """Mines blocks on the mirror chain"""
        return self.run_script("mirror_miner", [str(blocks)])
   
    def run_mirror_supply(self) -> Dict:
        """Calculates supply"""
        return self.run_script("mirror_supply")
   
    def run_retro_pastnet(self, date: str, url: str, wormhole: bool = False) -> Dict:
        """Queries the past"""
        args = []
        if wormhole:
            args.append("--wormhole")
        args.extend([date, url])
        return self.run_script("retro_pastnet", args)
   
    def run_show_chain(self) -> Dict:
        """Shows retro chain"""
        return self.run_script("show_chain")
   
    def run_show_mirror_chain(self) -> Dict:
        """Shows mirror chain"""
        return self.run_script("show_mirror_chain")

# ==================== QUBIST-C++ INTERFACE ====================
class QubistCoreInterface:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.root = config.root_dir
        self.qubist_binary = self.root / self.config.bridge["qubist_layer"]["binary"]
       
    def is_available(self) -> bool:
        """Checks whether the Qubist-C++ core is available"""
        return self.qubist_binary.exists() and os.access(self.qubist_binary, os.X_OK)
   
    def run_qubist(self, mode: str, args: List[str] = None) -> Dict:
        """Runs the Qubist-C++ core"""
        if not self.is_available():
            return {"error": "Qubist-C++ core not available. Compile with 'make qubist'"}
       
        if args is None:
            args = []
           
        try:
            cmd = [str(self.qubist_binary), mode] + args
           
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.root
            )
           
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "mode": mode
            }
        except Exception as e:
            return {"error": str(e)}
   
    def compile_qubist(self) -> Dict:
        """Compiles the Qubist-C++ core"""
        makefile = self.root / "Makefile"
        if not makefile.exists():
            return {"error": "Makefile not found"}
       
        try:
            make_target = self.config.bridge["qubist_layer"].get("make_target", "qubist")
            result = subprocess.run(
                ["make", make_target],
                capture_output=True,
                text=True,
                cwd=self.root
            )
           
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "available_now": self.is_available()
            }
        except Exception as e:
            return {"error": str(e)}

# ==================== UNIFIED QUANTUM ORCHESTRATOR ====================
class QuantumOrchestrator:
    def __init__(self):
        self.config = UnifiedConfig()
        self.python = PythonScriptRunner(self.config)
        self.qubist = QubistCoreInterface(self.config)
        self.mode = self.config.bridge["quantum_modes"]

    def export_ledger_snapshot(self, output_path: Optional[str] = None) -> Dict:
        """Exports an agents + metrics snapshot for the frontend."""
        ledger_file = self.config.qubist.get("agents", {}).get("ledger_file", "agents_ledger.json")
        ledger_path = Path(output_path) if output_path else self.config.root_dir / ledger_file
        ledger_data = self._load_ledger_data(ledger_path)
        snapshot = self._build_ledger_snapshot(ledger_data)
        with open(ledger_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        return {"success": True, "path": str(ledger_path), "agents": len(snapshot["agents"])}

    def _load_ledger_data(self, ledger_path: Path) -> Dict[str, Any]:
        if ledger_path.exists():
            with open(ledger_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        return {"agents": self._default_agents()}

    def _default_agents(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "bot_satoshi_mirror",
                "name": "Satoshi Mirror Bot",
                "balance_btc_mirror": 0.0,
                "ai_unlocked": False,
                "description": "Bot enfocado en minería espejo y economía temprana.",
                "specialty": "Minería cuántica",
            },
            {
                "id": "bot_archivist_2009",
                "name": "Archivist 2009",
                "balance_btc_mirror": 275.0,
                "ai_unlocked": True,
                "description": "Bot responsable de sintetizar conocimiento de bitcoin.org 2009.",
                "specialty": "Archivística temporal",
            },
        ]

    def _build_ledger_snapshot(self, ledger_data: Dict[str, Any]) -> Dict[str, Any]:
        agents = ledger_data.get("agents")
        if not isinstance(agents, list) or not agents:
            agents = self._default_agents()

        enriched_agents: List[Dict[str, Any]] = []
        total_balance = 0.0
        ai_unlocked_count = 0
        specialty_counts: Dict[str, int] = {}

        for agent in agents:
            if not isinstance(agent, dict):
                continue
            balance = float(agent.get("balance_btc_mirror", 0.0) or 0.0)
            total_balance += balance
            ai_unlocked = bool(agent.get("ai_unlocked", False))
            if ai_unlocked:
                ai_unlocked_count += 1
            specialty = agent.get("specialty")
            if not specialty:
                meta = agent.get("meta", {}) if isinstance(agent.get("meta"), dict) else {}
                specialty = meta.get("specialty") or agent.get("description") or "Operaciones urbanas"
            specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
            status = agent.get("status") or ("Activo" if ai_unlocked else "En espera")
            enriched_agents.append(
                {
                    "id": agent.get("id"),
                    "name": agent.get("name"),
                    "balance_btc_mirror": balance,
                    "ai_unlocked": ai_unlocked,
                    "description": agent.get("description", ""),
                    "specialty": specialty,
                    "status": status,
                    "owner": agent.get("owner", "Ledger"),
                    "meta": agent.get("meta", {}),
                }
            )

        locked_balance = round(total_balance * 0.26, 2)
        available_balance = round(total_balance - locked_balance, 2)
        snapshot = {
            "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "agents": enriched_agents,
            "metrics": {
                "total_agents": len(enriched_agents),
                "ai_unlocked_agents": ai_unlocked_count,
                "total_balance_btc": round(total_balance, 2),
                "available_balance_btc": available_balance,
                "locked_balance_btc": locked_balance,
                "specialties": specialty_counts,
            },
        }
        return snapshot
       
    def quantum_synthesis(self) -> Dict:
        """Runs full quantum synthesis (Python + C++)"""
        results = {}
       
        print("🌀 STARTING UNIFIED QUANTUM SYNTHESIS")
        print("=" * 50)
       
        # 1. Mine blocks with Python
        print("[1] Mining mirror blocks (Python)...")
        results["mining"] = self.python.run_mirror_miner(5)
       
        # 2. Run quantum AI cycle with Qubist
        print("[2] Running quantum AI cycle (Qubist-C++)...")
        results["ai_cycle"] = self.qubist.run_qubist("ai_cycle")
       
        # 3. Query the past
        print("[3] Querying the past (Python)...")
        results["retro"] = self.python.run_retro_pastnet(
            "2009-01-03",
            "https://bitcoin.org",
            wormhole=True
        )
       
        # 4. Calculate supply
        print("[4] Calculating supply (Python)...")
        results["supply"] = self.python.run_mirror_supply()
       
        # 5. Generate report
        print("[5] Generating timeline report (Python)...")
        results["report"] = self.python.run_export_report()
       
        # 6. Run energy sensor in the background
        print("[6] Starting quantum energy sensor (Qubist-C++)...")
        import threading
        energy_thread = threading.Thread(
            target=lambda: self.qubist.run_qubist("energy", ["5"])
        )
        energy_thread.daemon = True
        energy_thread.start()
       
        results["energy_sensor"] = {"status": "running_in_background"}
       
        print("=" * 50)
        print("✅ QUANTUM SYNTHESIS COMPLETED")
       
        return results
   
    def unified_mine(self, blocks: int, use_qubist: bool = False) -> Dict:
        """Mines blocks using Python or Qubist"""
        if use_qubist and self.qubist.is_available():
            print("⚡ Using Qubist-C++ core for quantum mining...")
            return self.qubist.run_qubist("mine", [str(blocks)])
        else:
            print("🐍 Using Python for mining...")
            return self.python.run_mirror_miner(blocks)
   
    def unified_report(self) -> Dict:
        """Generates unified report"""
        results = {}
       
        # Python report
        py_report = self.python.run_export_report()
        results["python_report"] = py_report
       
        # Read and display the generated report
        report_file = self.config.root_dir / "timeline_report.md"
        if report_file.exists():
            with open(report_file, 'r') as f:
                content = f.read()
                # Show first 10 lines
                lines = content.split('\n')[:10]
                print("\n📄 REPORT PREVIEW:")
                print("\n".join(lines))
                print("...")
       
        return results

# ==================== COMMAND LINE INTERFACE ====================
def main():
    parser = argparse.ArgumentParser(
        description="Satoshi Mirror - Unified Python/C++ Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s mine 10              # Mine 10 blocks (Python)
  %(prog)s mine --qubist 5      # Mine 5 blocks with Qubist-C++
  %(prog)s retro 2009-01-03 https://bitcoin.org --wormhole
  %(prog)s quantum-synthesis    # Full quantum synthesis
  %(prog)s compile-qubist       # Compile Qubist-C++ core
  %(prog)s status               # System status
        """
    )
   
    subparsers = parser.add_subparsers(dest="command", help="Commands")
   
    # Command: mine
    mine_parser = subparsers.add_parser("mine", help="Mine blocks")
    mine_parser.add_argument("blocks", type=int, help="Number of blocks to mine")
    mine_parser.add_argument("--qubist", action="store_true", help="Use Qubist-C++ core")
   
    # Command: supply
    subparsers.add_parser("supply", help="Show supply")
   
    # Command: retro
    retro_parser = subparsers.add_parser("retro", help="Query the past")
    retro_parser.add_argument("date", help="Date (YYYY-MM-DD)")
    retro_parser.add_argument("url", help="URL to query")
    retro_parser.add_argument("--wormhole", action="store_true", help="Wormhole mode")
   
    # Command: show
    show_parser = subparsers.add_parser("show", help="Show chains")
    show_parser.add_argument("type", choices=["mirror", "retro", "both"],
                           help="Type of chain to show")
   
    # Command: report
    subparsers.add_parser("report", help="Generate timeline report")

    # Command: export-ledger
    export_parser = subparsers.add_parser("export-ledger", help="Export agents ledger snapshot for frontend")
    export_parser.add_argument("--output", help="Optional output path for the snapshot JSON")
   
    # Command: quantum-synthesis
    subparsers.add_parser("quantum-synthesis", help="Full quantum synthesis")
   
    # Command: compile-qubist
    subparsers.add_parser("compile-qubist", help="Compile Qubist-C++ core")
   
    # Command: status
    subparsers.add_parser("status", help="System status")
   
    args = parser.parse_args()
   
    orchestrator = QuantumOrchestrator()
   
    if not args.command:
        parser.print_help()
        return
   
    if args.command == "mine":
        result = orchestrator.unified_mine(args.blocks, args.qubist)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(result.get("stdout", "✅ Mining completed"))
   
    elif args.command == "supply":
        result = orchestrator.python.run_mirror_supply()
        print(result.get("stdout", ""))
   
    elif args.command == "retro":
        result = orchestrator.python.run_retro_pastnet(
            args.date, args.url, args.wormhole
        )
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(result.get("stdout", "✅ Query completed"))
   
    elif args.command == "show":
        if args.type in ["mirror", "both"]:
            print("\n" + "="*60)
            print("MIRROR CHAIN:")
            print("="*60)
            result = orchestrator.python.run_show_mirror_chain()
            print(result.get("stdout", ""))
       
        if args.type in ["retro", "both"]:
            print("\n" + "="*60)
            print("RETRO CHAIN:")
            print("="*60)
            result = orchestrator.python.run_show_chain()
            print(result.get("stdout", ""))
   
    elif args.command == "report":
        result = orchestrator.unified_report()
        if "error" in result.get("python_report", {}):
            print(f"❌ Error: {result['python_report']['error']}")
        else:
            print("✅ Report generated in timeline_report.md")

    elif args.command == "export-ledger":
        result = orchestrator.export_ledger_snapshot(args.output)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Ledger snapshot exported to {result['path']}")
   
    elif args.command == "quantum-synthesis":
        orchestrator.quantum_synthesis()
   
    elif args.command == "compile-qubist":
        print("🔧 Compiling Qubist-C++ core...")
        result = orchestrator.qubist.compile_qubist()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(result.get("stdout", ""))
            if result.get("available_now"):
                print("✅ Qubist-C++ core compiled and ready")
   
    elif args.command == "status":
        print("📊 SATOSHI MIRROR SYSTEM STATUS")
        print("="*40)
       
        # Check files
        data_files = orchestrator.config.bridge["data_files"]
        for name, file in data_files.items():
            path = orchestrator.config.root_dir / file
            exists = "✅" if path.exists() else "❌"
            size = path.stat().st_size if path.exists() else 0
            print(f"{exists} {name:20} {file:25} {size:10,} bytes")
       
        # Check Qubist-C++
        qubist_ok = "✅" if orchestrator.qubist.is_available() else "❌"
        print(f"\n{qubist_ok} Qubist-C++ core available")
       
        # Check Python scripts
        print("\n📜 Python scripts:")
        scripts = orchestrator.config.bridge["python_scripts"]
        for name, script in scripts.items():
            path = orchestrator.config.root_dir / script
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {name:20}")

if __name__ == "__main__":
    main()

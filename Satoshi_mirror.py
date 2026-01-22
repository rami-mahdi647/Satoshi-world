#!/usr/bin/env python3
# satoshi_mirror.py - Unified Python-C++ Bridge
# Unifica todos los scripts Python y el núcleo Qubist-C++

import json
import os
import sys
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

# ==================== CONFIGURACIÓN UNIFICADA ====================
class UnifiedConfig:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config = self.load_config()
       
    def load_config(self) -> Dict:
        config_path = self.root_dir / "Qubist_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "python_scripts": {
                "export_report": "export_report.py",
                "mirror_miner": "mirror_miner.py",
                "mirror_supply": "mirror_supply.py",
                "retro_pastnet": "retro_pastnet.py",
                "show_chain": "show_chain.py",
                "show_mirror_chain": "show_mirror_chain.py"
            },
            "qubist_core": "satoshi_mirror",  # Ejecutable compilado
            "data_files": {
                "mirror_chain": "mirror_chain.jsonl",
                "retro_chain": "retro_chain.jsonl",
                "retro_identity": "retro_identity.json",
                "timeline_report": "timeline_report.md"
            },
            "quantum_modes": {
                "python_only": False,
                "cpp_only": False,
                "hybrid": True
            }
        }
   
    def save_config(self):
        config_path = self.root_dir / "Qubist_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

# ==================== PYTHON SCRIPT RUNNER ====================
class PythonScriptRunner:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.root = config.root_dir
       
    def run_script(self, script_name: str, args: List[str] = None) -> Dict:
        """Ejecuta un script Python y devuelve resultados"""
        if args is None:
            args = []
           
        script_path = self.root / self.config["python_scripts"].get(script_name)
        if not script_path.exists():
            return {"error": f"Script {script_name} no encontrado"}
       
        try:
            # Construir comando
            cmd = [sys.executable, str(script_path)] + args
           
            # Ejecutar
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
        """Mina bloques en la cadena espejo"""
        return self.run_script("mirror_miner", [str(blocks)])
   
    def run_mirror_supply(self) -> Dict:
        """Calcula suministro"""
        return self.run_script("mirror_supply")
   
    def run_retro_pastnet(self, date: str, url: str, wormhole: bool = False) -> Dict:
        """Consulta el pasado"""
        args = []
        if wormhole:
            args.append("--wormhole")
        args.extend([date, url])
        return self.run_script("retro_pastnet", args)
   
    def run_show_chain(self) -> Dict:
        """Muestra cadena retro"""
        return self.run_script("show_chain")
   
    def run_show_mirror_chain(self) -> Dict:
        """Muestra cadena espejo"""
        return self.run_script("show_mirror_chain")

# ==================== QUBIST-C++ INTERFACE ====================
class QubistCoreInterface:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.root = config.root_dir
        self.qubist_binary = self.root / self.config["qubist_core"]
       
    def is_available(self) -> bool:
        """Verifica si el núcleo Qubist-C++ está disponible"""
        return self.qubist_binary.exists() and os.access(self.qubist_binary, os.X_OK)
   
    def run_qubist(self, mode: str, args: List[str] = None) -> Dict:
        """Ejecuta el núcleo Qubist-C++"""
        if not self.is_available():
            return {"error": "Núcleo Qubist-C++ no disponible. Compila con 'make qubist'"}
       
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
        """Compila el núcleo Qubist-C++"""
        makefile = self.root / "Makefile"
        if not makefile.exists():
            return {"error": "Makefile no encontrado"}
       
        try:
            result = subprocess.run(
                ["make", "qubist"],
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
        self.mode = self.config.config["quantum_modes"]
       
    def quantum_synthesis(self) -> Dict:
        """Ejecuta síntesis cuántica completa (Python + C++)"""
        results = {}
       
        print("🌀 INICIANDO SÍNTESIS CUÁNTICA UNIFICADA")
        print("=" * 50)
       
        # 1. Minar bloques con Python
        print("[1] Minando bloques espejo (Python)...")
        results["mining"] = self.python.run_mirror_miner(5)
       
        # 2. Ejecutar ciclo IA cuántica con Qubist
        print("[2] Ejecutando ciclo IA cuántica (Qubist-C++)...")
        results["ai_cycle"] = self.qubist.run_qubist("ai_cycle")
       
        # 3. Consultar pasado
        print("[3] Consultando pasado (Python)...")
        results["retro"] = self.python.run_retro_pastnet(
            "2009-01-03",
            "https://bitcoin.org",
            wormhole=True
        )
       
        # 4. Calcular suministro
        print("[4] Calculando suministro (Python)...")
        results["supply"] = self.python.run_mirror_supply()
       
        # 5. Generar reporte
        print("[5] Generando reporte timeline (Python)...")
        results["report"] = self.python.run_export_report()
       
        # 6. Ejecutar sensor de energía en segundo plano
        print("[6] Iniciando sensor de energía cuántica (Qubist-C++)...")
        import threading
        energy_thread = threading.Thread(
            target=lambda: self.qubist.run_qubist("energy", ["5"])
        )
        energy_thread.daemon = True
        energy_thread.start()
       
        results["energy_sensor"] = {"status": "running_in_background"}
       
        print("=" * 50)
        print("✅ SÍNTESIS CUÁNTICA COMPLETADA")
       
        return results
   
    def unified_mine(self, blocks: int, use_qubist: bool = False) -> Dict:
        """Mina bloques usando Python o Qubist"""
        if use_qubist and self.qubist.is_available():
            print("⚡ Usando núcleo Qubist-C++ para minería cuántica...")
            return self.qubist.run_qubist("mine", [str(blocks)])
        else:
            print("🐍 Usando Python para minería...")
            return self.python.run_mirror_miner(blocks)
   
    def unified_report(self) -> Dict:
        """Genera reporte unificado"""
        results = {}
       
        # Reporte Python
        py_report = self.python.run_export_report()
        results["python_report"] = py_report
       
        # Leer y mostrar el reporte generado
        report_file = self.config.root_dir / "timeline_report.md"
        if report_file.exists():
            with open(report_file, 'r') as f:
                content = f.read()
                # Mostrar primeras 10 líneas
                lines = content.split('\n')[:10]
                print("\n📄 PREVIEW DEL REPORTE:")
                print("\n".join(lines))
                print("...")
       
        return results

# ==================== COMMAND LINE INTERFACE ====================
def main():
    parser = argparse.ArgumentParser(
        description="Satoshi Mirror - Bridge Python/C++ Unificado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s mine 10              # Mina 10 bloques (Python)
  %(prog)s mine --qubist 5      # Mina 5 bloques con Qubist-C++
  %(prog)s retro 2009-01-03 https://bitcoin.org --wormhole
  %(prog)s quantum-synthesis    # Síntesis cuántica completa
  %(prog)s compile-qubist       # Compila núcleo Qubist-C++
  %(prog)s status               # Estado del sistema
        """
    )
   
    subparsers = parser.add_subparsers(dest="command", help="Comandos")
   
    # Comando: mine
    mine_parser = subparsers.add_parser("mine", help="Minar bloques")
    mine_parser.add_argument("blocks", type=int, help="Número de bloques a minar")
    mine_parser.add_argument("--qubist", action="store_true", help="Usar núcleo Qubist-C++")
   
    # Comando: supply
    subparsers.add_parser("supply", help="Mostrar suministro")
   
    # Comando: retro
    retro_parser = subparsers.add_parser("retro", help="Consulta al pasado")
    retro_parser.add_argument("date", help="Fecha (YYYY-MM-DD)")
    retro_parser.add_argument("url", help="URL a consultar")
    retro_parser.add_argument("--wormhole", action="store_true", help="Modo wormhole")
   
    # Comando: show
    show_parser = subparsers.add_parser("show", help="Mostrar cadenas")
    show_parser.add_argument("type", choices=["mirror", "retro", "both"],
                           help="Tipo de cadena a mostrar")
   
    # Comando: report
    subparsers.add_parser("report", help="Generar reporte timeline")
   
    # Comando: quantum-synthesis
    subparsers.add_parser("quantum-synthesis", help="Síntesis cuántica completa")
   
    # Comando: compile-qubist
    subparsers.add_parser("compile-qubist", help="Compilar núcleo Qubist-C++")
   
    # Comando: status
    subparsers.add_parser("status", help="Estado del sistema")
   
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
            print(result.get("stdout", "✅ Minería completada"))
   
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
            print(result.get("stdout", "✅ Consulta completada"))
   
    elif args.command == "show":
        if args.type in ["mirror", "both"]:
            print("\n" + "="*60)
            print("CADENA ESPEJO:")
            print("="*60)
            result = orchestrator.python.run_show_mirror_chain()
            print(result.get("stdout", ""))
       
        if args.type in ["retro", "both"]:
            print("\n" + "="*60)
            print("CADENA RETRO:")
            print("="*60)
            result = orchestrator.python.run_show_chain()
            print(result.get("stdout", ""))
   
    elif args.command == "report":
        result = orchestrator.unified_report()
        if "error" in result.get("python_report", {}):
            print(f"❌ Error: {result['python_report']['error']}")
        else:
            print("✅ Reporte generado en timeline_report.md")
   
    elif args.command == "quantum-synthesis":
        orchestrator.quantum_synthesis()
   
    elif args.command == "compile-qubist":
        print("🔧 Compilando núcleo Qubist-C++...")
        result = orchestrator.qubist.compile_qubist()
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(result.get("stdout", ""))
            if result.get("available_now"):
                print("✅ Núcleo Qubist-C++ compilado y listo")
   
    elif args.command == "status":
        print("📊 ESTADO DEL SISTEMA SATOSHI MIRROR")
        print("="*40)
       
        # Verificar archivos
        data_files = orchestrator.config.config["data_files"]
        for name, file in data_files.items():
            path = orchestrator.config.root_dir / file
            exists = "✅" if path.exists() else "❌"
            size = path.stat().st_size if path.exists() else 0
            print(f"{exists} {name:20} {file:25} {size:10,} bytes")
       
        # Verificar Qubist-C++
        qubist_ok = "✅" if orchestrator.qubist.is_available() else "❌"
        print(f"\n{qubist_ok} Núcleo Qubist-C++ disponible")
       
        # Verificar scripts Python
        print("\n📜 Scripts Python:")
        scripts = orchestrator.config.config["python_scripts"]
        for name, script in scripts.items():
            path = orchestrator.config.root_dir / script
            exists = "✅" if path.exists() else "❌"
            print(f"  {exists} {name:20}")

if __name__ == "__main__":
    main()

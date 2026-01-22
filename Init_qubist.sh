#!/bin/bash
# init_qubist.sh - Full system initialization

echo "🌌 INITIALIZING SATOSHI MIRROR QUBIST"
echo "======================================"

# 1. Check dependencies
echo "[1] Checking quantum dependencies..."
if ! command -v g++ &> /dev/null; then
    echo "Installing g++..."
    xcode-select --install
fi

if ! command -v openssl &> /dev/null; then
    echo "Installing OpenSSL..."
    brew install openssl
fi

# 2. Create directory structure
echo "[2] Creating Qubist structure..."
mkdir -p quantum cyberpunk temporal data/logs

# 3. Compile core
echo "[3] Compiling Qubist-C++ core..."
make qubist

# 4. Initialize mirror blockchain
echo "[4] Initializing quantum blockchain..."
./satoshi_mirror mine 10

# 5. Configure quantum agents
echo "[5] Configuring agents..."
./satoshi_mirror add_agent bot_satoshi "Satoshi Quantum"
./satoshi_mirror add_agent bot_archivist "Archiver 2009-Q"
./satoshi_mirror add_agent bot_rami "Rami Quantum Baydoun" \
    "Bot-Rami in quantum superposition with Satoshi"

# 6. Start energy monitor
echo "[6] Starting quantum energy sensor (background)..."
./satoshi_mirror energy 10 &
ENERGY_PID=$!
echo $ENERGY_PID > data/energy.pid

# 7. Run full synthesis
echo "[7] Running full quantum synthesis..."
./satoshi_mirror quantum_synthesis

echo "======================================"
echo "✅ QUBIST SYSTEM INITIALIZED"
echo "📊 Available commands:"
echo "   ./satoshi_mirror [command]"
echo "📁 Data in: data/"
echo "📜 Logs in: data/logs/"

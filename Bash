#!/bin/bash
# init_qubist.sh - Inicialización completa del sistema

echo "🌌 INICIALIZANDO SATOSHI MIRROR QUBIST"
echo "======================================"

# 1. Verificar dependencias
echo "[1] Verificando dependencias cuánticas..."
if ! command -v g++ &> /dev/null; then
    echo "Instalando g++..."
    xcode-select --install
fi

if ! command -v openssl &> /dev/null; then
    echo "Instalando OpenSSL..."
    brew install openssl
fi

# 2. Crear estructura de directorios
echo "[2] Creando estructura Qubist..."
mkdir -p quantum cyberpunk temporal data/logs

# 3. Compilar núcleo
echo "[3] Compilando núcleo Qubist-C++..."
make qubist

# 4. Inicializar blockchain espejo
echo "[4] Inicializando blockchain cuántico..."
./satoshi_mirror mine 10

# 5. Configurar agentes cuánticos
echo "[5] Configurando agentes..."
./satoshi_mirror add_agent bot_satoshi "Satoshi Quantum"
./satoshi_mirror add_agent bot_archivist "Archiver 2009-Q"
./satoshi_mirror add_agent bot_rami "Rami Quantum Baydoun" \
    "Bot-Rami en superposición cuántica con Satoshi"

# 6. Iniciar monitor de energía
echo "[6] Iniciando sensor de energía cuántica (background)..."
./satoshi_mirror energy 10 &
ENERGY_PID=$!
echo $ENERGY_PID > data/energy.pid

# 7. Ejecutar síntesis completa
echo "[7] Ejecutando síntesis cuántica completa..."
./satoshi_mirror quantum_synthesis

echo "======================================"
echo "✅ SISTEMA QUBIST INICIALIZADO"
echo "📊 Comandos disponibles:"
echo "   ./satoshi_mirror [comando]"
echo "📁 Datos en: data/"
echo "📜 Logs en: data/logs/"

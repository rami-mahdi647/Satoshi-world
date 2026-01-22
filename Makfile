# Makefile para Satoshi Mirror Quantum Engine
# Ejecutar: make qubist

CXX = g++
CXXFLAGS = -std=c++20 -O3 -march=native -pthread
LDFLAGS = -lssl -lcrypto -lpthread

QUBIST_SOURCES = satoshi_mirror.qub.cpp
QUBIST_HEADERS = quantum/qubist.hpp cyberpunk/core.hpp temporal/blockchain.hpp
QUBIST_TARGET = satoshi_mirror

.PHONY: all clean qubist run

all: qubist

qubist: $(QUBIST_SOURCES)
@echo "🔧 Compilando núcleo Qubist-C++..."
$(CXX) $(CXXFLAGS) -o $(QUBIST_TARGET) $(QUBIST_SOURCES) $(LDFLAGS)
@echo "✅ Compilación completada: ./$(QUBIST_TARGET)"

run: qubist
@echo "🚀 Ejecutando síntesis cuántica..."
./$(QUBIST_TARGET) quantum_synthesis

clean:
rm -f $(QUBIST_TARGET) *.o
@echo "🧹 Limpieza completada"

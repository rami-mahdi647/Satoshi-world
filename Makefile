# Makefile for Satoshi Mirror Quantum Engine
# Run: make qubist

CXX = g++
CXXFLAGS = -std=c++20 -O3 -march=native -pthread
LDFLAGS = -lssl -lcrypto -lpthread

QUBIST_SOURCES = Satoshi_mirror.qub.cpp
QUBIST_HEADERS = quantum/qubist.hpp cyberpunk/core.hpp temporal/blockchain.hpp
QUBIST_TARGET = satoshi_mirror

.PHONY: all clean qubist run

all: qubist

qubist: $(QUBIST_SOURCES)
@echo "🔧 Compiling Qubist-C++ core..."
$(CXX) $(CXXFLAGS) -o $(QUBIST_TARGET) $(QUBIST_SOURCES) $(LDFLAGS)
@echo "✅ Compilation completed: ./$(QUBIST_TARGET)"

run: qubist
@echo "🚀 Running quantum synthesis..."
./$(QUBIST_TARGET) quantum_synthesis

clean:
rm -f $(QUBIST_TARGET) *.o
@echo "🧹 Cleanup completed"

# Satoshi Mirror Quantum Bridge

Satoshi Mirror is a hybrid system that fuses a Python orchestration layer with a Qubist-C++ core to prototype
disruptive technical innovations in decentralized computation. The repository blends experimental blockchain
mining, quantum-inspired hashing, and autonomous agent telemetry into a single, extensible stack.

## Disruptive innovation themes

- **Quantum-inspired security primitives**: the Qubist-C++ core models quantum-secure key generation and hashing
  to explore post-classical blockchain resilience.
- **Autonomous agent orchestration**: Python services run mining, ledger export, and system telemetry pipelines to
  simulate self-governing network behavior.
- **Unified pipeline for data + UI**: the ledger snapshot feeds a static frontend, proving a frictionless bridge
  between simulation and visualization.
- **Composable API surface**: the panel endpoints document how external services can inject bots, projects, and
  wallet activity into the mirror network.

## Quick deploy (bash)

Example based on `Deploy_satoshi_mirror.sh` to create directories, install dependencies, compile, and run basic commands:

```bash
mkdir -p {quantum,cyberpunk,temporal,data,logs,miner,retro,report}

pip install requests

make qubist

python3 Satoshi_mirror.py mine 5
python3 Satoshi_mirror.py quantum-synthesis
```

## Ledger snapshot for the frontend

The frontend (`index.html`) consumes a JSON snapshot with agents and metrics from static hosting. To regenerate it in
production, run:

```bash
python3 Satoshi_mirror.py export-ledger
```

The command overwrites/creates `agents_ledger.json` in the project root, ready to be served alongside `index.html`.

## Expected panel endpoints

The web panel (`index.html`) can integrate with an external API. The expected endpoint configuration is documented
in `api_endpoints.json` and includes routes like:

- `GET/POST /bots` — register and list active bots.
- `GET/POST /projects` — publish and list community projects.
- `POST /wallet/receive` — generate receive address/QR.
- `GET /activity` — recent activity (payments, missions, bots).

You can serve the API on a custom domain and configure its base in the panel’s “API base” field. The frontend uses
these routes to register bots, publish projects, and query activity.

## Python usage (Python)

Example taken from `Satoshi_mirror.py` that executes a Python script with arguments:

```python
def run_script(self, script_name: str, args: List[str] = None) -> Dict:
    """Runs a Python script and returns results"""
    if args is None:
        args = []

    script_path = self.root / self.config.config["python_scripts"].get(script_name)
    if not script_path.exists():
        return {"error": f"Script {script_name} not found"}

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
```

## Qubist-C++ core (C++)

Example taken from `Satoshi_mirror.qub.cpp` for quantum mining:

```cpp
qfunc mine_block(QubistInt difficulty = 4) -> QubistDict {
    current_height++;

    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::system_clock::to_time_t(now);

    // Generate quantum-secure keypair for block
    EC_KEY* key = EC_KEY_new_by_curve_name(NID_secp256k1);
    EC_KEY_generate_key(key);

    // Mine block with quantum-resistant algorithm
    QubistInt nonce = 0;
    QubistString block_hash;
    auto start = std::chrono::high_resolution_clock::now();

    while(true) {
        block_hash = generate_quantum_hash(std::to_string(current_height) +
                                          std::to_string(timestamp), nonce);

        if(block_hash.substr(0, difficulty) == std::string(difficulty, '0')) {
            break;
        }
        nonce++;
    }

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration<double>(end - start).count();

    // Create block
    QubistDict block = {
        {"height", current_height},
        {"hash", block_hash},
        {"previous_hash", current_height > 1 ? "0000..." : "0"},
        {"timestamp", timestamp},
        {"nonce", nonce},
        {"difficulty", difficulty},
        {"mining_time", duration},
        {"reward", block_reward},
        {"miner_address", "quantum_miner_" +
            std::to_string(std::hash<std::string>{}(block_hash.substr(0, 16)))},
        {"quantum_state", "superposition|mined⟩"}
    };

    // Save to chain
    std::ofstream chain(chain_file, std::ios::app);
    chain << json::dump(block) << std::endl;

    std::cout << "⛏️  Quantum block #" << current_height << " mined" << std::endl;
    std::cout << "   Hash: " << block_hash.substr(0, 32) << "..." << std::endl;
    std::cout << "   Nonce: " << nonce << " | Time: " << duration << "s" << std::endl;
    std::cout << "   Reward: " << block_reward << " mirror BTC" << std::endl;

    EC_KEY_free(key);
    return block;
}
```

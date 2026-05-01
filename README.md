# RTL Agent Pipeline

> Agentic CLI pipeline for RTL design automation — 
> spec-to-Verilog generation, LLM-powered lint fixing, 
> waveform anomaly debugging, and automated simulation.
> Built with Gemini 2.5 Flash-Lite + Hy3/OpenRouter fallback.

## What It Does
This project serves as an autonomous, multi-modal command-line agent for RTL development and debugging. It can parse plain-English specifications to generate pure synthesizable Verilog code and proper testbenches, recursively lint and fix Verilog syntax errors via `iverilog` integration, and debug VCD waveforms to flag anomalies like X/Z states and signal glitches. To tie it all together, it features an automated WSL2-based simulation bridge that seamlessly compiles, simulates, and debugs generated modules in a single cascaded command.

## What It Does NOT Do
- Does not formally verify functional correctness
- Does not perform synthesis, STA, or place & route
- iverilog clean ≠ silicon-ready

## Architecture
- **The ReAct Agent Loop Pattern**: The agent utilizes an iterative reasoning loop where it thinks about the problem, selects appropriate tools, analyzes the results, and dynamically corrects itself until reaching a terminal success or failure state.
- **Tool-calling Design**: The system relies on highly specialized tools like `run_iverilog` for syntax linting, `read_file`/`write_file` for active code editing, `get_waveform_summary` and `get_signal_transitions` for VCD anomaly detection, and `write_report` for final documentation generation.
- **LLM Fallback Chain**: It primarily leverages Google's highly efficient Gemini 2.5 Flash-Lite model, but features an automated, resilient fallback system to Tencent's Hy3 via OpenRouter in case of strict quota limits or API errors.
- **WSL2 Bridge**: Uses `simulator.py` to seamlessly pass cross-platform commands to compile generated `design.v` and `tb_design.v` files with `iverilog`, run `vvp` simulations on Linux subsystems, and securely extract the resulting VCD traces back to Windows.

## Prerequisites
- **Python 3.10+**
- **Windows with MSYS2** (`iverilog` + `verilator`)
- **WSL2 with Ubuntu** (for automated simulation)
  - `sudo apt install iverilog`
- Google AI Studio free API key (aistudio.google.com)
- OpenRouter free API key (openrouter.ai/keys)

## Setup

```bash
git clone <repo>
cd rtl-agent-pipeline
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```env
GOOGLE_API_KEY=your_google_key
OPENROUTER_API_KEY=your_openrouter_key
```

## Usage

### Mode 1 — Review existing RTL
```bash
python main.py --review examples/adder.v
```

### Mode 2 — Generate RTL from spec
```bash
python main.py --generate --spec "8-bit barrel shifter with direction control"
```

### Mode 3 — Debug a waveform
```bash
python main.py --debug --vcd examples/counter_debug.vcd --rtl examples/counter_debug.v
```

### Mode 4 — Full pipeline (generate + simulate + debug)
```bash
python main.py --generate --spec "4-bit up-down counter with reset" --simulate
```

### Simulate existing output folder
```bash
python main.py --simulate --dir outputs/20260501_161148
```

## Demo Results

### Barrel Shifter (--generate)
- Clean pass in 2 iterations, 0 bugs

### UART Transmitter (--generate)
- 4 iterations, 4 SystemVerilog→Verilog fixes applied
- Fallback to Hy3 triggered and seamless

### Counter Waveform (--debug)
- 6 anomalies detected across 4 iterations
- RTL line correlation for every finding

### Full Pipeline (--generate --simulate)
- Single command: spec → RTL → simulation → debug report
- WSL2 bridge fully automated via simulator.py

## Relevance
This project covers the first two stages of the RTL design pipeline:

```
Spec → RTL → Lint → Simulate → Synthesize → STA → P&R → Tape-out
       ↑_________________________↑
                Built here
```

Inspired by the work of ChipAgents and Cognichip in AI-native RTL design and verification automation.

## Limitations
- Functional correctness not guaranteed — iverilog lint passing ≠ correct behavior
- Testbench stimulus is generic — not design-specific
- Waveform debug works best with pre-annotated VCDs
- Free API tier limits: Gemini 2.5 Flash-Lite caps at ~1000 req/day, fallback to Hy3 is automatic

## License
MIT

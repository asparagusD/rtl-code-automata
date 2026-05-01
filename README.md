# RTL Agent Pipeline

> Agentic CLI pipeline for RTL design automation —
> spec-to-Verilog generation, LLM-powered lint fixing,
> automated simulation, and waveform anomaly debugging.
> Built with Hy3 (primary) + Ling-2.6-1T (fallback) via OpenRouter.

## What It Does

A 4-mode agentic CLI that automates the first two stages of the RTL design pipeline:

```
Spec → RTL → Lint → Simulate → [Synthesize → STA → P&R → Tape-out]
       ↑_________________________↑
                Built here
```

**Mode 1 (`--review`):** Takes an existing Verilog file, runs iverilog, sends errors to an LLM, auto-patches the file, loops until clean.

**Mode 2 (`--generate`):** Takes a plain English spec, generates Verilog RTL + cocotb testbench, pipes into Mode 1 review loop. Includes retry logic for empty/invalid LLM responses and pre-flight validation before review starts.

**Mode 3 (`--debug`):** Takes a VCD waveform + RTL, parses signal transitions, auto-detects anomalies (X/Z states, stuck signals, glitches, missing resets), correlates to RTL lines, produces a structured markdown debug report.

**Mode 4 (`--simulate` flag):** Full automated pipeline — generate RTL, compile + simulate via WSL2 bridge (no manual terminal switching), pipe VCD directly into debug agent. Single command, zero manual steps.

## What It Does NOT Do
- Does not run cocotb testbenches (testbench generated, not executed)
- Does not perform synthesis, STA, or place & route
- iverilog clean ≠ functionally correct silicon
- Waveform debugger catches structural and timing anomalies, not all functional bugs

## Architecture

### Agent Loop Pattern
All modes use a ReAct (Reason + Act) tool-calling loop:
LLM reasons about the current state → calls a tool → observes result → reasons again → loops until done or max iterations.

### Tools Available
| Agent | Tools |
|-------|-------|
| Review Agent | `run_iverilog`, `read_file`, `write_file` |
| Debug Agent | `get_waveform_summary`, `get_signal_transitions`, `read_file`, `write_report` |

### LLM Fallback Chain
| Role | Model | Provider |
|------|-------|----------|
| Primary | `tencent/hy3-preview:free` | OpenRouter (free) |
| Fallback | `inclusionai/ling-2.6-1t:free` | OpenRouter (free) |

Both via OpenRouter — single API key, automatic fallback on 429.

### WSL2 Simulation Bridge (`simulator.py`)
Converts Windows paths to WSL2 mount points, runs `iverilog` + `vvp` inside WSL2 via subprocess, returns VCD path to Windows pipeline. No manual terminal switching required.

## Prerequisites
- **Python 3.10+** on Windows
- **MSYS2** with `iverilog` installed (for `--review` and `--generate`)
- **WSL2 with Ubuntu** + `iverilog` (for `--simulate` automated VCD generation)
  ```bash
  sudo apt install iverilog
  ```
- **OpenRouter free API key** — [openrouter.ai/keys](https://openrouter.ai/keys)
  (no credit card, no daily cap)

## Setup

```bash
git clone <repo>
cd rtl-agent-pipeline
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```env
OPENROUTER_API_KEY=your_key_here
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

### Mode 4 — Full automated pipeline
```bash
python main.py --generate --spec "4-bit up-down counter with reset" --simulate
```

### Simulate existing output folder
```bash
python main.py --simulate --dir outputs/20260501_161148
```

### Optional flags
```
--max-iter N    Set max agent iterations (default: 8)
--output DIR    Custom output directory
```

## Demo Results

### Barrel Shifter (`--generate`)
Clean pass in 2 iterations. Zero bugs. No fallback needed.

### UART Transmitter (`--generate --simulate`)
- Generation retry triggered — empty response caught, succeeded on attempt 2
- Review agent completed truncated RTL (missing `endmodule`, unassigned `tx_busy`, incomplete state machine) in 5 iterations
- Debug agent diagnosed simulation timing mismatch: `BAUD_DIV=434` requires 4340ns minimum but testbench ran 200ns. Correctly concluded RTL logic is sound — testbench window too short. 13 tool calls, 6 iterations.

### Counter Waveform Debug (`--debug`)
6 anomalies found across 4 iterations: X-states, stuck signals, glitch, missing reset — all correlated to specific RTL lines with suggested fixes.

### Up-Down Counter (`--generate --simulate`)
Caught underflow wrap-around bug: `count=0`, `up_down=0` → `count - 1 = 15` (no floor check). Exact timestamp, RTL line, and root cause identified.

## Relevance to Industry
This project covers the spec-to-lint-to-simulate stages that companies like ChipAgents and Cognichip are building at scale. ChipAgents demonstrated Waveform Agents at DVCon 2026 for the same class of problem this pipeline solves.

## Known Limitations
- UART and other timing-sensitive designs need longer simulation windows than the default 200ns testbench
- Testbench stimulus is generic — not tailored to design specifics
- Free tier models occasionally return empty responses — retry logic handles this up to 3 attempts
- X at t=0 on reg outputs is correctly classified as INFO, not CRITICAL (expected Verilog simulation behavior)

## Project Structure
```
main.py            — CLI entrypoint, all 4 modes
agent.py           — RTL review ReAct loop
debug_agent.py     — Waveform debug ReAct loop
llm.py             — OpenRouter client, fallback chain
tools.py           — iverilog, read_file, write_file
waveform_parser.py — VCD parsing, anomaly detection
simulator.py       — WSL2 bridge for automated simulation
prompts.py         — All LLM system/user prompts
examples/          — Demo Verilog files and VCDs
```

## License
MIT

# Agentic RTL Design Automation Pipeline

A CLI agent that generates Verilog RTL from a natural language spec and automatically fixes compilation errors using an LLM in a loop.

## Overview
This tool automates Verilog code generation from plain English specifications and actively loops to review, lint, and fix Verilog code.

### Features
- **Part 1: Code Review Agent**: Takes an existing `.v` file, runs `iverilog` to lint the design, and uses the LLM to recursively fix the code until compilation passes.
- **Part 2: Spec-to-RTL Generator**: Takes a plain English specification, generates the raw Verilog RTL alongside a `cocotb` Python testbench, and automatically pipes the RTL into the Review Agent to ensure syntactical correctness.
- **Dual-Provider Architecture**: Powered primarily by Google's **Gemini 2.5 Flash-Lite**, with an automatic, seamless fallback to **Tencent Hy3 Preview via OpenRouter** if the hard daily quotas are hit or rate limits are reached.

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.10+**
- **iverilog** (`iverilog.exe` on Windows or `iverilog` on Linux/macOS) available in your system `PATH`.

### 2. Installation
Install the required python dependencies:
```bash
pip install openai rich python-dotenv
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## Usage

### Part 1: Review and Fix Existing RTL
```bash
python main.py --review examples/adder.v
```

### Part 2: Generate RTL from Specification
```bash
python main.py --generate --spec "an 8-bit carry lookahead adder with registered output"
```
*Optional: You can use `--output <folder>` to specify a custom base directory for generated files (defaults to `outputs/`). You can also use `--max-iter <num>` to increase or decrease the retry limit.*

---

## Demo Test Cases

Here are 3 real test cases demonstrating the capabilities of the pipeline:

### Test Case 1: Fixing a Buggy Module
**Command:** 
```bash
python main.py --review examples/adder.v
```
**Result:** 
The review agent iteratively analyzed `examples/adder.v`, which intentionally contained three distinct errors: a missing semicolon, an undeclared signal (`c_in` instead of `cin`), and a wire width mismatch. The agent caught and successfully fixed all three bugs within 4 iterations, rendering the file completely clean.

### Test Case 2: Generating a UART Transmitter
**Command:**
```bash
python main.py --generate --spec "8-bit UART transmitter with configurable baud rate divider, start and stop bits, and a transmission done flag"
```
**Result:** 
The pipeline successfully generated the raw Verilog design alongside a matching `cocotb` testbench inside the `outputs/` folder. The Verilog design was then seamlessly piped into the Review Agent, which successfully linted it on the first iteration without needing to make any syntactical fixes.

### Test Case 3: Generating an 8-bit Barrel Shifter
**Command:**
```bash
python main.py --generate --spec "8-bit barrel shifter with shift amount input and direction control"
```
**Result:**
The pipeline successfully generated the Verilog design and testbench. During the subsequent automatic linting phase, the Review Agent caught compilation errors and recursively applied fixes over 5 iterations, ultimately bringing the RTL code to a clean, successfully compiling state.

import subprocess
import os
from pathlib import Path
from rich.console import Console

console = Console()

def windows_to_wsl_path(windows_path: str) -> str:
    r"""Convert Windows path to WSL2 mountpoint path.
    Example: I:\rtl-code-reviewer\outputs\xyz 
          -> /mnt/i/rtl-code-reviewer/outputs/xyz
    """
    path = Path(windows_path).resolve()
    drive = path.drive.lower().replace(":", "")
    rest = str(path.relative_to(path.anchor)).replace("\\", "/")
    return f"/mnt/{drive}/{rest}"

def run_in_wsl2(bash_command: str, cwd: str = None) -> subprocess.CompletedProcess:
    wsl_cmd = ["wsl", "bash", "-c"]
    if cwd:
        wsl_cwd = windows_to_wsl_path(cwd)
        full_cmd = f"cd {wsl_cwd} && {bash_command}"
    else:
        full_cmd = bash_command
    wsl_cmd.append(full_cmd)
    return subprocess.run(wsl_cmd, capture_output=True, text=True)

def compile_and_simulate(output_dir: str) -> str | None:
    """
    Compiles design.v + tb_design.v with iverilog and runs vvp via WSL2.
    Returns path to generated waveform.vcd or None on failure.
    """
    # Check for WSL
    wsl_check = subprocess.run(["wsl", "--status"], capture_output=True, text=True)
    if wsl_check.returncode != 0 and "Default Distribution" not in wsl_check.stdout:
        # Fallback check just in case wsl --status isn't enough
        wsl_check2 = subprocess.run(["wsl", "echo", "1"], capture_output=True, text=True)
        if wsl_check2.returncode != 0:
            console.print("[red]WSL2 not found. Install it with: wsl --install[/red]")
            console.print(f"[dim]Manual commands:\n  cd {output_dir}\n  iverilog -o sim.vvp design.v tb_design.v\n  vvp sim.vvp[/dim]")
            return None
        
    iv_check = run_in_wsl2("which iverilog")
    if iv_check.returncode != 0:
        console.print("[red]iverilog not found in WSL2. Run: sudo apt install iverilog[/red]")
        return None
        
    design_v = os.path.join(output_dir, "design.v")
    tb_v = os.path.join(output_dir, "tb_design.v")
    vvp_out = os.path.join(output_dir, "sim.vvp")
    vcd_out = os.path.join(output_dir, "waveform.vcd")
    
    if not os.path.exists(design_v) or not os.path.exists(tb_v):
        console.print("[red]✗ design.v or tb_design.v not found in output directory.[/red]")
        return None
    
    # Step 1 — Compile
    console.print("[cyan]⚙ Compiling RTL with iverilog via WSL2...[/cyan]")
    compile_result = run_in_wsl2(
        "iverilog -o sim.vvp design.v tb_design.v",
        cwd=output_dir
    )
    if compile_result.returncode != 0:
        console.print(f"[red]✗ iverilog failed:\n{compile_result.stderr}[/red]")
        return None
    console.print("[green]✓ Compilation successful[/green]")

    # Step 2 — Simulate
    console.print("[cyan]⚙ Running simulation via WSL2...[/cyan]")
    sim_result = run_in_wsl2("vvp sim.vvp", cwd=output_dir)
    console.print(f"[dim]{sim_result.stdout.strip()}[/dim]")

    # Step 3 — Verify VCD was created
    if not os.path.exists(vcd_out):
        console.print("[red]✗ waveform.vcd was not created[/red]")
        if sim_result.stdout:
            console.print(f"[dim]vvp stdout:\n{sim_result.stdout}[/dim]")
        if sim_result.stderr:
            console.print(f"[red]vvp stderr:\n{sim_result.stderr}[/red]")
        return None
    
    console.print(f"[green]✓ Simulation complete → waveform.vcd generated[/green]")
    return vcd_out

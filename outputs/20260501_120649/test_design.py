import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.handle import Force, Release

async def generate_clock(dut):
    """Generate clock pulses."""
    while True:
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer(1, units="ns")

async def reset_dut(dut):
    """Reset the DUT."""
    dut.rst_n.value = 0
    await FallingEdge(dut.clk) # Ensure reset is asserted before or at clock edge
    await RisingEdge(dut.clk)  # Keep reset asserted for at least one clock cycle
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)  # Wait for reset to deassert and the first active clock edge

@cocotb.test()
async def minimal_carry_lookahead_adder_test(dut):
    """Minimal test for carry_lookahead_adder_8bit_registered."""

    # Start clock generation
    cocotb.start_soon(generate_clock(dut))

    # Initial values for inputs
    dut.A.value = 0
    dut.B.value = 0
    dut.carry_in.value = 0

    # Apply reset
    await reset_dut(dut)
    dut._log.info("Reset complete.")

    # Test Case 1: Simple addition
    A_val = 0x05
    B_val = 0x03
    carry_in_val = 0
    expected_sum = (A_val + B_val + carry_in_val) & 0xFF
    expected_carry_out = 0

    dut.A.value = A_val
    dut.B.value = B_val
    dut.carry_in.value = carry_in_val
    dut._log.info(f"Applying A={A_val:#04x}, B={B_val:#04x}, carry_in={carry_in_val}")

    await RisingEdge(dut.clk) # Inputs registered on this edge
    await RisingEdge(dut.clk) # Registered outputs available on this edge

    actual_sum = dut.sum.value.integer
    actual_carry_out = dut.carry_out.value.integer
    dut._log.info(f"Observed: sum={actual_sum:#04x}, carry_out={actual_carry_out}")

    assert actual_sum == expected_sum, \
        f"TEST FAILED (Simple addition): Sum mismatch. Expected {expected_sum:#04x}, got {actual_sum:#04x}"
    assert actual_carry_out == expected_carry_out, \
        f"TEST FAILED (Simple addition): Carry out mismatch. Expected {expected_carry_out}, got {actual_carry_out}"
    dut._log.info("Test Case 1 Passed: 5 + 3 + 0 = 8")

    # Test Case 2: Overflow condition
    A_val = 0xFF
    B_val = 0x01
    carry_in_val = 0
    expected_sum = (A_val + B_val + carry_in_val) & 0xFF # 255 + 1 + 0 = 256, so 0x00
    expected_carry_out = 1

    dut.A.value = A_val
    dut.B.value = B_val
    dut.carry_in.value = carry_in_val
    dut._log.info(f"Applying A={A_val:#04x}, B={B_val:#04x}, carry_in={carry_in_val}")

    await RisingEdge(dut.clk) # Inputs registered
    await RisingEdge(dut.clk) # Registered outputs available

    actual_sum = dut.sum.value.integer
    actual_carry_out = dut.carry_out.value.integer
    dut._log.info(f"Observed: sum={actual_sum:#04x}, carry_out={actual_carry_out}")

    assert actual_sum == expected_sum, \
        f"TEST FAILED (Overflow): Sum mismatch. Expected {expected_sum:#04x}, got {actual_sum:#04x}"
    assert actual_carry_out == expected_carry_out, \
        f"TEST FAILED (Overflow): Carry out mismatch. Expected {expected_carry_out}, got {actual_carry_out}"
    dut._log.info("Test Case 2 Passed: 0xFF + 0x01 + 0 = 0x00 (carry_out=1)")

    # Test Case 3: All ones with carry_in
    A_val = 0xFF
    B_val = 0xFF
    carry_in_val = 1
    expected_sum = (A_val + B_val + carry_in_val) & 0xFF # 255 + 255 + 1 = 511, so 0xFF
    expected_carry_out = 1

    dut.A.value = A_val
    dut.B.value = B_val
    dut.carry_in.value = carry_in_val
    dut._log.info(f"Applying A={A_val:#04x}, B={B_val:#04x}, carry_in={carry_in_val}")

    await RisingEdge(dut.clk) # Inputs registered
    await RisingEdge(dut.clk) # Registered outputs available

    actual_sum = dut.sum.value.integer
    actual_carry_out = dut.carry_out.value.integer
    dut._log.info(f"Observed: sum={actual_sum:#04x}, carry_out={actual_carry_out}")

    assert actual_sum == expected_sum, \
        f"TEST FAILED (All ones): Sum mismatch. Expected {expected_sum:#04x}, got {actual_sum:#04x}"
    assert actual_carry_out == expected_carry_out, \
        f"TEST FAILED (All ones): Carry out mismatch. Expected {expected_carry_out}, got {actual_carry_out}"
    dut._log.info("Test Case 3 Passed: 0xFF + 0xFF + 1 = 0xFF (carry_out=1)")
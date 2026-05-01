import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
import random

async def generate_clock(dut):
    dut.clk.value = 0
    await cocotb.start(Clock(dut.clk, 10, units="ns").start())

@cocotb.test()
async def basic_test(dut):
    await generate_clock(dut)

    dut._log.info("Starting reset")
    dut.rst_n.value = 0
    dut.A.value = 0
    dut.B.value = 0
    dut.Cin.value = 0
    await Timer(20, units="ns")
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    dut._log.info("Reset complete")

    await RisingEdge(dut.clk) # Wait for one cycle after reset to ensure outputs update

    # Test case 1: 0 + 0 + 0
    dut._log.info(f"Test 1: A=0, B=0, Cin=0")
    dut.A.value = 0
    dut.B.value = 0
    dut.Cin.value = 0
    await RisingEdge(dut.clk)
    expected_sum = 0
    expected_cout = 0
    assert dut.Sum.value == expected_sum, f"Sum mismatch: Expected {expected_sum}, got {dut.Sum.value}"
    assert dut.Cout.value == expected_cout, f"Cout mismatch: Expected {expected_cout}, got {dut.Cout.value}"

    # Test case 2: 5 + 3 + 0
    dut._log.info(f"Test 2: A=5, B=3, Cin=0")
    dut.A.value = 5
    dut.B.value = 3
    dut.Cin.value = 0
    await RisingEdge(dut.clk)
    expected_sum = 8
    expected_cout = 0
    assert dut.Sum.value == expected_sum, f"Sum mismatch: Expected {expected_sum}, got {dut.Sum.value}"
    assert dut.Cout.value == expected_cout, f"Cout mismatch: Expected {expected_cout}, got {dut.Cout.value}"

    # Test case 3: 255 + 1 + 0 (overflow)
    dut._log.info(f"Test 3: A=255, B=1, Cin=0")
    dut.A.value = 255
    dut.B.value = 1
    dut.Cin.value = 0
    await RisingEdge(dut.clk)
    expected_sum = 0 # 255 + 1 = 256, 8-bit sum is 0
    expected_cout = 1
    assert dut.Sum.value == expected_sum, f"Sum mismatch: Expected {expected_sum}, got {dut.Sum.value}"
    assert dut.Cout.value == expected_cout, f"Cout mismatch: Expected {expected_cout}, got {dut.Cout.value}"

    # Test case 4: 255 + 255 + 1 (all ones)
    dut._log.info(f"Test 4: A=255, B=255, Cin=1")
    dut.A.value = 255
    dut.B.value = 255
    dut.Cin.value = 1
    await RisingEdge(dut.clk)
    expected_sum = 255 # 255 + 255 + 1 = 511, 8-bit sum is 255
    expected_cout = 1
    assert dut.Sum.value == expected_sum, f"Sum mismatch: Expected {expected_sum}, got {dut.Sum.value}"
    assert dut.Cout.value == expected_cout, f"Cout mismatch: Expected {expected_cout}, got {dut.Cout.value}"
    
    # Test case 5: Random values
    dut._log.info("Starting random tests")
    for i in range(50):
        val_a = random.randint(0, 2**8 - 1)
        val_b = random.randint(0, 2**8 - 1)
        val_cin = random.randint(0, 1)

        dut._log.info(f"Random Test {i+1}: A={val_a}, B={val_b}, Cin={val_cin}")
        dut.A.value = val_a
        dut.B.value = val_b
        dut.Cin.value = val_cin
        await RisingEdge(dut.clk)

        expected_full_sum = val_a + val_b + val_cin
        expected_sum = expected_full_sum & 0xFF
        expected_cout = 1 if expected_full_sum > 255 else 0

        assert dut.Sum.value == expected_sum, f"Random Sum mismatch for A={val_a}, B={val_b}, Cin={val_cin}: Expected {expected_sum}, got {dut.Sum.value}"
        assert dut.Cout.value == expected_cout, f"Random Cout mismatch for A={val_a}, B={val_b}, Cin={val_cin}: Expected {expected_cout}, got {dut.Cout.value}"

    dut._log.info("All tests passed!")
import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.handle import Force, Release

async def generate_clock(dut):
    """Generate clock pulses."""
    for _ in range(50):
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer(1, units="ns")

@cocotb.test()
async def cla_8bit_reg_test(dut):
    """Test the 8-bit Carry Lookahead Adder with registration."""

    cocotb.start_soon(generate_clock(dut))

    # Initialize inputs
    dut.rst_n.value = 0
    dut.A.value = 0
    dut.B.value = 0
    dut.cin.value = 0

    await Timer(2, units="ns")  # Wait for a bit for initial values to settle
    await RisingEdge(dut.clk)

    # De-assert reset
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk) # Wait for clock cycle for reset to take effect on registered outputs

    # Test case 1: 0 + 0 + 0 = 0, cout = 0
    dut.A.value = 0
    dut.B.value = 0
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk) # Sample outputs
    assert dut.sum.value == 0, f"Test Case 1 Failed: sum expected 0, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 1 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 2: 1 + 0 + 0 = 1, cout = 0
    dut.A.value = 1
    dut.B.value = 0
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 1, f"Test Case 2 Failed: sum expected 1, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 2 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 3: 0 + 1 + 0 = 1, cout = 0
    dut.A.value = 0
    dut.B.value = 1
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 1, f"Test Case 3 Failed: sum expected 1, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 3 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 4: 1 + 1 + 0 = 2, cout = 0 (for 8-bit sum)
    dut.A.value = 1
    dut.B.value = 1
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 2, f"Test Case 4 Failed: sum expected 2, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 4 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 5: MAX + MAX + 0 = -2 (wrapped around), cout = 1
    dut.A.value = 0xFF # 255
    dut.B.value = 0xFF # 255
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == (0xFF + 0xFF) & 0xFF, f"Test Case 5 Failed: sum expected {(0xFF + 0xFF) & 0xFF}, got {dut.sum.value}" # 254
    assert dut.cout.value == 1, f"Test Case 5 Failed: cout expected 1, got {dut.cout.value}"

    # Test case 6: MAX + MAX + 1 = -1 (wrapped around), cout = 1
    dut.A.value = 0xFF
    dut.B.value = 0xFF
    dut.cin.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == (0xFF + 0xFF + 1) & 0xFF, f"Test Case 6 Failed: sum expected {(0xFF + 0xFF + 1) & 0xFF}, got {dut.sum.value}" # 255
    assert dut.cout.value == 1, f"Test Case 6 Failed: cout expected 1, got {dut.cout.value}"

    # Test case 7: 127 + 127 + 0 = 254, cout = 0
    dut.A.value = 127 # 0x7F
    dut.B.value = 127 # 0x7F
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 254, f"Test Case 7 Failed: sum expected 254, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 7 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 8: 127 + 127 + 1 = 255, cout = 0
    dut.A.value = 127
    dut.B.value = 127
    dut.cin.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 255, f"Test Case 8 Failed: sum expected 255, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 8 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 9: 127 + 128 + 0 = 255, cout = 0
    dut.A.value = 127
    dut.B.value = 128
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 255, f"Test Case 9 Failed: sum expected 255, got {dut.sum.value}"
    assert dut.cout.value == 0, f"Test Case 9 Failed: cout expected 0, got {dut.cout.value}"

    # Test case 10: 127 + 129 + 0 = 0 (wrapped), cout = 1
    dut.A.value = 127
    dut.B.value = 129
    dut.cin.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert dut.sum.value == 0, f"Test Case 10 Failed: sum expected 0, got {dut.sum.value}"
    assert dut.cout.value == 1, f"Test Case 10 Failed: cout expected 1, got {dut.cout.value}"

    # Test using a loop for more values
    for i in range(10):
        for j in range(10):
            for k in range(2): # cin
                a = i * 10
                b = j * 10
                cin = k
                expected_sum = (a + b + cin) & 0xFF
                expected_cout = 1 if (a + b + cin) > 0xFF else 0

                dut.A.value = a
                dut.B.value = b
                dut.cin.value = cin
                await RisingEdge(dut.clk)
                await FallingEdge(dut.clk)
                assert dut.sum.value == expected_sum, \
                    f"Loop Test Failed: A={a}, B={b}, cin={cin}, sum expected {expected_sum}, got {dut.sum.value}"
                assert dut.cout.value == expected_cout, \
                    f"Loop Test Failed: A={a}, B={b}, cin={cin}, cout expected {expected_cout}, got {dut.cout.value}"

    await Timer(100, units="ns") # Allow clock to run a bit more before ending
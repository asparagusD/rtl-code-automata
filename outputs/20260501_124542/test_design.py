import cocotb
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_cla_adder_8bit(dut):
    """Test the 8-bit CLA adder with basic operations."""

    # Initialize inputs
    dut.a.value = 0
    dut.b.value = 0
    dut.cin.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Test case 1: 0 + 0 = 0
    dut.a.value = 0
    dut.b.value = 0
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 0
    assert dut.cout.value == 0

    # Test case 2: 1 + 0 = 1
    dut.a.value = 1
    dut.b.value = 0
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 1
    assert dut.cout.value == 0

    # Test case 3: 0 + 1 = 1
    dut.a.value = 0
    dut.b.value = 1
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 1
    assert dut.cout.value == 0

    # Test case 4: 1 + 1 = 0, carry 1
    dut.a.value = 1
    dut.b.value = 1
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 0
    assert dut.cout.value == 1

    # Test case 5: 5 + 3 = 8
    dut.a.value = 5
    dut.b.value = 3
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 8
    assert dut.cout.value == 0

    # Test case 6: 255 + 1 = 0, carry 1
    dut.a.value = 255
    dut.b.value = 1
    dut.cin.value = 0
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 0
    assert dut.cout.value == 1

    # Test case 7: 100 + 156 + 1 (cin) = 257 -> 1, carry 1
    dut.a.value = 100
    dut.b.value = 156
    dut.cin.value = 1
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 1
    assert dut.cout.value == 1

    # Test case 8: Max values with carry
    dut.a.value = 255
    dut.b.value = 255
    dut.cin.value = 1
    await ClockCycles(dut.clk, 1)
    assert dut.sum.value == 255
    assert dut.cout.value == 1
```
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_up_down_counter(dut):
    """Basic test for up_down_counter_4bit"""

    # Start a clock
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Test counting up
    dut.en.value = 1
    dut.up.value = 1
    for i in range(16):
        expected_count = i
        await RisingEdge(dut.clk)
        assert dut.count.value == expected_count, f"Count mismatch during up count: expected {expected_count}, got {dut.count.value}"
        assert dut.overflow.value == 0, "Overflow detected unexpectedly during up count"

    # Test overflow on up count
    await RisingEdge(dut.clk)
    assert dut.count.value == 0, "Count should wrap around to 0 after overflow"
    assert dut.overflow.value == 1, "Overflow should be high after wrapping around"

    # Test counting down
    dut.up.value = 0
    for i in range(15, -1, -1):
        expected_count = i
        await RisingEdge(dut.clk)
        assert dut.count.value == expected_count, f"Count mismatch during down count: expected {expected_count}, got {dut.count.value}"
        assert dut.overflow.value == 0, "Overflow detected unexpectedly during down count"

    # Test overflow on down count
    await RisingEdge(dut.clk)
    assert dut.count.value == 15, "Count should wrap around to 15 after underflow"
    assert dut.overflow.value == 1, "Overflow should be high after wrapping around (down)"

    # Disable enable and check values
    dut.en.value = 0
    await RisingEdge(dut.clk)
    initial_count = dut.count.value
    initial_overflow = dut.overflow.value
    await RisingEdge(dut.clk)
    assert dut.count.value == initial_count, "Count should not change when enable is low"
    assert dut.overflow.value == initial_overflow, "Overflow should not change when enable is low"

    dut.en.value = 1
    await RisingEdge(dut.clk)
    assert dut.count.value == initial_count, "Count should not change when enable is low"
    assert dut.overflow.value == initial_overflow, "Overflow should not change when enable is low"

    dut.en.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert dut.count.value == initial_count, "Count should remain stable when enable is low"
    assert dut.overflow.value == initial_overflow, "Overflow should remain stable when enable is low"

```
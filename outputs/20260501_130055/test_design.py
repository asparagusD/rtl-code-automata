import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def test_barrel_shifter(dut):
    """Minimal test for the 8-bit barrel shifter."""

    # Clock generation (optional, uncomment if clock is present in DUT)
    # cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset the DUT (optional, uncomment if reset is present in DUT)
    # dut.rst.value = 1
    # await Timer(10, units="ns")
    # dut.rst.value = 0
    # await RisingEdge(dut.clk)

    # Test case 1: No shift
    dut.data_in.value = 0b11001010
    dut.shift_amount.value = 0b000
    dut.direction.value = 0 # Left
    await Timer(10, units="ns") # Wait for combinational logic to settle
    assert dut.data_out.value == 0b11001010, f"Test 1 failed: Expected 0b11001010, got {dut.data_out.value}"

    # Test case 2: Left shift by 2
    dut.data_in.value = 0b10101010
    dut.shift_amount.value = 0b010
    dut.direction.value = 0 # Left
    await Timer(10, units="ns")
    assert dut.data_out.value == 0b10101000, f"Test 2 failed: Expected 0b10101000, got {dut.data_out.value}"

    # Test case 3: Right shift by 3
    dut.data_in.value = 0b10101010
    dut.shift_amount.value = 0b011
    dut.direction.value = 1 # Right
    await Timer(10, units="ns")
    assert dut.data_out.value == 0b00010101, f"Test 3 failed: Expected 0b00010101, got {dut.data_out.value}"

    # Test case 4: Maximum left shift (by 7)
    dut.data_in.value = 0xAA # 0b10101010
    dut.shift_amount.value = 0b111
    dut.direction.value = 0 # Left
    await Timer(10, units="ns")
    assert dut.data_out.value == 0x00, f"Test 4 failed: Expected 0x00, got {dut.data_out.value}" # With 8 bits, shifting left by 7 results in all zeros

    # Test case 5: Maximum right shift (by 7)
    dut.data_in.value = 0x55 # 0b01010101
    dut.shift_amount.value = 0b111
    dut.direction.value = 1 # Right
    await Timer(10, units="ns")
    assert dut.data_out.value == 0x00, f"Test 5 failed: Expected 0x00, got {dut.data_out.value}" # With 8 bits, shifting right by 7 results in all zeros

    # Test case 6: Left shift by 1
    dut.data_in.value = 0x01
    dut.shift_amount.value = 0b001
    dut.direction.value = 0 # Left
    await Timer(10, units="ns")
    assert dut.data_out.value == 0x02, f"Test 6 failed: Expected 0x02, got {dut.data_out.value}"

    # Test case 7: Right shift by 1
    dut.data_in.value = 0x02
    dut.shift_amount.value = 0b001
    dut.direction.value = 1 # Right
    await Timer(10, units="ns")
    assert dut.data_out.value == 0x01, f"Test 7 failed: Expected 0x01, got {dut.data_out.value}"

    cocotb.log.info("All basic tests passed!")
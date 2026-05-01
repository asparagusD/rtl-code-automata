import cocotb
from cocotb.triggers import ClockCycles

@cocotb.test()
async def barrel_shifter_test(dut):
    """Test barrel shifter with various shifts."""

    # Clock generation if module had a clock, but it doesn't.
    # We will just drive inputs and check outputs immediately.

    # Test case 1: No shift
    dut.data_in.value = 0x5A
    dut.shift_amount.value = 0
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait() # Simulate a small delay to let logic settle
    assert dut.data_out.value == 0x5A, f"Expected 0x5A, got {dut.data_out.value}"

    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x5A, f"Expected 0x5A, got {dut.data_out.value}"


    # Test case 2: Left shift by 1
    dut.data_in.value = 0x01
    dut.shift_amount.value = 1
    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x02, f"Expected 0x02, got {dut.data_out.value}"

    # Test case 3: Right shift by 1
    dut.data_in.value = 0x02
    dut.shift_amount.value = 1
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x01, f"Expected 0x01, got {dut.data_out.value}"

    # Test case 4: Left shift by 3 (1 + 2)
    dut.data_in.value = 0x01
    dut.shift_amount.value = 3 # Binary 011, means shift by 1 then by 2
    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x08, f"Expected 0x08, got {dut.data_out.value}"

    # Test case 5: Right shift by 3 (1 + 2)
    dut.data_in.value = 0x08
    dut.shift_amount.value = 3 # Binary 011, means shift by 1 then by 2
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x01, f"Expected 0x01, got {dut.data_out.value}"

    # Test case 6: Left shift by 4
    dut.data_in.value = 0x01
    dut.shift_amount.value = 4 # Binary 100, means shift by 4
    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x10, f"Expected 0x10, got {dut.data_out.value}"

    # Test case 7: Right shift by 4
    dut.data_in.value = 0x10
    dut.shift_amount.value = 4 # Binary 100, means shift by 4
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x01, f"Expected 0x01, got {dut.data_out.value}"

    # Test case 8: Full left shift by 7 (1 + 2 + 4)
    dut.data_in.value = 0x01
    dut.shift_amount.value = 7 # Binary 111, means shift by 1, then 2, then 4
    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x80, f"Expected 0x80, got {dut.data_out.value}"

    # Test case 9: Full right shift by 7 (1 + 2 + 4)
    dut.data_in.value = 0x80
    dut.shift_amount.value = 7 # Binary 111, means shift by 1, then 2, then 4
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x01, f"Expected 0x01, got {dut.data_out.value}"

    # Test case 10: Shift with all bits set, left
    dut.data_in.value = 0xFF
    dut.shift_amount.value = 2
    dut.shift_left.value = 1
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0xFC, f"Expected 0xFC, got {dut.data_out.value}"

    # Test case 11: Shift with all bits set, right
    dut.data_in.value = 0xFF
    dut.shift_amount.value = 2
    dut.shift_left.value = 0
    await cocotb.triggers.Event().wait()
    assert dut.data_out.value == 0x3F, f"Expected 0x3F, got {dut.data_out.value}"
```
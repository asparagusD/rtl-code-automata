import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles
from cocotb.regression import TestModule

@cocotb.test()
async def basic_tx_test(dut):
    """Test basic UART transmission."""

    clk = dut.clk
    reset_n = dut.reset_n
    tx_data = dut.tx_data
    tx_start = dut.tx_start
    tx_busy = dut.tx_busy
    tx_done = dut.tx_done
    tx_out = dut.tx_out

    # Reset the DUT
    dut.reset_n.value = 0
    await ClockCycles(clk, 10)
    dut.reset_n.value = 1
    await ClockCycles(clk, 10)

    # Test Case 1: Send a single byte
    data_to_send = 0x55
    tx_data.value = data_to_send
    tx_start.value = 1
    dut.log.info(f"Starting transmission of {data_to_send:02X}")
    await RisingEdge(clk)
    tx_start.value = 0
    await RisingEdge(clk)

    # Wait for transmission to start and complete
    while tx_busy.value:
        await RisingEdge(clk)

    dut.log.info("Transmission busy deasserted")
    await RisingEdge(clk) # Wait one cycle to ensure tx_done is stable

    assert tx_done.value == 1, "tx_done should be asserted after transmission"
    dut.log.info("tx_done asserted")

    # Wait for the DUT to return to IDLE
    while not tx_busy.value and not tx_done.value:
        await RisingEdge(clk)

    dut.log.info("Transmission finished and DUT returned to IDLE")

    # Test Case 2: Send another byte while busy (should be ignored)
    tx_data.value = 0xAA
    tx_start.value = 1
    dut.log.info("Asserting tx_start while busy")
    await RisingEdge(clk)
    tx_start.value = 0
    await RisingEdge(clk)

    # Wait for transmission to start and complete
    while tx_busy.value:
        await RisingEdge(clk)

    dut.log.info("Transmission busy deasserted")
    await RisingEdge(clk)

    assert tx_done.value == 1, "tx_done should be asserted after transmission"
    dut.log.info("tx_done asserted")

    # Wait for the DUT to return to IDLE
    while not tx_busy.value and not tx_done.value:
        await RisingEdge(clk)

    dut.log.info("Transmission finished and DUT returned to IDLE")

    # Test Case 3: Send data with no stop after reset
    dut.reset_n.value = 0
    await ClockCycles(clk, 5)
    dut.reset_n.value = 1
    await ClockCycles(clk, 5)

    data_to_send_3 = 0x0F
    tx_data.value = data_to_send_3
    tx_start.value = 1
    dut.log.info(f"Starting transmission after reset: {data_to_send_3:02X}")
    await RisingEdge(clk)
    tx_start.value = 0
    await RisingEdge(clk)

    while tx_busy.value:
        await RisingEdge(clk)
    dut.log.info("Transmission busy deasserted after reset test")
    await RisingEdge(clk)

    assert tx_done.value == 1, "tx_done should be asserted after transmission after reset"
    dut.log.info("tx_done asserted after reset test")

    while not tx_busy.value and not tx_done.value:
        await RisingEdge(clk)
    dut.log.info("Transmission finished and DUT returned to IDLE after reset test")

@cocotb.test()
async def test_idle_state(dut):
    """Test that the DUT stays in IDLE state when no tx_start is asserted."""
    clk = dut.clk
    reset_n = dut.reset_n
    tx_start = dut.tx_start
    tx_busy = dut.tx_busy
    tx_out = dut.tx_out

    dut.reset_n.value = 0
    await ClockCycles(clk, 10)
    dut.reset_n.value = 1
    await ClockCycles(clk, 10)

    # Ensure tx_start is low
    tx_start.value = 0

    for _ in range(100):
        await RisingEdge(clk)
        assert tx_busy.value == 0, "tx_busy should be 0 in IDLE state"
        assert tx_out.value == 1, "tx_out should be high in IDLE state"

    dut.log.info("DUT remained in IDLE state as expected.")
```
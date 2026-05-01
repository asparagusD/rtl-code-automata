module uart_tx #(
    parameter CLK_FREQ = 50000000, // System clock frequency in Hz
    parameter BAUD_RATE = 9600      // Target baud rate in bps
) (
    input wire clk,
    input wire reset_n,

    // Data input and control
    input wire [7:0] tx_data,
    input wire tx_start,
    output wire tx_busy,
    output wire tx_done,

    // UART output
    output wire tx_out
);

    // Calculate the baud rate divider
    localparam BAUD_DIVIDER = CLK_FREQ / BAUD_RATE;

    // State machine states (encoded as 3-bit binary)
    localparam [2:0] IDLE      = 3'b000;
    localparam [2:0] START_BIT = 3'b001;
    localparam [2:0] DATA_BITS = 3'b010;
    localparam [2:0] STOP_BIT  = 3'b011;
    localparam [2:0] DONE      = 3'b100;

    // Internal signals
    reg [7:0] tx_buffer;
    reg [3:0] bit_count;
    reg [31:0] clk_counter; // Counter for baud rate generation (wide enough)
    reg [2:0] current_state, next_state;
    reg tx_start_reg;
    reg tx_done_reg;
    reg tx_busy_reg;

    // Transmit output
    reg tx_out_reg;
    assign tx_out = tx_out_reg;

    // State machine registers
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            current_state <= IDLE;
        end else begin
            current_state <= next_state;
        end
    end

    // Baud rate clock generation and control logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            clk_counter <= 0;
            tx_start_reg <= 1'b0;
            tx_busy_reg <= 1'b0;
            tx_done_reg <= 1'b0;
            tx_buffer <= 8'b0;
            bit_count <= 4'b0;
            tx_out_reg <= 1'b1; // Idle state is high
        end else begin
            // Default assignments
            tx_start_reg <= tx_start;
            tx_done_reg <= 1'b0; // Clear done flag by default
            tx_busy_reg <= (current_state != IDLE) || (next_state != IDLE);

            case (current_state)
                IDLE: begin
                    if (tx_start_reg) begin
                        tx_buffer <= tx_data;
                        bit_count <= 4'b0; // Reset bit counter
                        clk_counter <= 0;  // Reset baud rate counter
                        tx_out_reg <= 1'b0; // Start bit (low)
                        tx_done_reg <= 1'b0; // Clear done flag
                    end else begin
                        tx_out_reg <= 1'b1; // Idle state is high
                    end
                end
                START_BIT: begin
                    clk_counter <= clk_counter + 1;
                    if (clk_counter == BAUD_DIVIDER - 1) begin
                        clk_counter <= 0;
                        tx_out_reg <= tx_buffer[0]; // First data bit
                        bit_count <= 1; // Move to first data bit
                    end
                end
                DATA_BITS: begin
                    clk_counter <= clk_counter + 1;
                    if (clk_counter == BAUD_DIVIDER - 1) begin
                        clk_counter <= 0;
                        tx_out_reg <= tx_buffer[bit_count];
                        bit_count <= bit_count + 1;
                    end
                end
                STOP_BIT: begin
                    clk_counter <= clk_counter + 1;
                    if (clk_counter == BAUD_DIVIDER - 1) begin
                        clk_counter <= 0;
                        tx_out_reg <= 1'b1; // Stop bit (high)
                        bit_count <= 4'b0;  // Reset bit counter
                    end
                end
                DONE: begin
                    tx_done_reg <= 1'b1; // Set done flag
                    if (!tx_start_reg) begin // If new transmission is not requested
                        tx_out_reg <= 1'b1; // Return to idle high
                    end
                end
                default: begin
                    tx_out_reg <= 1'b1;
                end
            endcase
        end
    end

    // Next state logic (combinational)
    always @(*) begin
        next_state = current_state; // Default to staying in current state
        case (current_state)
            IDLE: begin
                if (tx_start_reg) begin
                    next_state = START_BIT;
                end
            end
            START_BIT: begin
                if (clk_counter == BAUD_DIVIDER - 1) begin
                    if (bit_count == 8) begin // All data bits sent
                        next_state = STOP_BIT;
                    end else begin
                        next_state = DATA_BITS;
                    end
                end
            end
            DATA_BITS: begin
                if (clk_counter == BAUD_DIVIDER - 1) begin
                    if (bit_count == 8) begin // All data bits sent
                        next_state = STOP_BIT;
                    end
                end
            end
            STOP_BIT: begin
                if (clk_counter == BAUD_DIVIDER - 1) begin
                    next_state = DONE;
                end
            end
            DONE: begin
                if (!tx_start_reg) begin // If new transmission is not requested
                    next_state = IDLE;
                end
            end
            default: begin
                next_state = IDLE;
            end
        endcase
    end

    // Output assignments
    assign tx_busy = tx_busy_reg;
    assign tx_done = tx_done_reg;

endmodule

`timescale 1ns/1ns

module counter_debug;
    reg clk;
    reg rst_n;
    reg up_down;
    
    // Internal signals we want to dump
    reg [3:0] count;
    reg overflow;
    reg [2:0] fsm_state;

    initial begin
        $dumpfile("examples/counter_debug.vcd");
        $dumpvars(0, counter_debug);
        
        clk = 0;
        // Bug: missing reset assertion (rst_n never drops to 0)
        rst_n = 1; 
        up_down = 1;

        #150;
        $finish;
    end

    // Clock generator
    always #5 clk = ~clk;

    // Bug 1: X state on fsm_state at t=45
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            fsm_state <= 3'b000;
        end else begin
            case (fsm_state)
                3'b000: fsm_state <= 3'b001;
                3'b001: fsm_state <= 3'b010;
                3'b010: fsm_state <= 3'b111; // Illegal state
                // Missing default case causes X state if state goes rogue
            endcase
        end
    end

    // Bug 2: Stuck overflow signal
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            overflow <= 1'b0;
        end else begin
            overflow <= 1'b0; // Stuck at 0!
        end
    end
    
    // Bug 3: Glitch on count
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'b0000;
        end else begin
            if (up_down)
                count <= count + 1;
            else
                count <= count - 1;
        end
    end
    
    // Injecting a glitch into count directly
    initial begin
        #120;
        force count = 4'b1111;
        #1;
        release count;
    end

endmodule

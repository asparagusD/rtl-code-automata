`timescale 1ns/1ps
module tb_counter_debug;
    reg clk;
    reg rst_n;
    reg up_down;
    wire [3:0] count;
    wire overflow;

    counter_debug uut (
        .clk(clk),
        .rst_n(rst_n),
        .up_down(up_down),
        .count(count),
        .overflow(overflow)
    );

    initial begin
        $dumpfile("examples/counter_debug.vcd");
        $dumpvars(0, tb_counter_debug);
        
        clk = 0;
        // Bug: missing reset assertion (rst_n never drops to 0)
        rst_n = 1; 
        up_down = 1;

        #150;
        $finish;
    end

    always #5 clk = ~clk;

    // Glitch injection at t=120
    initial begin
        #120;
        force uut.count = 4'b1111;
        #2;
        release uut.count;
    end
endmodule

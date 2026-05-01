module up_down_counter_4bit (
    input wire clk,
    input wire rst_n,
    input wire en,
    input wire up,
    output reg [3:0] count,
    output reg overflow
);

    reg [3:0] next_count;
    reg next_overflow;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'b0000;
            overflow <= 1'b0;
        end else if (en) begin
            count <= next_count;
            overflow <= next_overflow;
        end
    end

    always @(*) begin
        if (up) begin
            if (count == 4'b1111) begin
                next_count = 4'b0000;
                next_overflow = 1'b1;
            end else begin
                next_count = count + 1;
                next_overflow = 1'b0;
            end
        end else begin // down
            if (count == 4'b0000) begin
                next_count = 4'b1111;
                next_overflow = 1'b1;
            end else begin
                next_count = count - 1;
                next_overflow = 1'b0;
            end
        end
    end

endmodule
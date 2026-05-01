module cla_adder_8bit (
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire       cin,
    input  wire       clk,
    input  wire       rst_n,
    output wire [7:0] sum,
    output wire       cout
);

    // Intermediate signals for carry lookahead logic
    wire [7:0] p; // Propagate signal
    wire [7:0] g; // Generate signal
    wire [7:0] c; // Carry signal

    // Calculate propagate (p) and generate (g) signals for each bit
    assign p[0] = a[0] ^ b[0];
    assign g[0] = a[0] & b[0];
    assign p[1] = a[1] ^ b[1];
    assign g[1] = a[1] & b[1];
    assign p[2] = a[2] ^ b[2];
    assign g[2] = a[2] & b[2];
    assign p[3] = a[3] ^ b[3];
    assign g[3] = a[3] & b[3];
    assign p[4] = a[4] ^ b[4];
    assign g[4] = a[4] & b[4];
    assign p[5] = a[5] ^ b[5];
    assign g[5] = a[5] & b[5];
    assign p[6] = a[6] ^ b[6];
    assign g[6] = a[6] & b[6];
    assign p[7] = a[7] ^ b[7];
    assign g[7] = a[7] & b[7];

    // Calculate carry signals using carry lookahead logic
    // c[0] is the initial carry-in
    assign c[0] = cin;
    // c[1] = g[0] | (p[0] & c[0])
    assign c[1] = g[0] | (p[0] & c[0]);
    // c[2] = g[1] | (p[1] & c[1])
    assign c[2] = g[1] | (p[1] & c[1]);
    // c[3] = g[2] | (p[2] & c[2])
    assign c[3] = g[2] | (p[2] & c[2]);
    // c[4] = g[3] | (p[3] & c[3])
    assign c[4] = g[3] | (p[3] & c[3]);
    // c[5] = g[4] | (p[4] & c[4])
    assign c[5] = g[4] | (p[4] & c[4]);
    // c[6] = g[5] | (p[5] & c[5])
    assign c[6] = g[5] | (p[5] & c[5]);
    // c[7] = g[6] | (p[6] & c[6])
    assign c[7] = g[6] | (p[6] & c[6]);
    // c[8] (cout) = g[7] | (p[7] & c[7])
    assign cout = g[7] | (p[7] & c[7]);

    // Calculate sum bits: sum[i] = p[i] ^ c[i]
    wire [7:0] sum_unregistered;
    assign sum_unregistered[0] = p[0] ^ c[0];
    assign sum_unregistered[1] = p[1] ^ c[1];
    assign sum_unregistered[2] = p[2] ^ c[2];
    assign sum_unregistered[3] = p[3] ^ c[3];
    assign sum_unregistered[4] = p[4] ^ c[4];
    assign sum_unregistered[5] = p[5] ^ c[5];
    assign sum_unregistered[6] = p[6] ^ c[6];
    assign sum_unregistered[7] = p[7] ^ c[7];

    // Registered output
    reg [7:0] sum_reg;
    reg       cout_reg;

    assign sum = sum_reg;
    assign cout = cout_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum_reg <= 8'b0;
            cout_reg <= 1'b0;
        end else begin
            sum_reg <= sum_unregistered;
            cout_reg <= cout; // Connect the actual carry out to the registered output
        end
    end

endmodule
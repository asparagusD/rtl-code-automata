module carry_lookahead_adder_8bit_registered (
    input  logic        clk,
    input  logic        rst_n, // Active low synchronous reset
    input  logic [7:0]  A,
    input  logic [7:0]  B,
    input  logic        carry_in,
    output logic [7:0]  sum,
    output logic        carry_out
);

    logic [7:0] P; // Propagate terms (P_i = A_i ^ B_i)
    logic [7:0] G; // Generate terms (G_i = A_i & B_i)
    logic [8:0] C; // Carries, C[0] is carry_in, C[8] is carry_out
    logic [7:0] sum_unreg;
    logic       carry_out_unreg;

    // 1. Calculate P and G terms (combinational logic)
    genvar i;
    generate
        for (i = 0; i < 8; i = i + 1) begin : gen_pg_terms
            assign P[i] = A[i] ^ B[i];
            assign G[i] = A[i] & B[i];
        end
    endgenerate

    // 2. Calculate carries (combinational lookahead logic)
    assign C[0] = carry_in;

    // C[k+1] = G[k] | (P[k] & G[k-1]) | (P[k] & P[k-1] & G[k-2]) | ... | (P[k] & ... & P[0] & C[0])
    assign C[1] = G[0] | (P[0] & C[0]);
    assign C[2] = G[1] | (P[1] & G[0]) | (P[1] & P[0] & C[0]);
    assign C[3] = G[2] | (P[2] & G[1]) | (P[2] & P[1] & G[0]) | (P[2] & P[1] & P[0] & C[0]);
    assign C[4] = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]) | (P[3] & P[2] & P[1] & P[0] & C[0]);
    assign C[5] = G[4] | (P[4] & G[3]) | (P[4] & P[3] & G[2]) | (P[4] & P[3] & P[2] & G[1]) | (P[4] & P[3] & P[2] & P[1] & G[0]) | (P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);
    assign C[6] = G[5] | (P[5] & G[4]) | (P[5] & P[4] & G[3]) | (P[5] & P[4] & P[3] & G[2]) | (P[5] & P[4] & P[3] & P[2] & G[1]) | (P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) | (P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);
    assign C[7] = G[6] | (P[6] & G[5]) | (P[6] & P[5] & G[4]) | (P[6] & P[5] & P[4] & G[3]) | (P[6] & P[5] & P[4] & P[3] & G[2]) | (P[6] & P[5] & P[4] & P[3] & P[2] & G[1]) | (P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) | (P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);
    assign C[8] = G[7] | (P[7] & G[6]) | (P[7] & P[6] & G[5]) | (P[7] & P[6] & P[5] & G[4]) | (P[7] & P[6] & P[5] & P[4] & G[3]) | (P[7] & P[6] & P[5] & P[4] & P[3] & G[2]) | (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & G[1]) | (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) | (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);

    // 3. Calculate sum (combinational logic: S_i = P_i ^ C_i) - Unrolled for debugging
    assign sum_unreg[0] = P[0] ^ C[0];
    assign sum_unreg[1] = P[1] ^ C[1];
    assign sum_unreg[2] = P[2] ^ C[2];
    assign sum_unreg[3] = P[3] ^ C[3];
    assign sum_unreg[4] = P[4] ^ C[4];
    assign sum_unreg[5] = P[5] ^ C[5];
    assign sum_unreg[6] = P[6] ^ C[6];
    assign sum_unreg[7] = P[7] ^ C[7];

    // 4. Assign the final carry_out (combinational)
    assign carry_out_unreg = C[8];

    // 5. Register outputs with synchronous reset
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sum       <= 8'b0;      // Reset sum to all zeros (fixed '0 to 8'b0)
            carry_out <= 1'b0;    // Reset carry_out to zero
        end else begin
            sum       <= sum_unreg;
            carry_out <= carry_out_unreg;
        end
    end

endmodule
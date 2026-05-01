module cla_8bit_reg (
    input wire clk,
    input wire rst_n,
    input wire [7:0] A,
    input wire [7:0] B,
    input wire cin,
    output reg [7:0] sum,
    output reg cout
);

// P (Propagate) and G (Generate) signals for each bit
wire [7:0] P;
wire [7:0] G;

// Carries: C[0] is cin, C[1] to C[7] are carries into bit stages 1 to 7.
// C[8] is the final carry-out.
wire [8:0] C; 

// Combinational Sum for registering
wire [7:0] S_comb;

// Generate P and G for each bit
assign P = A ^ B;
assign G = A & B;

// C[0] is the input carry
assign C[0] = cin;

// Calculate carry lookahead for each bit position
// C[i] is the carry into bit position i
assign C[1] = G[0] | (P[0] & C[0]);

assign C[2] = G[1] |
              (P[1] & G[0]) |
              (P[1] & P[0] & C[0]);

assign C[3] = G[2] |
              (P[2] & G[1]) |
              (P[2] & P[1] & G[0]) |
              (P[2] & P[1] & P[0] & C[0]);

assign C[4] = G[3] |
              (P[3] & G[2]) |
              (P[3] & P[2] & G[1]) |
              (P[3] & P[2] & P[1] & G[0]) |
              (P[3] & P[2] & P[1] & P[0] & C[0]);

assign C[5] = G[4] |
              (P[4] & G[3]) |
              (P[4] & P[3] & G[2]) |
              (P[4] & P[3] & P[2] & G[1]) |
              (P[4] & P[3] & P[2] & P[1] & G[0]) |
              (P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);

assign C[6] = G[5] |
              (P[5] & G[4]) |
              (P[5] & P[4] & G[3]) |
              (P[5] & P[4] & P[3] & G[2]) |
              (P[5] & P[4] & P[3] & P[2] & G[1]) |
              (P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) |
              (P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);

assign C[7] = G[6] |
              (P[6] & G[5]) |
              (P[6] & P[5] & G[4]) |
              (P[6] & P[5] & P[4] & G[3]) |
              (P[6] & P[5] & P[4] & P[3] & G[2]) |
              (P[6] & P[5] & P[4] & P[3] & P[2] & G[1]) |
              (P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) |
              (P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);

// C[8] is the final carry out
assign C[8] = G[7] |
              (P[7] & G[6]) |
              (P[7] & P[6] & G[5]) |
              (P[7] & P[6] & P[5] & G[4]) |
              (P[7] & P[6] & P[5] & P[4] & G[3]) |
              (P[7] & P[6] & P[5] & P[4] & P[3] & G[2]) |
              (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & G[1]) |
              (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & G[0]) |
              (P[7] & P[6] & P[5] & P[4] & P[3] & P[2] & P[1] & P[0] & C[0]);

// Calculate combinational sum bits
assign S_comb[0] = P[0] ^ C[0];
assign S_comb[1] = P[1] ^ C[1];
assign S_comb[2] = P[2] ^ C[2];
assign S_comb[3] = P[3] ^ C[3];
assign S_comb[4] = P[4] ^ C[4];
assign S_comb[5] = P[5] ^ C[5];
assign S_comb[6] = P[6] ^ C[6];
assign S_comb[7] = P[7] ^ C[7];

// Register the sum and carry out
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        sum <= 8'b0;
        cout <= 1'b0;
    end else begin
        sum <= S_comb;
        cout <= C[8];
    end
end

endmodule
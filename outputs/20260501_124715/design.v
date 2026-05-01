module barrel_shifter_8bit (
  input wire [7:0] data_in,
  input wire [2:0] shift_amount, // Needs 3 bits for shift amounts 0-7 for an 8-bit shifter
  input wire       shift_left, // 1 for left shift, 0 for right shift
  output wire [7:0] data_out
);

  // Internal signals to hold shifted data at each stage
  wire [7:0] shifted_data_0;
  wire [7:0] shifted_data_1;
  wire [7:0] shifted_data_2;

  // Stage 0: Shift by 1 or 0 bits
  assign shifted_data_0 = shift_left ?
                          (shift_amount[0] ? (data_in << 1) : data_in) :
                          (shift_amount[0] ? (data_in >> 1) : data_in);

  // Stage 1: Shift by 2 or 0 bits
  assign shifted_data_1 = shift_left ?
                          (shift_amount[1] ? (shifted_data_0 << 2) : shifted_data_0) :
                          (shift_amount[1] ? (shifted_data_0 >> 2) : shifted_data_0);

  // Stage 2: Shift by 4 or 0 bits
  assign shifted_data_2 = shift_left ?
                          (shift_amount[2] ? (shifted_data_1 << 4) : shifted_data_1) :
                          (shift_amount[2] ? (shifted_data_1 >> 4) : shifted_data_1);

  // The final output is the result after all stages
  assign data_out = shifted_data_2;

endmodule
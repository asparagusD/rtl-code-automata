module barrel_shifter_8bit (
  input  wire [7:0] data_in,
  input  wire [2:0] shift_amount,
  input  wire       direction, // 0 for logical left, 1 for logical right
  output reg [7:0] data_out // Changed from wire to reg
);

  wire [7:0] shifted_left_0;
  wire [7:0] shifted_left_1;
  wire [7:0] shifted_left_2;
  wire [7:0] shifted_left_3;
  wire [7:0] shifted_left_4;
  wire [7:0] shifted_left_5;
  wire [7:0] shifted_left_6;

  wire [7:0] shifted_right_0;
  wire [7:0] shifted_right_1;
  wire [7:0] shifted_right_2;
  wire [7:0] shifted_right_3;
  wire [7:0] shifted_right_4;
  wire [7:0] shifted_right_5;
  wire [7:0] shifted_right_6;

  // Barrel shifter for left shifts
  assign shifted_left_0 = data_in << 1;
  assign shifted_left_1 = shifted_left_0 << 1;
  assign shifted_left_2 = shifted_left_1 << 1;
  assign shifted_left_3 = shifted_left_2 << 1;
  assign shifted_left_4 = shifted_left_3 << 1;
  assign shifted_left_5 = shifted_left_4 << 1;
  assign shifted_left_6 = shifted_left_5 << 1;

  // Barrel shifter for right shifts
  assign shifted_right_0 = data_in >> 1;
  assign shifted_right_1 = shifted_right_0 >> 1;
  assign shifted_right_2 = shifted_right_1 >> 1;
  assign shifted_right_3 = shifted_right_2 >> 1;
  assign shifted_right_4 = shifted_right_3 >> 1;
  assign shifted_right_5 = shifted_right_4 >> 1;
  assign shifted_right_6 = shifted_right_5 >> 1;

  // Select output based on shift amount and direction
  always @(*) begin
    casez (shift_amount)
      3'b000: data_out = data_in;
      3'b001: begin
        if (direction) data_out = shifted_right_0;
        else data_out = shifted_left_0;
      end
      3'b010: begin
        if (direction) data_out = shifted_right_1;
        else data_out = shifted_left_1;
      end
      3'b011: begin
        if (direction) data_out = shifted_right_2;
        else data_out = shifted_left_2;
      end
      3'b100: begin
        if (direction) data_out = shifted_right_3;
        else data_out = shifted_left_3;
      end
      3'b101: begin
        if (direction) data_out = shifted_right_4;
        else data_out = shifted_left_4;
      end
      3'b110: begin
        if (direction) data_out = shifted_right_5;
        else data_out = shifted_left_5;
      end
      3'b111: begin
        if (direction) data_out = shifted_right_6;
        else data_out = shifted_left_6;
      end
      default: data_out = data_in; // Default to no shift
    endcase
  end

endmodule

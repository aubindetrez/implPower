// IEEE 754 floating point adder
// This implementation is based on the Vanilla Floating Point Addition algorithm described by
// P.M.Seidel and G.Even in "On the Design of Fast IEEE Floating-Point Adders"
// Warning: This is a slow adder implementation
// It consists in 9 steps 

// TODO benchmark the two stage shift used in picorv32: https://github.com/YosysHQ/picorv32/blob/master/picorv32.v#L1824-L1847

module fpu_adder_vanilla #(
    parameter integer p_max_shift = 55; // >= 55, limit the maximum significand shift
) (
    logic i_clk,
    logic i_rst,
    logic i_en,

    logic [0:63] i_operand_a,
    /* 
     * S, E[10:0], F[0:52]
     * | 0 | 1..11 | 12..63 |
     * | S |   E   |FRACTION|
     * S is the sign
     * E is the exponent + 1023 (bias)
     * Significant F is {1,EXP} for normalized numbers, [1, 2)
     * and {0,EXP} for denormalized numbers
     * Examples:
     * 64'h3FF0_0000_0000_0001 is 2**0 * (1 + 2**-52) ~= 1.0000000000000002
     * 64'h3FF0_0000_0000_0002 is 2**0 * (1 + 2**-51) ~= 1.0000000000000004
     * 64'h4000_0000_0000_0000 is 2**1 * 1 = 2
     * 64'hC000_0000_0000_0000 is 2**1 * 1 = -2
     * 64'h0000_0000_0000_0000 is +0
     * 64'h8000_0000_0000_0000 is -0
     * 64'h7FF0_0000_0000_0000 is +inf
     * 64'hFFF0_0000_0000_0000 is -inf
     * 64'h7FF0_0000_0000_0001 is sNaN
     * 64'h7FF8_0000_0000_0001 is qNaN
     * 64'h7FFF_FFFF_FFFF_FFFF is NAN
     */
    logic [0:63] i_operand_b,
    logic sop, // 1'b1 -> substraction, 1'b0 -> addition
    logic [0:3] rounding_mode, // IEEE rounding mode
    /*
     * 00 Round to Nearest
     * 01 Round toward zero
     * 10 Round toward + infinity
     * 11 Round toward - infinity
     */
    logic [0:63] o_result,
);

logic sa; // Sign of i_operand_a, 1-bit
logic [0:10] ea; // Exponent of i_operand_a, 11-bit
logic [0:53] fa; // Significant of i_operand_a, 53-bit
logic inf_a; // 1'b1 if i_operand_a is infinity
assign sa = i_operand_a[0];
assign ea = i_operand_a[1:11];
assign fa = {1'b1, i_operand_a[12:63]}; // Normalized number according-Power ISA Book I Section 4.3.1
logic fa_null; // 1'b1 if fa is null
assign fa_null = (fa=={1'b1, 52'b0})? 1'b1: 1'b0;
assign inf_a = (ea == 2047 && fa_null == 1'b1)? 1'b1: 1'b0; // See Power ISA Book I, Section 4.3.2
assign nan_a = (ea == 2047 && fa_null == 1'b0)? 1'b1: 1'b0;

logic sb; // Sign of i_operand_b, 1-bit
logic [0:10] eb; // Exponent of i_operand_b, 11-bit
logic [0:53] fb; // Significant of i_operand_b, 53-bit
assign sb = i_operand_b[0];
assign eb = i_operand_b[1:11];
assign fb = {1'b1, i_operand_b[12:63]}; // Normalized number like fa
logic fb_null; // 1'b1 if fa is null
assign fb_null = (fb=={1'b1, 52'b0})? 1'b1: 1'b0;
assign inf_b = (eb == 2047 && fb_null == 1'b1)? 1'b1: 1'b0; // like inf_a
assign nan_b = (eb == 2047 && fb_null == 1'b0)? 1'b1: 1'b0;

logic seff;
assign seff = sa ^ sb ^ sop; // seff=1'b1 -> effective substraction, else effective addition

/*           EXPONENT SUBTRACTION      */
logic [10:0] e_diff; // exponent difference
assign e_diff = ea - eb;
logic diff_pos; // 1'b1 if the exponent difference (e_diff) is >= 0
assign diff_pos = e_diff[10]; // Sign bit from the exponent difference

/*           OPERAND SWAPPING          */
logic sl; // sign of the large operand
logic [10:0] el; // Exponent of the large operand
logic [0:52] fl; // Significant of the large operand
assign sl = (diff_pos == 1'b1)? sa : sb ^ sop;
assign el = (diff_pos == 1'b1)? ea : eb;
assign fl = (diff_pos == 1'b1)? fa : fb;

logic ss; // sign of the small operand
logic [10:0] es; // Exponent of the small operand
logic [0:52] fs; // Significant of the small operand
assign ss = (diff_pos == 1'b1)? sb ^ sop : sa;
assign es = (diff_pos == 1'b1)? eb : ea;
assign fs = (diff_pos == 1'b1)? fb : fa;

/*           ALIGNMENT SHIFT           */
logic [10:0] abs_e_diff; // absolute value of e_diff
assign abs_e_diff = (e_diff[0]==1'b1)? -e_diff : e_diff;

logic [TODO] shift_lim; // limitation of the laignment shift amount
assign shift_lim = (p_max_shift < abs_e_diff)? p_max_shift: abs_e_diff; // min{p_max_shift, abs(e_diff)}
// Note: Delay is logarithmic in the significand's length

// Alignment shift of fs
logic [0:52] fsa; // aligned fs
assign fsa = fs >> shift_lim;
// TODO endode the fhist amount in pairs and use a 4:1 mux to redure delay to 5 LL

/*           SIGNIFICAND NEGATION      */
logic [0:52] fsan; // fs, aligned and negated
assign fsan = (seff==1'b1)? -fsa: fsa;

/*           SIGNIFICAND ADDITION      */
logic [0:52] fsum; // sum of the significants
assign fsum = fl + fsan;
// Note: Delay is logarithmic in the significand's length

/*           CONVERSION                */
logic [0:52] abs_fsum; // absolution value of fsum
assign abs_fsum = (fsum[0]==1'b1)? -fsum: fsum;
logic s; // sign of the resulting significant
assign s = sl ^ fsum[0]; // sl xor (fsum < 0)
// Note: Delay is logarithmic in the significand's length

/*           NORMALISATION             */
logic [0:52] n_fsum; // normalized abs_fsum (range [1, 4) )
// TODO
// Note: Delay is logarithmic in the significand's length

/*  ROUNDING AND POST-NORMALIZATION   */
// TODO
// Note: Delay is logarithmic in the significand's length

/*           EXPONENT                  */
// TODO Compute result's exponent

endmodule

# Reference / Non-submission test code
class MyPlayer(BasePlayer):
    def __init__(self, color, opponent_color=None):
        if opponent_color is None:
            opponent_color = Cell.WHITE if color == Cell.BLACK else Cell.BLACK
        super().__init__(color)
        self.color = color
        self.opponent_color = opponent_color

    def _board_to_bits(self, board) -> tuple[int, int]:
        black_bits = 0
        white_bits = 0
        for r in range(8):
            for c in range(8):
                cell = board[r][c]
                idx = r * 8 + c
                if cell == Cell.BLACK or cell == 1:
                    black_bits |= 1 << idx
                elif cell == Cell.WHITE or cell == 2:
                    white_bits |= 1 << idx
        return black_bits, white_bits

    def _legal_moves_bits(self, my_bits: int, opp_bits: int) -> int:
        empty = ~(my_bits | opp_bits) & 0xFFFFFFFFFFFFFFFF
        mask = opp_bits & 0x7E7E7E7E7E7E7E7E
        legal = 0

        # Right
        t = (my_bits >> 1) & mask
        t |= (t >> 1) & mask
        t |= (t >> 1) & mask
        t |= (t >> 1) & mask
        t |= (t >> 1) & mask
        t |= (t >> 1) & mask
        legal |= (t >> 1) & empty

        # Left
        t = (my_bits << 1) & mask
        t |= (t << 1) & mask
        t |= (t << 1) & mask
        t |= (t << 1) & mask
        t |= (t << 1) & mask
        t |= (t << 1) & mask
        legal |= (t << 1) & empty

        # Down
        t = (my_bits >> 8) & opp_bits
        t |= (t >> 8) & opp_bits
        t |= (t >> 8) & opp_bits
        t |= (t >> 8) & opp_bits
        t |= (t >> 8) & opp_bits
        t |= (t >> 8) & opp_bits
        legal |= (t >> 8) & empty

        # Up
        t = (my_bits << 8) & opp_bits
        t |= (t << 8) & opp_bits
        t |= (t << 8) & opp_bits
        t |= (t << 8) & opp_bits
        t |= (t << 8) & opp_bits
        t |= (t << 8) & opp_bits
        legal |= (t << 8) & empty

        # Down-Right
        t = (my_bits >> 9) & mask
        t |= (t >> 9) & mask
        t |= (t >> 9) & mask
        t |= (t >> 9) & mask
        t |= (t >> 9) & mask
        t |= (t >> 9) & mask
        legal |= (t >> 9) & empty

        # Up-Left
        t = (my_bits << 9) & mask
        t |= (t << 9) & mask
        t |= (t << 9) & mask
        t |= (t << 9) & mask
        t |= (t << 9) & mask
        t |= (t << 9) & mask
        legal |= (t << 9) & empty

        # Down-Left
        t = (my_bits >> 7) & mask
        t |= (t >> 7) & mask
        t |= (t >> 7) & mask
        t |= (t >> 7) & mask
        t |= (t >> 7) & mask
        t |= (t >> 7) & mask
        legal |= (t >> 7) & empty

        # Up-Right
        t = (my_bits << 7) & mask
        t |= (t << 7) & mask
        t |= (t << 7) & mask
        t |= (t << 7) & mask
        t |= (t << 7) & mask
        t |= (t << 7) & mask
        legal |= (t << 7) & empty

        return legal

    def next_move(self, board):
        black_bits, white_bits = self._board_to_bits(board)
        is_black = (self.color == Cell.BLACK or self.color == 1)
        my_bits = black_bits if is_black else white_bits
        opp_bits = white_bits if is_black else black_bits
        legal_mask = self._legal_moves_bits(my_bits, opp_bits)
        if legal_mask:
            lsb = legal_mask & -legal_mask
            idx = lsb.bit_length() - 1
            return (idx // 8, idx % 8)

        for r in range(8):
            for c in range(8):
                if board[r][c] == Cell.EMPTY or board[r][c] == 0:
                    return (r, c)
        return (0, 0)


    @staticmethod
    def _evaluate_patterns_func_static(keys, tables, bias):
        return (
            bias
            + tables[0][keys[0]]
            + tables[0][keys[1]]
            + tables[0][keys[2]]
            + tables[0][keys[3]]
            + tables[1][keys[4]]
            + tables[1][keys[5]]
            + tables[1][keys[6]]
            + tables[1][keys[7]]
            + tables[1][keys[8]]
            + tables[1][keys[9]]
            + tables[1][keys[10]]
            + tables[1][keys[11]]
            + tables[2][keys[12]]
            + tables[2][keys[13]]
            + tables[2][keys[14]]
            + tables[2][keys[15]]
            + tables[2][keys[16]]
            + tables[2][keys[17]]
            + tables[2][keys[18]]
            + tables[2][keys[19]]
            + tables[3][keys[20]]
            + tables[3][keys[21]]
            + tables[3][keys[22]]
            + tables[3][keys[23]]
            + tables[3][keys[24]]
            + tables[3][keys[25]]
            + tables[3][keys[26]]
            + tables[3][keys[27]]
            + tables[4][keys[28]]
            + tables[4][keys[29]]
            + tables[4][keys[30]]
            + tables[4][keys[31]]
            + tables[4][keys[32]]
            + tables[4][keys[33]]
            + tables[4][keys[34]]
            + tables[4][keys[35]]
            + tables[5][keys[36]]
            + tables[5][keys[37]]
            + tables[5][keys[38]]
            + tables[5][keys[39]]
            + tables[5][keys[40]]
            + tables[5][keys[41]]
            + tables[5][keys[42]]
            + tables[5][keys[43]]
            + tables[6][keys[44]]
            + tables[6][keys[45]]
            + tables[6][keys[46]]
            + tables[6][keys[47]]
            + tables[6][keys[48]]
            + tables[6][keys[49]]
            + tables[6][keys[50]]
            + tables[6][keys[51]]
            + tables[7][keys[52]]
            + tables[7][keys[53]]
            + tables[7][keys[54]]
            + tables[7][keys[55]]
            + tables[7][keys[56]]
            + tables[7][keys[57]]
            + tables[7][keys[58]]
            + tables[7][keys[59]]
        )

    @staticmethod
    def _update_pos_black_0(keys):
        keys[0] -= 4374
        keys[2] -= 2
        keys[28] -= 4374
        keys[29] -= 4374
        keys[32] -= 2
        keys[33] -= 2
        keys[36] -= 13122
        keys[37] -= 13122
        keys[40] -= 6
        keys[41] -= 6
        keys[44] -= 39366
        keys[45] -= 39366
        keys[52] -= 13122
        keys[56] -= 2
    @staticmethod
    def _update_pos_black_1(keys):
        keys[4] -= 1458
        keys[8] -= 2
        keys[28] -= 1458
        keys[32] -= 6
        keys[36] -= 4374
        keys[40] -= 18
        keys[44] -= 13122
        keys[45] -= 486
        keys[52] -= 4374
        keys[56] -= 6
    @staticmethod
    def _update_pos_black_2(keys):
        keys[12] -= 486
        keys[16] -= 2
        keys[28] -= 486
        keys[32] -= 18
        keys[36] -= 1458
        keys[40] -= 54
        keys[44] -= 4374
        keys[45] -= 18
        keys[52] -= 1458
        keys[56] -= 18
    @staticmethod
    def _update_pos_black_3(keys):
        keys[20] -= 162
        keys[24] -= 2
        keys[28] -= 162
        keys[32] -= 54
        keys[36] -= 486
        keys[40] -= 162
        keys[44] -= 1458
        keys[45] -= 2
    @staticmethod
    def _update_pos_black_4(keys):
        keys[22] -= 162
        keys[26] -= 2
        keys[28] -= 54
        keys[32] -= 162
        keys[36] -= 162
        keys[40] -= 486
        keys[46] -= 1458
        keys[47] -= 2
    @staticmethod
    def _update_pos_black_5(keys):
        keys[14] -= 486
        keys[18] -= 2
        keys[28] -= 18
        keys[32] -= 486
        keys[36] -= 54
        keys[40] -= 1458
        keys[46] -= 4374
        keys[47] -= 18
        keys[53] -= 1458
        keys[57] -= 18
    @staticmethod
    def _update_pos_black_6(keys):
        keys[6] -= 1458
        keys[10] -= 2
        keys[28] -= 6
        keys[32] -= 1458
        keys[36] -= 18
        keys[40] -= 4374
        keys[46] -= 13122
        keys[47] -= 486
        keys[53] -= 4374
        keys[57] -= 6
    @staticmethod
    def _update_pos_black_7(keys):
        keys[1] -= 4374
        keys[3] -= 2
        keys[28] -= 2
        keys[31] -= 4374
        keys[32] -= 4374
        keys[35] -= 2
        keys[36] -= 6
        keys[39] -= 6
        keys[40] -= 13122
        keys[43] -= 13122
        keys[46] -= 39366
        keys[47] -= 39366
        keys[53] -= 13122
        keys[57] -= 2
    @staticmethod
    def _update_pos_black_8(keys):
        keys[5] -= 1458
        keys[9] -= 2
        keys[29] -= 1458
        keys[33] -= 6
        keys[37] -= 4374
        keys[41] -= 18
        keys[44] -= 486
        keys[45] -= 13122
        keys[52] -= 486
        keys[56] -= 54
    @staticmethod
    def _update_pos_black_9(keys):
        keys[0] -= 1458
        keys[2] -= 6
        keys[36] -= 39366
        keys[37] -= 39366
        keys[40] -= 2
        keys[41] -= 2
        keys[44] -= 162
        keys[45] -= 162
        keys[52] -= 162
        keys[56] -= 162
    @staticmethod
    def _update_pos_black_10(keys):
        keys[4] -= 486
        keys[8] -= 6
        keys[44] -= 54
        keys[45] -= 6
        keys[52] -= 54
        keys[56] -= 486
    @staticmethod
    def _update_pos_black_11(keys):
        keys[12] -= 162
        keys[16] -= 6
        keys[22] -= 54
        keys[26] -= 6
    @staticmethod
    def _update_pos_black_12(keys):
        keys[14] -= 162
        keys[18] -= 6
        keys[20] -= 54
        keys[24] -= 6
    @staticmethod
    def _update_pos_black_13(keys):
        keys[6] -= 486
        keys[10] -= 6
        keys[46] -= 54
        keys[47] -= 6
        keys[53] -= 54
        keys[57] -= 486
    @staticmethod
    def _update_pos_black_14(keys):
        keys[1] -= 1458
        keys[3] -= 6
        keys[36] -= 2
        keys[39] -= 2
        keys[40] -= 39366
        keys[43] -= 39366
        keys[46] -= 162
        keys[47] -= 162
        keys[53] -= 162
        keys[57] -= 162
    @staticmethod
    def _update_pos_black_15(keys):
        keys[7] -= 1458
        keys[11] -= 2
        keys[31] -= 1458
        keys[35] -= 6
        keys[39] -= 18
        keys[43] -= 4374
        keys[46] -= 486
        keys[47] -= 13122
        keys[53] -= 486
        keys[57] -= 54
    @staticmethod
    def _update_pos_black_16(keys):
        keys[13] -= 486
        keys[17] -= 2
        keys[29] -= 486
        keys[33] -= 18
        keys[37] -= 1458
        keys[41] -= 54
        keys[44] -= 18
        keys[45] -= 4374
        keys[52] -= 18
        keys[56] -= 1458
    @staticmethod
    def _update_pos_black_17(keys):
        keys[5] -= 486
        keys[9] -= 6
        keys[44] -= 6
        keys[45] -= 54
        keys[52] -= 6
        keys[56] -= 4374
    @staticmethod
    def _update_pos_black_18(keys):
        keys[0] -= 486
        keys[2] -= 18
        keys[22] -= 18
        keys[26] -= 18
        keys[52] -= 2
        keys[56] -= 13122
    @staticmethod
    def _update_pos_black_19(keys):
        keys[4] -= 162
        keys[8] -= 18
        keys[14] -= 54
        keys[18] -= 18
    @staticmethod
    def _update_pos_black_20(keys):
        keys[6] -= 162
        keys[10] -= 18
        keys[12] -= 54
        keys[16] -= 18
    @staticmethod
    def _update_pos_black_21(keys):
        keys[1] -= 486
        keys[3] -= 18
        keys[20] -= 18
        keys[24] -= 18
        keys[53] -= 2
        keys[57] -= 13122
    @staticmethod
    def _update_pos_black_22(keys):
        keys[7] -= 486
        keys[11] -= 6
        keys[46] -= 6
        keys[47] -= 54
        keys[53] -= 6
        keys[57] -= 4374
    @staticmethod
    def _update_pos_black_23(keys):
        keys[15] -= 486
        keys[19] -= 2
        keys[31] -= 486
        keys[35] -= 18
        keys[39] -= 54
        keys[43] -= 1458
        keys[46] -= 18
        keys[47] -= 4374
        keys[53] -= 18
        keys[57] -= 1458
    @staticmethod
    def _update_pos_black_24(keys):
        keys[21] -= 162
        keys[25] -= 2
        keys[29] -= 162
        keys[33] -= 54
        keys[37] -= 486
        keys[41] -= 162
        keys[44] -= 2
        keys[45] -= 1458
    @staticmethod
    def _update_pos_black_25(keys):
        keys[13] -= 162
        keys[17] -= 6
        keys[22] -= 6
        keys[26] -= 54
    @staticmethod
    def _update_pos_black_26(keys):
        keys[5] -= 162
        keys[9] -= 18
        keys[14] -= 18
        keys[18] -= 54
    @staticmethod
    def _update_pos_black_27(keys):
        keys[0] -= 162
        keys[2] -= 54
        keys[6] -= 54
        keys[10] -= 54
    @staticmethod
    def _update_pos_black_28(keys):
        keys[1] -= 162
        keys[3] -= 54
        keys[4] -= 54
        keys[8] -= 54
    @staticmethod
    def _update_pos_black_29(keys):
        keys[7] -= 162
        keys[11] -= 18
        keys[12] -= 18
        keys[16] -= 54
    @staticmethod
    def _update_pos_black_30(keys):
        keys[15] -= 162
        keys[19] -= 6
        keys[20] -= 6
        keys[24] -= 54
    @staticmethod
    def _update_pos_black_31(keys):
        keys[23] -= 162
        keys[27] -= 2
        keys[31] -= 162
        keys[35] -= 54
        keys[39] -= 162
        keys[43] -= 486
        keys[46] -= 2
        keys[47] -= 1458
    @staticmethod
    def _update_pos_black_32(keys):
        keys[22] -= 2
        keys[26] -= 162
        keys[29] -= 54
        keys[33] -= 162
        keys[37] -= 162
        keys[41] -= 486
        keys[50] -= 2
        keys[51] -= 1458
    @staticmethod
    def _update_pos_black_33(keys):
        keys[14] -= 6
        keys[18] -= 162
        keys[21] -= 54
        keys[25] -= 6
    @staticmethod
    def _update_pos_black_34(keys):
        keys[6] -= 18
        keys[10] -= 162
        keys[13] -= 54
        keys[17] -= 18
    @staticmethod
    def _update_pos_black_35(keys):
        keys[1] -= 54
        keys[3] -= 162
        keys[5] -= 54
        keys[9] -= 54
    @staticmethod
    def _update_pos_black_36(keys):
        keys[0] -= 54
        keys[2] -= 162
        keys[7] -= 54
        keys[11] -= 54
    @staticmethod
    def _update_pos_black_37(keys):
        keys[4] -= 18
        keys[8] -= 162
        keys[15] -= 54
        keys[19] -= 18
    @staticmethod
    def _update_pos_black_38(keys):
        keys[12] -= 6
        keys[16] -= 162
        keys[23] -= 54
        keys[27] -= 6
    @staticmethod
    def _update_pos_black_39(keys):
        keys[20] -= 2
        keys[24] -= 162
        keys[31] -= 54
        keys[35] -= 162
        keys[39] -= 486
        keys[43] -= 162
        keys[48] -= 2
        keys[49] -= 1458
    @staticmethod
    def _update_pos_black_40(keys):
        keys[14] -= 2
        keys[18] -= 486
        keys[29] -= 18
        keys[33] -= 486
        keys[37] -= 54
        keys[41] -= 1458
        keys[50] -= 18
        keys[51] -= 4374
        keys[54] -= 18
        keys[58] -= 1458
    @staticmethod
    def _update_pos_black_41(keys):
        keys[6] -= 6
        keys[10] -= 486
        keys[50] -= 6
        keys[51] -= 54
        keys[54] -= 6
        keys[58] -= 4374
    @staticmethod
    def _update_pos_black_42(keys):
        keys[1] -= 18
        keys[3] -= 486
        keys[21] -= 18
        keys[25] -= 18
        keys[54] -= 2
        keys[58] -= 13122
    @staticmethod
    def _update_pos_black_43(keys):
        keys[7] -= 18
        keys[11] -= 162
        keys[13] -= 18
        keys[17] -= 54
    @staticmethod
    def _update_pos_black_44(keys):
        keys[5] -= 18
        keys[9] -= 162
        keys[15] -= 18
        keys[19] -= 54
    @staticmethod
    def _update_pos_black_45(keys):
        keys[0] -= 18
        keys[2] -= 486
        keys[23] -= 18
        keys[27] -= 18
        keys[55] -= 2
        keys[59] -= 13122
    @staticmethod
    def _update_pos_black_46(keys):
        keys[4] -= 6
        keys[8] -= 486
        keys[48] -= 6
        keys[49] -= 54
        keys[55] -= 6
        keys[59] -= 4374
    @staticmethod
    def _update_pos_black_47(keys):
        keys[12] -= 2
        keys[16] -= 486
        keys[31] -= 18
        keys[35] -= 486
        keys[39] -= 1458
        keys[43] -= 54
        keys[48] -= 18
        keys[49] -= 4374
        keys[55] -= 18
        keys[59] -= 1458
    @staticmethod
    def _update_pos_black_48(keys):
        keys[6] -= 2
        keys[10] -= 1458
        keys[29] -= 6
        keys[33] -= 1458
        keys[37] -= 18
        keys[41] -= 4374
        keys[50] -= 486
        keys[51] -= 13122
        keys[54] -= 486
        keys[58] -= 54
    @staticmethod
    def _update_pos_black_49(keys):
        keys[1] -= 6
        keys[3] -= 1458
        keys[37] -= 2
        keys[38] -= 39366
        keys[41] -= 39366
        keys[42] -= 2
        keys[50] -= 162
        keys[51] -= 162
        keys[54] -= 162
        keys[58] -= 162
    @staticmethod
    def _update_pos_black_50(keys):
        keys[7] -= 6
        keys[11] -= 486
        keys[50] -= 54
        keys[51] -= 6
        keys[54] -= 54
        keys[58] -= 486
    @staticmethod
    def _update_pos_black_51(keys):
        keys[15] -= 6
        keys[19] -= 162
        keys[21] -= 6
        keys[25] -= 54
    @staticmethod
    def _update_pos_black_52(keys):
        keys[13] -= 6
        keys[17] -= 162
        keys[23] -= 6
        keys[27] -= 54
    @staticmethod
    def _update_pos_black_53(keys):
        keys[5] -= 6
        keys[9] -= 486
        keys[48] -= 54
        keys[49] -= 6
        keys[55] -= 54
        keys[59] -= 486
    @staticmethod
    def _update_pos_black_54(keys):
        keys[0] -= 6
        keys[2] -= 1458
        keys[38] -= 2
        keys[39] -= 39366
        keys[42] -= 39366
        keys[43] -= 2
        keys[48] -= 162
        keys[49] -= 162
        keys[55] -= 162
        keys[59] -= 162
    @staticmethod
    def _update_pos_black_55(keys):
        keys[4] -= 2
        keys[8] -= 1458
        keys[31] -= 6
        keys[35] -= 1458
        keys[39] -= 4374
        keys[43] -= 18
        keys[48] -= 486
        keys[49] -= 13122
        keys[55] -= 486
        keys[59] -= 54
    @staticmethod
    def _update_pos_black_56(keys):
        keys[1] -= 2
        keys[3] -= 4374
        keys[29] -= 2
        keys[30] -= 4374
        keys[33] -= 4374
        keys[34] -= 2
        keys[37] -= 6
        keys[38] -= 13122
        keys[41] -= 13122
        keys[42] -= 6
        keys[50] -= 39366
        keys[51] -= 39366
        keys[54] -= 13122
        keys[58] -= 2
    @staticmethod
    def _update_pos_black_57(keys):
        keys[7] -= 2
        keys[11] -= 1458
        keys[30] -= 1458
        keys[34] -= 6
        keys[38] -= 4374
        keys[42] -= 18
        keys[50] -= 13122
        keys[51] -= 486
        keys[54] -= 4374
        keys[58] -= 6
    @staticmethod
    def _update_pos_black_58(keys):
        keys[15] -= 2
        keys[19] -= 486
        keys[30] -= 486
        keys[34] -= 18
        keys[38] -= 1458
        keys[42] -= 54
        keys[50] -= 4374
        keys[51] -= 18
        keys[54] -= 1458
        keys[58] -= 18
    @staticmethod
    def _update_pos_black_59(keys):
        keys[23] -= 2
        keys[27] -= 162
        keys[30] -= 162
        keys[34] -= 54
        keys[38] -= 486
        keys[42] -= 162
        keys[50] -= 1458
        keys[51] -= 2
    @staticmethod
    def _update_pos_black_60(keys):
        keys[21] -= 2
        keys[25] -= 162
        keys[30] -= 54
        keys[34] -= 162
        keys[38] -= 162
        keys[42] -= 486
        keys[48] -= 1458
        keys[49] -= 2
    @staticmethod
    def _update_pos_black_61(keys):
        keys[13] -= 2
        keys[17] -= 486
        keys[30] -= 18
        keys[34] -= 486
        keys[38] -= 54
        keys[42] -= 1458
        keys[48] -= 4374
        keys[49] -= 18
        keys[55] -= 1458
        keys[59] -= 18
    @staticmethod
    def _update_pos_black_62(keys):
        keys[5] -= 2
        keys[9] -= 1458
        keys[30] -= 6
        keys[34] -= 1458
        keys[38] -= 18
        keys[42] -= 4374
        keys[48] -= 13122
        keys[49] -= 486
        keys[55] -= 4374
        keys[59] -= 6
    @staticmethod
    def _update_pos_black_63(keys):
        keys[0] -= 2
        keys[2] -= 4374
        keys[30] -= 2
        keys[31] -= 2
        keys[34] -= 4374
        keys[35] -= 4374
        keys[38] -= 6
        keys[39] -= 13122
        keys[42] -= 13122
        keys[43] -= 6
        keys[48] -= 39366
        keys[49] -= 39366
        keys[55] -= 13122
        keys[59] -= 2
    @staticmethod
    def _update_pos_white_0(keys):
        keys[0] -= 2187
        keys[2] -= 1
        keys[28] -= 2187
        keys[29] -= 2187
        keys[32] -= 1
        keys[33] -= 1
        keys[36] -= 6561
        keys[37] -= 6561
        keys[40] -= 3
        keys[41] -= 3
        keys[44] -= 19683
        keys[45] -= 19683
        keys[52] -= 6561
        keys[56] -= 1
    @staticmethod
    def _update_pos_white_1(keys):
        keys[4] -= 729
        keys[8] -= 1
        keys[28] -= 729
        keys[32] -= 3
        keys[36] -= 2187
        keys[40] -= 9
        keys[44] -= 6561
        keys[45] -= 243
        keys[52] -= 2187
        keys[56] -= 3
    @staticmethod
    def _update_pos_white_2(keys):
        keys[12] -= 243
        keys[16] -= 1
        keys[28] -= 243
        keys[32] -= 9
        keys[36] -= 729
        keys[40] -= 27
        keys[44] -= 2187
        keys[45] -= 9
        keys[52] -= 729
        keys[56] -= 9
    @staticmethod
    def _update_pos_white_3(keys):
        keys[20] -= 81
        keys[24] -= 1
        keys[28] -= 81
        keys[32] -= 27
        keys[36] -= 243
        keys[40] -= 81
        keys[44] -= 729
        keys[45] -= 1
    @staticmethod
    def _update_pos_white_4(keys):
        keys[22] -= 81
        keys[26] -= 1
        keys[28] -= 27
        keys[32] -= 81
        keys[36] -= 81
        keys[40] -= 243
        keys[46] -= 729
        keys[47] -= 1
    @staticmethod
    def _update_pos_white_5(keys):
        keys[14] -= 243
        keys[18] -= 1
        keys[28] -= 9
        keys[32] -= 243
        keys[36] -= 27
        keys[40] -= 729
        keys[46] -= 2187
        keys[47] -= 9
        keys[53] -= 729
        keys[57] -= 9
    @staticmethod
    def _update_pos_white_6(keys):
        keys[6] -= 729
        keys[10] -= 1
        keys[28] -= 3
        keys[32] -= 729
        keys[36] -= 9
        keys[40] -= 2187
        keys[46] -= 6561
        keys[47] -= 243
        keys[53] -= 2187
        keys[57] -= 3
    @staticmethod
    def _update_pos_white_7(keys):
        keys[1] -= 2187
        keys[3] -= 1
        keys[28] -= 1
        keys[31] -= 2187
        keys[32] -= 2187
        keys[35] -= 1
        keys[36] -= 3
        keys[39] -= 3
        keys[40] -= 6561
        keys[43] -= 6561
        keys[46] -= 19683
        keys[47] -= 19683
        keys[53] -= 6561
        keys[57] -= 1
    @staticmethod
    def _update_pos_white_8(keys):
        keys[5] -= 729
        keys[9] -= 1
        keys[29] -= 729
        keys[33] -= 3
        keys[37] -= 2187
        keys[41] -= 9
        keys[44] -= 243
        keys[45] -= 6561
        keys[52] -= 243
        keys[56] -= 27
    @staticmethod
    def _update_pos_white_9(keys):
        keys[0] -= 729
        keys[2] -= 3
        keys[36] -= 19683
        keys[37] -= 19683
        keys[40] -= 1
        keys[41] -= 1
        keys[44] -= 81
        keys[45] -= 81
        keys[52] -= 81
        keys[56] -= 81
    @staticmethod
    def _update_pos_white_10(keys):
        keys[4] -= 243
        keys[8] -= 3
        keys[44] -= 27
        keys[45] -= 3
        keys[52] -= 27
        keys[56] -= 243
    @staticmethod
    def _update_pos_white_11(keys):
        keys[12] -= 81
        keys[16] -= 3
        keys[22] -= 27
        keys[26] -= 3
    @staticmethod
    def _update_pos_white_12(keys):
        keys[14] -= 81
        keys[18] -= 3
        keys[20] -= 27
        keys[24] -= 3
    @staticmethod
    def _update_pos_white_13(keys):
        keys[6] -= 243
        keys[10] -= 3
        keys[46] -= 27
        keys[47] -= 3
        keys[53] -= 27
        keys[57] -= 243
    @staticmethod
    def _update_pos_white_14(keys):
        keys[1] -= 729
        keys[3] -= 3
        keys[36] -= 1
        keys[39] -= 1
        keys[40] -= 19683
        keys[43] -= 19683
        keys[46] -= 81
        keys[47] -= 81
        keys[53] -= 81
        keys[57] -= 81
    @staticmethod
    def _update_pos_white_15(keys):
        keys[7] -= 729
        keys[11] -= 1
        keys[31] -= 729
        keys[35] -= 3
        keys[39] -= 9
        keys[43] -= 2187
        keys[46] -= 243
        keys[47] -= 6561
        keys[53] -= 243
        keys[57] -= 27
    @staticmethod
    def _update_pos_white_16(keys):
        keys[13] -= 243
        keys[17] -= 1
        keys[29] -= 243
        keys[33] -= 9
        keys[37] -= 729
        keys[41] -= 27
        keys[44] -= 9
        keys[45] -= 2187
        keys[52] -= 9
        keys[56] -= 729
    @staticmethod
    def _update_pos_white_17(keys):
        keys[5] -= 243
        keys[9] -= 3
        keys[44] -= 3
        keys[45] -= 27
        keys[52] -= 3
        keys[56] -= 2187
    @staticmethod
    def _update_pos_white_18(keys):
        keys[0] -= 243
        keys[2] -= 9
        keys[22] -= 9
        keys[26] -= 9
        keys[52] -= 1
        keys[56] -= 6561
    @staticmethod
    def _update_pos_white_19(keys):
        keys[4] -= 81
        keys[8] -= 9
        keys[14] -= 27
        keys[18] -= 9
    @staticmethod
    def _update_pos_white_20(keys):
        keys[6] -= 81
        keys[10] -= 9
        keys[12] -= 27
        keys[16] -= 9
    @staticmethod
    def _update_pos_white_21(keys):
        keys[1] -= 243
        keys[3] -= 9
        keys[20] -= 9
        keys[24] -= 9
        keys[53] -= 1
        keys[57] -= 6561
    @staticmethod
    def _update_pos_white_22(keys):
        keys[7] -= 243
        keys[11] -= 3
        keys[46] -= 3
        keys[47] -= 27
        keys[53] -= 3
        keys[57] -= 2187
    @staticmethod
    def _update_pos_white_23(keys):
        keys[15] -= 243
        keys[19] -= 1
        keys[31] -= 243
        keys[35] -= 9
        keys[39] -= 27
        keys[43] -= 729
        keys[46] -= 9
        keys[47] -= 2187
        keys[53] -= 9
        keys[57] -= 729
    @staticmethod
    def _update_pos_white_24(keys):
        keys[21] -= 81
        keys[25] -= 1
        keys[29] -= 81
        keys[33] -= 27
        keys[37] -= 243
        keys[41] -= 81
        keys[44] -= 1
        keys[45] -= 729
    @staticmethod
    def _update_pos_white_25(keys):
        keys[13] -= 81
        keys[17] -= 3
        keys[22] -= 3
        keys[26] -= 27
    @staticmethod
    def _update_pos_white_26(keys):
        keys[5] -= 81
        keys[9] -= 9
        keys[14] -= 9
        keys[18] -= 27
    @staticmethod
    def _update_pos_white_27(keys):
        keys[0] -= 81
        keys[2] -= 27
        keys[6] -= 27
        keys[10] -= 27
    @staticmethod
    def _update_pos_white_28(keys):
        keys[1] -= 81
        keys[3] -= 27
        keys[4] -= 27
        keys[8] -= 27
    @staticmethod
    def _update_pos_white_29(keys):
        keys[7] -= 81
        keys[11] -= 9
        keys[12] -= 9
        keys[16] -= 27
    @staticmethod
    def _update_pos_white_30(keys):
        keys[15] -= 81
        keys[19] -= 3
        keys[20] -= 3
        keys[24] -= 27
    @staticmethod
    def _update_pos_white_31(keys):
        keys[23] -= 81
        keys[27] -= 1
        keys[31] -= 81
        keys[35] -= 27
        keys[39] -= 81
        keys[43] -= 243
        keys[46] -= 1
        keys[47] -= 729
    @staticmethod
    def _update_pos_white_32(keys):
        keys[22] -= 1
        keys[26] -= 81
        keys[29] -= 27
        keys[33] -= 81
        keys[37] -= 81
        keys[41] -= 243
        keys[50] -= 1
        keys[51] -= 729
    @staticmethod
    def _update_pos_white_33(keys):
        keys[14] -= 3
        keys[18] -= 81
        keys[21] -= 27
        keys[25] -= 3
    @staticmethod
    def _update_pos_white_34(keys):
        keys[6] -= 9
        keys[10] -= 81
        keys[13] -= 27
        keys[17] -= 9
    @staticmethod
    def _update_pos_white_35(keys):
        keys[1] -= 27
        keys[3] -= 81
        keys[5] -= 27
        keys[9] -= 27
    @staticmethod
    def _update_pos_white_36(keys):
        keys[0] -= 27
        keys[2] -= 81
        keys[7] -= 27
        keys[11] -= 27
    @staticmethod
    def _update_pos_white_37(keys):
        keys[4] -= 9
        keys[8] -= 81
        keys[15] -= 27
        keys[19] -= 9
    @staticmethod
    def _update_pos_white_38(keys):
        keys[12] -= 3
        keys[16] -= 81
        keys[23] -= 27
        keys[27] -= 3
    @staticmethod
    def _update_pos_white_39(keys):
        keys[20] -= 1
        keys[24] -= 81
        keys[31] -= 27
        keys[35] -= 81
        keys[39] -= 243
        keys[43] -= 81
        keys[48] -= 1
        keys[49] -= 729
    @staticmethod
    def _update_pos_white_40(keys):
        keys[14] -= 1
        keys[18] -= 243
        keys[29] -= 9
        keys[33] -= 243
        keys[37] -= 27
        keys[41] -= 729
        keys[50] -= 9
        keys[51] -= 2187
        keys[54] -= 9
        keys[58] -= 729
    @staticmethod
    def _update_pos_white_41(keys):
        keys[6] -= 3
        keys[10] -= 243
        keys[50] -= 3
        keys[51] -= 27
        keys[54] -= 3
        keys[58] -= 2187
    @staticmethod
    def _update_pos_white_42(keys):
        keys[1] -= 9
        keys[3] -= 243
        keys[21] -= 9
        keys[25] -= 9
        keys[54] -= 1
        keys[58] -= 6561
    @staticmethod
    def _update_pos_white_43(keys):
        keys[7] -= 9
        keys[11] -= 81
        keys[13] -= 9
        keys[17] -= 27
    @staticmethod
    def _update_pos_white_44(keys):
        keys[5] -= 9
        keys[9] -= 81
        keys[15] -= 9
        keys[19] -= 27
    @staticmethod
    def _update_pos_white_45(keys):
        keys[0] -= 9
        keys[2] -= 243
        keys[23] -= 9
        keys[27] -= 9
        keys[55] -= 1
        keys[59] -= 6561
    @staticmethod
    def _update_pos_white_46(keys):
        keys[4] -= 3
        keys[8] -= 243
        keys[48] -= 3
        keys[49] -= 27
        keys[55] -= 3
        keys[59] -= 2187
    @staticmethod
    def _update_pos_white_47(keys):
        keys[12] -= 1
        keys[16] -= 243
        keys[31] -= 9
        keys[35] -= 243
        keys[39] -= 729
        keys[43] -= 27
        keys[48] -= 9
        keys[49] -= 2187
        keys[55] -= 9
        keys[59] -= 729
    @staticmethod
    def _update_pos_white_48(keys):
        keys[6] -= 1
        keys[10] -= 729
        keys[29] -= 3
        keys[33] -= 729
        keys[37] -= 9
        keys[41] -= 2187
        keys[50] -= 243
        keys[51] -= 6561
        keys[54] -= 243
        keys[58] -= 27
    @staticmethod
    def _update_pos_white_49(keys):
        keys[1] -= 3
        keys[3] -= 729
        keys[37] -= 1
        keys[38] -= 19683
        keys[41] -= 19683
        keys[42] -= 1
        keys[50] -= 81
        keys[51] -= 81
        keys[54] -= 81
        keys[58] -= 81
    @staticmethod
    def _update_pos_white_50(keys):
        keys[7] -= 3
        keys[11] -= 243
        keys[50] -= 27
        keys[51] -= 3
        keys[54] -= 27
        keys[58] -= 243
    @staticmethod
    def _update_pos_white_51(keys):
        keys[15] -= 3
        keys[19] -= 81
        keys[21] -= 3
        keys[25] -= 27
    @staticmethod
    def _update_pos_white_52(keys):
        keys[13] -= 3
        keys[17] -= 81
        keys[23] -= 3
        keys[27] -= 27
    @staticmethod
    def _update_pos_white_53(keys):
        keys[5] -= 3
        keys[9] -= 243
        keys[48] -= 27
        keys[49] -= 3
        keys[55] -= 27
        keys[59] -= 243
    @staticmethod
    def _update_pos_white_54(keys):
        keys[0] -= 3
        keys[2] -= 729
        keys[38] -= 1
        keys[39] -= 19683
        keys[42] -= 19683
        keys[43] -= 1
        keys[48] -= 81
        keys[49] -= 81
        keys[55] -= 81
        keys[59] -= 81
    @staticmethod
    def _update_pos_white_55(keys):
        keys[4] -= 1
        keys[8] -= 729
        keys[31] -= 3
        keys[35] -= 729
        keys[39] -= 2187
        keys[43] -= 9
        keys[48] -= 243
        keys[49] -= 6561
        keys[55] -= 243
        keys[59] -= 27
    @staticmethod
    def _update_pos_white_56(keys):
        keys[1] -= 1
        keys[3] -= 2187
        keys[29] -= 1
        keys[30] -= 2187
        keys[33] -= 2187
        keys[34] -= 1
        keys[37] -= 3
        keys[38] -= 6561
        keys[41] -= 6561
        keys[42] -= 3
        keys[50] -= 19683
        keys[51] -= 19683
        keys[54] -= 6561
        keys[58] -= 1
    @staticmethod
    def _update_pos_white_57(keys):
        keys[7] -= 1
        keys[11] -= 729
        keys[30] -= 729
        keys[34] -= 3
        keys[38] -= 2187
        keys[42] -= 9
        keys[50] -= 6561
        keys[51] -= 243
        keys[54] -= 2187
        keys[58] -= 3
    @staticmethod
    def _update_pos_white_58(keys):
        keys[15] -= 1
        keys[19] -= 243
        keys[30] -= 243
        keys[34] -= 9
        keys[38] -= 729
        keys[42] -= 27
        keys[50] -= 2187
        keys[51] -= 9
        keys[54] -= 729
        keys[58] -= 9
    @staticmethod
    def _update_pos_white_59(keys):
        keys[23] -= 1
        keys[27] -= 81
        keys[30] -= 81
        keys[34] -= 27
        keys[38] -= 243
        keys[42] -= 81
        keys[50] -= 729
        keys[51] -= 1
    @staticmethod
    def _update_pos_white_60(keys):
        keys[21] -= 1
        keys[25] -= 81
        keys[30] -= 27
        keys[34] -= 81
        keys[38] -= 81
        keys[42] -= 243
        keys[48] -= 729
        keys[49] -= 1
    @staticmethod
    def _update_pos_white_61(keys):
        keys[13] -= 1
        keys[17] -= 243
        keys[30] -= 9
        keys[34] -= 243
        keys[38] -= 27
        keys[42] -= 729
        keys[48] -= 2187
        keys[49] -= 9
        keys[55] -= 729
        keys[59] -= 9
    @staticmethod
    def _update_pos_white_62(keys):
        keys[5] -= 1
        keys[9] -= 729
        keys[30] -= 3
        keys[34] -= 729
        keys[38] -= 9
        keys[42] -= 2187
        keys[48] -= 6561
        keys[49] -= 243
        keys[55] -= 2187
        keys[59] -= 3
    @staticmethod
    def _update_pos_white_63(keys):
        keys[0] -= 1
        keys[2] -= 2187
        keys[30] -= 1
        keys[31] -= 1
        keys[34] -= 2187
        keys[35] -= 2187
        keys[38] -= 3
        keys[39] -= 6561
        keys[42] -= 6561
        keys[43] -= 3
        keys[48] -= 19683
        keys[49] -= 19683
        keys[55] -= 6561
        keys[59] -= 1
    @staticmethod
    def _update_flip_black_0(keys):
        keys[0] -= 2187
        keys[2] -= 1
        keys[28] -= 2187
        keys[29] -= 2187
        keys[32] -= 1
        keys[33] -= 1
        keys[36] -= 6561
        keys[37] -= 6561
        keys[40] -= 3
        keys[41] -= 3
        keys[44] -= 19683
        keys[45] -= 19683
        keys[52] -= 6561
        keys[56] -= 1
    @staticmethod
    def _update_flip_black_1(keys):
        keys[4] -= 729
        keys[8] -= 1
        keys[28] -= 729
        keys[32] -= 3
        keys[36] -= 2187
        keys[40] -= 9
        keys[44] -= 6561
        keys[45] -= 243
        keys[52] -= 2187
        keys[56] -= 3
    @staticmethod
    def _update_flip_black_2(keys):
        keys[12] -= 243
        keys[16] -= 1
        keys[28] -= 243
        keys[32] -= 9
        keys[36] -= 729
        keys[40] -= 27
        keys[44] -= 2187
        keys[45] -= 9
        keys[52] -= 729
        keys[56] -= 9
    @staticmethod
    def _update_flip_black_3(keys):
        keys[20] -= 81
        keys[24] -= 1
        keys[28] -= 81
        keys[32] -= 27
        keys[36] -= 243
        keys[40] -= 81
        keys[44] -= 729
        keys[45] -= 1
    @staticmethod
    def _update_flip_black_4(keys):
        keys[22] -= 81
        keys[26] -= 1
        keys[28] -= 27
        keys[32] -= 81
        keys[36] -= 81
        keys[40] -= 243
        keys[46] -= 729
        keys[47] -= 1
    @staticmethod
    def _update_flip_black_5(keys):
        keys[14] -= 243
        keys[18] -= 1
        keys[28] -= 9
        keys[32] -= 243
        keys[36] -= 27
        keys[40] -= 729
        keys[46] -= 2187
        keys[47] -= 9
        keys[53] -= 729
        keys[57] -= 9
    @staticmethod
    def _update_flip_black_6(keys):
        keys[6] -= 729
        keys[10] -= 1
        keys[28] -= 3
        keys[32] -= 729
        keys[36] -= 9
        keys[40] -= 2187
        keys[46] -= 6561
        keys[47] -= 243
        keys[53] -= 2187
        keys[57] -= 3
    @staticmethod
    def _update_flip_black_7(keys):
        keys[1] -= 2187
        keys[3] -= 1
        keys[28] -= 1
        keys[31] -= 2187
        keys[32] -= 2187
        keys[35] -= 1
        keys[36] -= 3
        keys[39] -= 3
        keys[40] -= 6561
        keys[43] -= 6561
        keys[46] -= 19683
        keys[47] -= 19683
        keys[53] -= 6561
        keys[57] -= 1
    @staticmethod
    def _update_flip_black_8(keys):
        keys[5] -= 729
        keys[9] -= 1
        keys[29] -= 729
        keys[33] -= 3
        keys[37] -= 2187
        keys[41] -= 9
        keys[44] -= 243
        keys[45] -= 6561
        keys[52] -= 243
        keys[56] -= 27
    @staticmethod
    def _update_flip_black_9(keys):
        keys[0] -= 729
        keys[2] -= 3
        keys[36] -= 19683
        keys[37] -= 19683
        keys[40] -= 1
        keys[41] -= 1
        keys[44] -= 81
        keys[45] -= 81
        keys[52] -= 81
        keys[56] -= 81
    @staticmethod
    def _update_flip_black_10(keys):
        keys[4] -= 243
        keys[8] -= 3
        keys[44] -= 27
        keys[45] -= 3
        keys[52] -= 27
        keys[56] -= 243
    @staticmethod
    def _update_flip_black_11(keys):
        keys[12] -= 81
        keys[16] -= 3
        keys[22] -= 27
        keys[26] -= 3
    @staticmethod
    def _update_flip_black_12(keys):
        keys[14] -= 81
        keys[18] -= 3
        keys[20] -= 27
        keys[24] -= 3
    @staticmethod
    def _update_flip_black_13(keys):
        keys[6] -= 243
        keys[10] -= 3
        keys[46] -= 27
        keys[47] -= 3
        keys[53] -= 27
        keys[57] -= 243
    @staticmethod
    def _update_flip_black_14(keys):
        keys[1] -= 729
        keys[3] -= 3
        keys[36] -= 1
        keys[39] -= 1
        keys[40] -= 19683
        keys[43] -= 19683
        keys[46] -= 81
        keys[47] -= 81
        keys[53] -= 81
        keys[57] -= 81
    @staticmethod
    def _update_flip_black_15(keys):
        keys[7] -= 729
        keys[11] -= 1
        keys[31] -= 729
        keys[35] -= 3
        keys[39] -= 9
        keys[43] -= 2187
        keys[46] -= 243
        keys[47] -= 6561
        keys[53] -= 243
        keys[57] -= 27
    @staticmethod
    def _update_flip_black_16(keys):
        keys[13] -= 243
        keys[17] -= 1
        keys[29] -= 243
        keys[33] -= 9
        keys[37] -= 729
        keys[41] -= 27
        keys[44] -= 9
        keys[45] -= 2187
        keys[52] -= 9
        keys[56] -= 729
    @staticmethod
    def _update_flip_black_17(keys):
        keys[5] -= 243
        keys[9] -= 3
        keys[44] -= 3
        keys[45] -= 27
        keys[52] -= 3
        keys[56] -= 2187
    @staticmethod
    def _update_flip_black_18(keys):
        keys[0] -= 243
        keys[2] -= 9
        keys[22] -= 9
        keys[26] -= 9
        keys[52] -= 1
        keys[56] -= 6561
    @staticmethod
    def _update_flip_black_19(keys):
        keys[4] -= 81
        keys[8] -= 9
        keys[14] -= 27
        keys[18] -= 9
    @staticmethod
    def _update_flip_black_20(keys):
        keys[6] -= 81
        keys[10] -= 9
        keys[12] -= 27
        keys[16] -= 9
    @staticmethod
    def _update_flip_black_21(keys):
        keys[1] -= 243
        keys[3] -= 9
        keys[20] -= 9
        keys[24] -= 9
        keys[53] -= 1
        keys[57] -= 6561
    @staticmethod
    def _update_flip_black_22(keys):
        keys[7] -= 243
        keys[11] -= 3
        keys[46] -= 3
        keys[47] -= 27
        keys[53] -= 3
        keys[57] -= 2187
    @staticmethod
    def _update_flip_black_23(keys):
        keys[15] -= 243
        keys[19] -= 1
        keys[31] -= 243
        keys[35] -= 9
        keys[39] -= 27
        keys[43] -= 729
        keys[46] -= 9
        keys[47] -= 2187
        keys[53] -= 9
        keys[57] -= 729
    @staticmethod
    def _update_flip_black_24(keys):
        keys[21] -= 81
        keys[25] -= 1
        keys[29] -= 81
        keys[33] -= 27
        keys[37] -= 243
        keys[41] -= 81
        keys[44] -= 1
        keys[45] -= 729
    @staticmethod
    def _update_flip_black_25(keys):
        keys[13] -= 81
        keys[17] -= 3
        keys[22] -= 3
        keys[26] -= 27
    @staticmethod
    def _update_flip_black_26(keys):
        keys[5] -= 81
        keys[9] -= 9
        keys[14] -= 9
        keys[18] -= 27
    @staticmethod
    def _update_flip_black_27(keys):
        keys[0] -= 81
        keys[2] -= 27
        keys[6] -= 27
        keys[10] -= 27
    @staticmethod
    def _update_flip_black_28(keys):
        keys[1] -= 81
        keys[3] -= 27
        keys[4] -= 27
        keys[8] -= 27
    @staticmethod
    def _update_flip_black_29(keys):
        keys[7] -= 81
        keys[11] -= 9
        keys[12] -= 9
        keys[16] -= 27
    @staticmethod
    def _update_flip_black_30(keys):
        keys[15] -= 81
        keys[19] -= 3
        keys[20] -= 3
        keys[24] -= 27
    @staticmethod
    def _update_flip_black_31(keys):
        keys[23] -= 81
        keys[27] -= 1
        keys[31] -= 81
        keys[35] -= 27
        keys[39] -= 81
        keys[43] -= 243
        keys[46] -= 1
        keys[47] -= 729
    @staticmethod
    def _update_flip_black_32(keys):
        keys[22] -= 1
        keys[26] -= 81
        keys[29] -= 27
        keys[33] -= 81
        keys[37] -= 81
        keys[41] -= 243
        keys[50] -= 1
        keys[51] -= 729
    @staticmethod
    def _update_flip_black_33(keys):
        keys[14] -= 3
        keys[18] -= 81
        keys[21] -= 27
        keys[25] -= 3
    @staticmethod
    def _update_flip_black_34(keys):
        keys[6] -= 9
        keys[10] -= 81
        keys[13] -= 27
        keys[17] -= 9
    @staticmethod
    def _update_flip_black_35(keys):
        keys[1] -= 27
        keys[3] -= 81
        keys[5] -= 27
        keys[9] -= 27
    @staticmethod
    def _update_flip_black_36(keys):
        keys[0] -= 27
        keys[2] -= 81
        keys[7] -= 27
        keys[11] -= 27
    @staticmethod
    def _update_flip_black_37(keys):
        keys[4] -= 9
        keys[8] -= 81
        keys[15] -= 27
        keys[19] -= 9
    @staticmethod
    def _update_flip_black_38(keys):
        keys[12] -= 3
        keys[16] -= 81
        keys[23] -= 27
        keys[27] -= 3
    @staticmethod
    def _update_flip_black_39(keys):
        keys[20] -= 1
        keys[24] -= 81
        keys[31] -= 27
        keys[35] -= 81
        keys[39] -= 243
        keys[43] -= 81
        keys[48] -= 1
        keys[49] -= 729
    @staticmethod
    def _update_flip_black_40(keys):
        keys[14] -= 1
        keys[18] -= 243
        keys[29] -= 9
        keys[33] -= 243
        keys[37] -= 27
        keys[41] -= 729
        keys[50] -= 9
        keys[51] -= 2187
        keys[54] -= 9
        keys[58] -= 729
    @staticmethod
    def _update_flip_black_41(keys):
        keys[6] -= 3
        keys[10] -= 243
        keys[50] -= 3
        keys[51] -= 27
        keys[54] -= 3
        keys[58] -= 2187
    @staticmethod
    def _update_flip_black_42(keys):
        keys[1] -= 9
        keys[3] -= 243
        keys[21] -= 9
        keys[25] -= 9
        keys[54] -= 1
        keys[58] -= 6561
    @staticmethod
    def _update_flip_black_43(keys):
        keys[7] -= 9
        keys[11] -= 81
        keys[13] -= 9
        keys[17] -= 27
    @staticmethod
    def _update_flip_black_44(keys):
        keys[5] -= 9
        keys[9] -= 81
        keys[15] -= 9
        keys[19] -= 27
    @staticmethod
    def _update_flip_black_45(keys):
        keys[0] -= 9
        keys[2] -= 243
        keys[23] -= 9
        keys[27] -= 9
        keys[55] -= 1
        keys[59] -= 6561
    @staticmethod
    def _update_flip_black_46(keys):
        keys[4] -= 3
        keys[8] -= 243
        keys[48] -= 3
        keys[49] -= 27
        keys[55] -= 3
        keys[59] -= 2187
    @staticmethod
    def _update_flip_black_47(keys):
        keys[12] -= 1
        keys[16] -= 243
        keys[31] -= 9
        keys[35] -= 243
        keys[39] -= 729
        keys[43] -= 27
        keys[48] -= 9
        keys[49] -= 2187
        keys[55] -= 9
        keys[59] -= 729
    @staticmethod
    def _update_flip_black_48(keys):
        keys[6] -= 1
        keys[10] -= 729
        keys[29] -= 3
        keys[33] -= 729
        keys[37] -= 9
        keys[41] -= 2187
        keys[50] -= 243
        keys[51] -= 6561
        keys[54] -= 243
        keys[58] -= 27
    @staticmethod
    def _update_flip_black_49(keys):
        keys[1] -= 3
        keys[3] -= 729
        keys[37] -= 1
        keys[38] -= 19683
        keys[41] -= 19683
        keys[42] -= 1
        keys[50] -= 81
        keys[51] -= 81
        keys[54] -= 81
        keys[58] -= 81
    @staticmethod
    def _update_flip_black_50(keys):
        keys[7] -= 3
        keys[11] -= 243
        keys[50] -= 27
        keys[51] -= 3
        keys[54] -= 27
        keys[58] -= 243
    @staticmethod
    def _update_flip_black_51(keys):
        keys[15] -= 3
        keys[19] -= 81
        keys[21] -= 3
        keys[25] -= 27
    @staticmethod
    def _update_flip_black_52(keys):
        keys[13] -= 3
        keys[17] -= 81
        keys[23] -= 3
        keys[27] -= 27
    @staticmethod
    def _update_flip_black_53(keys):
        keys[5] -= 3
        keys[9] -= 243
        keys[48] -= 27
        keys[49] -= 3
        keys[55] -= 27
        keys[59] -= 243
    @staticmethod
    def _update_flip_black_54(keys):
        keys[0] -= 3
        keys[2] -= 729
        keys[38] -= 1
        keys[39] -= 19683
        keys[42] -= 19683
        keys[43] -= 1
        keys[48] -= 81
        keys[49] -= 81
        keys[55] -= 81
        keys[59] -= 81
    @staticmethod
    def _update_flip_black_55(keys):
        keys[4] -= 1
        keys[8] -= 729
        keys[31] -= 3
        keys[35] -= 729
        keys[39] -= 2187
        keys[43] -= 9
        keys[48] -= 243
        keys[49] -= 6561
        keys[55] -= 243
        keys[59] -= 27
    @staticmethod
    def _update_flip_black_56(keys):
        keys[1] -= 1
        keys[3] -= 2187
        keys[29] -= 1
        keys[30] -= 2187
        keys[33] -= 2187
        keys[34] -= 1
        keys[37] -= 3
        keys[38] -= 6561
        keys[41] -= 6561
        keys[42] -= 3
        keys[50] -= 19683
        keys[51] -= 19683
        keys[54] -= 6561
        keys[58] -= 1
    @staticmethod
    def _update_flip_black_57(keys):
        keys[7] -= 1
        keys[11] -= 729
        keys[30] -= 729
        keys[34] -= 3
        keys[38] -= 2187
        keys[42] -= 9
        keys[50] -= 6561
        keys[51] -= 243
        keys[54] -= 2187
        keys[58] -= 3
    @staticmethod
    def _update_flip_black_58(keys):
        keys[15] -= 1
        keys[19] -= 243
        keys[30] -= 243
        keys[34] -= 9
        keys[38] -= 729
        keys[42] -= 27
        keys[50] -= 2187
        keys[51] -= 9
        keys[54] -= 729
        keys[58] -= 9
    @staticmethod
    def _update_flip_black_59(keys):
        keys[23] -= 1
        keys[27] -= 81
        keys[30] -= 81
        keys[34] -= 27
        keys[38] -= 243
        keys[42] -= 81
        keys[50] -= 729
        keys[51] -= 1
    @staticmethod
    def _update_flip_black_60(keys):
        keys[21] -= 1
        keys[25] -= 81
        keys[30] -= 27
        keys[34] -= 81
        keys[38] -= 81
        keys[42] -= 243
        keys[48] -= 729
        keys[49] -= 1
    @staticmethod
    def _update_flip_black_61(keys):
        keys[13] -= 1
        keys[17] -= 243
        keys[30] -= 9
        keys[34] -= 243
        keys[38] -= 27
        keys[42] -= 729
        keys[48] -= 2187
        keys[49] -= 9
        keys[55] -= 729
        keys[59] -= 9
    @staticmethod
    def _update_flip_black_62(keys):
        keys[5] -= 1
        keys[9] -= 729
        keys[30] -= 3
        keys[34] -= 729
        keys[38] -= 9
        keys[42] -= 2187
        keys[48] -= 6561
        keys[49] -= 243
        keys[55] -= 2187
        keys[59] -= 3
    @staticmethod
    def _update_flip_black_63(keys):
        keys[0] -= 1
        keys[2] -= 2187
        keys[30] -= 1
        keys[31] -= 1
        keys[34] -= 2187
        keys[35] -= 2187
        keys[38] -= 3
        keys[39] -= 6561
        keys[42] -= 6561
        keys[43] -= 3
        keys[48] -= 19683
        keys[49] -= 19683
        keys[55] -= 6561
        keys[59] -= 1
    @staticmethod
    def _update_flip_white_0(keys):
        keys[0] += 2187
        keys[2] += 1
        keys[28] += 2187
        keys[29] += 2187
        keys[32] += 1
        keys[33] += 1
        keys[36] += 6561
        keys[37] += 6561
        keys[40] += 3
        keys[41] += 3
        keys[44] += 19683
        keys[45] += 19683
        keys[52] += 6561
        keys[56] += 1
    @staticmethod
    def _update_flip_white_1(keys):
        keys[4] += 729
        keys[8] += 1
        keys[28] += 729
        keys[32] += 3
        keys[36] += 2187
        keys[40] += 9
        keys[44] += 6561
        keys[45] += 243
        keys[52] += 2187
        keys[56] += 3
    @staticmethod
    def _update_flip_white_2(keys):
        keys[12] += 243
        keys[16] += 1
        keys[28] += 243
        keys[32] += 9
        keys[36] += 729
        keys[40] += 27
        keys[44] += 2187
        keys[45] += 9
        keys[52] += 729
        keys[56] += 9
    @staticmethod
    def _update_flip_white_3(keys):
        keys[20] += 81
        keys[24] += 1
        keys[28] += 81
        keys[32] += 27
        keys[36] += 243
        keys[40] += 81
        keys[44] += 729
        keys[45] += 1
    @staticmethod
    def _update_flip_white_4(keys):
        keys[22] += 81
        keys[26] += 1
        keys[28] += 27
        keys[32] += 81
        keys[36] += 81
        keys[40] += 243
        keys[46] += 729
        keys[47] += 1
    @staticmethod
    def _update_flip_white_5(keys):
        keys[14] += 243
        keys[18] += 1
        keys[28] += 9
        keys[32] += 243
        keys[36] += 27
        keys[40] += 729
        keys[46] += 2187
        keys[47] += 9
        keys[53] += 729
        keys[57] += 9
    @staticmethod
    def _update_flip_white_6(keys):
        keys[6] += 729
        keys[10] += 1
        keys[28] += 3
        keys[32] += 729
        keys[36] += 9
        keys[40] += 2187
        keys[46] += 6561
        keys[47] += 243
        keys[53] += 2187
        keys[57] += 3
    @staticmethod
    def _update_flip_white_7(keys):
        keys[1] += 2187
        keys[3] += 1
        keys[28] += 1
        keys[31] += 2187
        keys[32] += 2187
        keys[35] += 1
        keys[36] += 3
        keys[39] += 3
        keys[40] += 6561
        keys[43] += 6561
        keys[46] += 19683
        keys[47] += 19683
        keys[53] += 6561
        keys[57] += 1
    @staticmethod
    def _update_flip_white_8(keys):
        keys[5] += 729
        keys[9] += 1
        keys[29] += 729
        keys[33] += 3
        keys[37] += 2187
        keys[41] += 9
        keys[44] += 243
        keys[45] += 6561
        keys[52] += 243
        keys[56] += 27
    @staticmethod
    def _update_flip_white_9(keys):
        keys[0] += 729
        keys[2] += 3
        keys[36] += 19683
        keys[37] += 19683
        keys[40] += 1
        keys[41] += 1
        keys[44] += 81
        keys[45] += 81
        keys[52] += 81
        keys[56] += 81
    @staticmethod
    def _update_flip_white_10(keys):
        keys[4] += 243
        keys[8] += 3
        keys[44] += 27
        keys[45] += 3
        keys[52] += 27
        keys[56] += 243
    @staticmethod
    def _update_flip_white_11(keys):
        keys[12] += 81
        keys[16] += 3
        keys[22] += 27
        keys[26] += 3
    @staticmethod
    def _update_flip_white_12(keys):
        keys[14] += 81
        keys[18] += 3
        keys[20] += 27
        keys[24] += 3
    @staticmethod
    def _update_flip_white_13(keys):
        keys[6] += 243
        keys[10] += 3
        keys[46] += 27
        keys[47] += 3
        keys[53] += 27
        keys[57] += 243
    @staticmethod
    def _update_flip_white_14(keys):
        keys[1] += 729
        keys[3] += 3
        keys[36] += 1
        keys[39] += 1
        keys[40] += 19683
        keys[43] += 19683
        keys[46] += 81
        keys[47] += 81
        keys[53] += 81
        keys[57] += 81
    @staticmethod
    def _update_flip_white_15(keys):
        keys[7] += 729
        keys[11] += 1
        keys[31] += 729
        keys[35] += 3
        keys[39] += 9
        keys[43] += 2187
        keys[46] += 243
        keys[47] += 6561
        keys[53] += 243
        keys[57] += 27
    @staticmethod
    def _update_flip_white_16(keys):
        keys[13] += 243
        keys[17] += 1
        keys[29] += 243
        keys[33] += 9
        keys[37] += 729
        keys[41] += 27
        keys[44] += 9
        keys[45] += 2187
        keys[52] += 9
        keys[56] += 729
    @staticmethod
    def _update_flip_white_17(keys):
        keys[5] += 243
        keys[9] += 3
        keys[44] += 3
        keys[45] += 27
        keys[52] += 3
        keys[56] += 2187
    @staticmethod
    def _update_flip_white_18(keys):
        keys[0] += 243
        keys[2] += 9
        keys[22] += 9
        keys[26] += 9
        keys[52] += 1
        keys[56] += 6561
    @staticmethod
    def _update_flip_white_19(keys):
        keys[4] += 81
        keys[8] += 9
        keys[14] += 27
        keys[18] += 9
    @staticmethod
    def _update_flip_white_20(keys):
        keys[6] += 81
        keys[10] += 9
        keys[12] += 27
        keys[16] += 9
    @staticmethod
    def _update_flip_white_21(keys):
        keys[1] += 243
        keys[3] += 9
        keys[20] += 9
        keys[24] += 9
        keys[53] += 1
        keys[57] += 6561
    @staticmethod
    def _update_flip_white_22(keys):
        keys[7] += 243
        keys[11] += 3
        keys[46] += 3
        keys[47] += 27
        keys[53] += 3
        keys[57] += 2187
    @staticmethod
    def _update_flip_white_23(keys):
        keys[15] += 243
        keys[19] += 1
        keys[31] += 243
        keys[35] += 9
        keys[39] += 27
        keys[43] += 729
        keys[46] += 9
        keys[47] += 2187
        keys[53] += 9
        keys[57] += 729
    @staticmethod
    def _update_flip_white_24(keys):
        keys[21] += 81
        keys[25] += 1
        keys[29] += 81
        keys[33] += 27
        keys[37] += 243
        keys[41] += 81
        keys[44] += 1
        keys[45] += 729
    @staticmethod
    def _update_flip_white_25(keys):
        keys[13] += 81
        keys[17] += 3
        keys[22] += 3
        keys[26] += 27
    @staticmethod
    def _update_flip_white_26(keys):
        keys[5] += 81
        keys[9] += 9
        keys[14] += 9
        keys[18] += 27
    @staticmethod
    def _update_flip_white_27(keys):
        keys[0] += 81
        keys[2] += 27
        keys[6] += 27
        keys[10] += 27
    @staticmethod
    def _update_flip_white_28(keys):
        keys[1] += 81
        keys[3] += 27
        keys[4] += 27
        keys[8] += 27
    @staticmethod
    def _update_flip_white_29(keys):
        keys[7] += 81
        keys[11] += 9
        keys[12] += 9
        keys[16] += 27
    @staticmethod
    def _update_flip_white_30(keys):
        keys[15] += 81
        keys[19] += 3
        keys[20] += 3
        keys[24] += 27
    @staticmethod
    def _update_flip_white_31(keys):
        keys[23] += 81
        keys[27] += 1
        keys[31] += 81
        keys[35] += 27
        keys[39] += 81
        keys[43] += 243
        keys[46] += 1
        keys[47] += 729
    @staticmethod
    def _update_flip_white_32(keys):
        keys[22] += 1
        keys[26] += 81
        keys[29] += 27
        keys[33] += 81
        keys[37] += 81
        keys[41] += 243
        keys[50] += 1
        keys[51] += 729
    @staticmethod
    def _update_flip_white_33(keys):
        keys[14] += 3
        keys[18] += 81
        keys[21] += 27
        keys[25] += 3
    @staticmethod
    def _update_flip_white_34(keys):
        keys[6] += 9
        keys[10] += 81
        keys[13] += 27
        keys[17] += 9
    @staticmethod
    def _update_flip_white_35(keys):
        keys[1] += 27
        keys[3] += 81
        keys[5] += 27
        keys[9] += 27
    @staticmethod
    def _update_flip_white_36(keys):
        keys[0] += 27
        keys[2] += 81
        keys[7] += 27
        keys[11] += 27
    @staticmethod
    def _update_flip_white_37(keys):
        keys[4] += 9
        keys[8] += 81
        keys[15] += 27
        keys[19] += 9
    @staticmethod
    def _update_flip_white_38(keys):
        keys[12] += 3
        keys[16] += 81
        keys[23] += 27
        keys[27] += 3
    @staticmethod
    def _update_flip_white_39(keys):
        keys[20] += 1
        keys[24] += 81
        keys[31] += 27
        keys[35] += 81
        keys[39] += 243
        keys[43] += 81
        keys[48] += 1
        keys[49] += 729
    @staticmethod
    def _update_flip_white_40(keys):
        keys[14] += 1
        keys[18] += 243
        keys[29] += 9
        keys[33] += 243
        keys[37] += 27
        keys[41] += 729
        keys[50] += 9
        keys[51] += 2187
        keys[54] += 9
        keys[58] += 729
    @staticmethod
    def _update_flip_white_41(keys):
        keys[6] += 3
        keys[10] += 243
        keys[50] += 3
        keys[51] += 27
        keys[54] += 3
        keys[58] += 2187
    @staticmethod
    def _update_flip_white_42(keys):
        keys[1] += 9
        keys[3] += 243
        keys[21] += 9
        keys[25] += 9
        keys[54] += 1
        keys[58] += 6561
    @staticmethod
    def _update_flip_white_43(keys):
        keys[7] += 9
        keys[11] += 81
        keys[13] += 9
        keys[17] += 27
    @staticmethod
    def _update_flip_white_44(keys):
        keys[5] += 9
        keys[9] += 81
        keys[15] += 9
        keys[19] += 27
    @staticmethod
    def _update_flip_white_45(keys):
        keys[0] += 9
        keys[2] += 243
        keys[23] += 9
        keys[27] += 9
        keys[55] += 1
        keys[59] += 6561
    @staticmethod
    def _update_flip_white_46(keys):
        keys[4] += 3
        keys[8] += 243
        keys[48] += 3
        keys[49] += 27
        keys[55] += 3
        keys[59] += 2187
    @staticmethod
    def _update_flip_white_47(keys):
        keys[12] += 1
        keys[16] += 243
        keys[31] += 9
        keys[35] += 243
        keys[39] += 729
        keys[43] += 27
        keys[48] += 9
        keys[49] += 2187
        keys[55] += 9
        keys[59] += 729
    @staticmethod
    def _update_flip_white_48(keys):
        keys[6] += 1
        keys[10] += 729
        keys[29] += 3
        keys[33] += 729
        keys[37] += 9
        keys[41] += 2187
        keys[50] += 243
        keys[51] += 6561
        keys[54] += 243
        keys[58] += 27
    @staticmethod
    def _update_flip_white_49(keys):
        keys[1] += 3
        keys[3] += 729
        keys[37] += 1
        keys[38] += 19683
        keys[41] += 19683
        keys[42] += 1
        keys[50] += 81
        keys[51] += 81
        keys[54] += 81
        keys[58] += 81
    @staticmethod
    def _update_flip_white_50(keys):
        keys[7] += 3
        keys[11] += 243
        keys[50] += 27
        keys[51] += 3
        keys[54] += 27
        keys[58] += 243
    @staticmethod
    def _update_flip_white_51(keys):
        keys[15] += 3
        keys[19] += 81
        keys[21] += 3
        keys[25] += 27
    @staticmethod
    def _update_flip_white_52(keys):
        keys[13] += 3
        keys[17] += 81
        keys[23] += 3
        keys[27] += 27
    @staticmethod
    def _update_flip_white_53(keys):
        keys[5] += 3
        keys[9] += 243
        keys[48] += 27
        keys[49] += 3
        keys[55] += 27
        keys[59] += 243
    @staticmethod
    def _update_flip_white_54(keys):
        keys[0] += 3
        keys[2] += 729
        keys[38] += 1
        keys[39] += 19683
        keys[42] += 19683
        keys[43] += 1
        keys[48] += 81
        keys[49] += 81
        keys[55] += 81
        keys[59] += 81
    @staticmethod
    def _update_flip_white_55(keys):
        keys[4] += 1
        keys[8] += 729
        keys[31] += 3
        keys[35] += 729
        keys[39] += 2187
        keys[43] += 9
        keys[48] += 243
        keys[49] += 6561
        keys[55] += 243
        keys[59] += 27
    @staticmethod
    def _update_flip_white_56(keys):
        keys[1] += 1
        keys[3] += 2187
        keys[29] += 1
        keys[30] += 2187
        keys[33] += 2187
        keys[34] += 1
        keys[37] += 3
        keys[38] += 6561
        keys[41] += 6561
        keys[42] += 3
        keys[50] += 19683
        keys[51] += 19683
        keys[54] += 6561
        keys[58] += 1
    @staticmethod
    def _update_flip_white_57(keys):
        keys[7] += 1
        keys[11] += 729
        keys[30] += 729
        keys[34] += 3
        keys[38] += 2187
        keys[42] += 9
        keys[50] += 6561
        keys[51] += 243
        keys[54] += 2187
        keys[58] += 3
    @staticmethod
    def _update_flip_white_58(keys):
        keys[15] += 1
        keys[19] += 243
        keys[30] += 243
        keys[34] += 9
        keys[38] += 729
        keys[42] += 27
        keys[50] += 2187
        keys[51] += 9
        keys[54] += 729
        keys[58] += 9
    @staticmethod
    def _update_flip_white_59(keys):
        keys[23] += 1
        keys[27] += 81
        keys[30] += 81
        keys[34] += 27
        keys[38] += 243
        keys[42] += 81
        keys[50] += 729
        keys[51] += 1
    @staticmethod
    def _update_flip_white_60(keys):
        keys[21] += 1
        keys[25] += 81
        keys[30] += 27
        keys[34] += 81
        keys[38] += 81
        keys[42] += 243
        keys[48] += 729
        keys[49] += 1
    @staticmethod
    def _update_flip_white_61(keys):
        keys[13] += 1
        keys[17] += 243
        keys[30] += 9
        keys[34] += 243
        keys[38] += 27
        keys[42] += 729
        keys[48] += 2187
        keys[49] += 9
        keys[55] += 729
        keys[59] += 9
    @staticmethod
    def _update_flip_white_62(keys):
        keys[5] += 1
        keys[9] += 729
        keys[30] += 3
        keys[34] += 729
        keys[38] += 9
        keys[42] += 2187
        keys[48] += 6561
        keys[49] += 243
        keys[55] += 2187
        keys[59] += 3
    @staticmethod
    def _update_flip_white_63(keys):
        keys[0] += 1
        keys[2] += 2187
        keys[30] += 1
        keys[31] += 1
        keys[34] += 2187
        keys[35] += 2187
        keys[38] += 3
        keys[39] += 6561
        keys[42] += 6561
        keys[43] += 3
        keys[48] += 19683
        keys[49] += 19683
        keys[55] += 6561
        keys[59] += 1
    UPDATE_POS_BLACK_FUNCS_STATIC = (
        _update_pos_black_0,
        _update_pos_black_1,
        _update_pos_black_2,
        _update_pos_black_3,
        _update_pos_black_4,
        _update_pos_black_5,
        _update_pos_black_6,
        _update_pos_black_7,
        _update_pos_black_8,
        _update_pos_black_9,
        _update_pos_black_10,
        _update_pos_black_11,
        _update_pos_black_12,
        _update_pos_black_13,
        _update_pos_black_14,
        _update_pos_black_15,
        _update_pos_black_16,
        _update_pos_black_17,
        _update_pos_black_18,
        _update_pos_black_19,
        _update_pos_black_20,
        _update_pos_black_21,
        _update_pos_black_22,
        _update_pos_black_23,
        _update_pos_black_24,
        _update_pos_black_25,
        _update_pos_black_26,
        _update_pos_black_27,
        _update_pos_black_28,
        _update_pos_black_29,
        _update_pos_black_30,
        _update_pos_black_31,
        _update_pos_black_32,
        _update_pos_black_33,
        _update_pos_black_34,
        _update_pos_black_35,
        _update_pos_black_36,
        _update_pos_black_37,
        _update_pos_black_38,
        _update_pos_black_39,
        _update_pos_black_40,
        _update_pos_black_41,
        _update_pos_black_42,
        _update_pos_black_43,
        _update_pos_black_44,
        _update_pos_black_45,
        _update_pos_black_46,
        _update_pos_black_47,
        _update_pos_black_48,
        _update_pos_black_49,
        _update_pos_black_50,
        _update_pos_black_51,
        _update_pos_black_52,
        _update_pos_black_53,
        _update_pos_black_54,
        _update_pos_black_55,
        _update_pos_black_56,
        _update_pos_black_57,
        _update_pos_black_58,
        _update_pos_black_59,
        _update_pos_black_60,
        _update_pos_black_61,
        _update_pos_black_62,
        _update_pos_black_63,
    )
    UPDATE_POS_WHITE_FUNCS_STATIC = (
        _update_pos_white_0,
        _update_pos_white_1,
        _update_pos_white_2,
        _update_pos_white_3,
        _update_pos_white_4,
        _update_pos_white_5,
        _update_pos_white_6,
        _update_pos_white_7,
        _update_pos_white_8,
        _update_pos_white_9,
        _update_pos_white_10,
        _update_pos_white_11,
        _update_pos_white_12,
        _update_pos_white_13,
        _update_pos_white_14,
        _update_pos_white_15,
        _update_pos_white_16,
        _update_pos_white_17,
        _update_pos_white_18,
        _update_pos_white_19,
        _update_pos_white_20,
        _update_pos_white_21,
        _update_pos_white_22,
        _update_pos_white_23,
        _update_pos_white_24,
        _update_pos_white_25,
        _update_pos_white_26,
        _update_pos_white_27,
        _update_pos_white_28,
        _update_pos_white_29,
        _update_pos_white_30,
        _update_pos_white_31,
        _update_pos_white_32,
        _update_pos_white_33,
        _update_pos_white_34,
        _update_pos_white_35,
        _update_pos_white_36,
        _update_pos_white_37,
        _update_pos_white_38,
        _update_pos_white_39,
        _update_pos_white_40,
        _update_pos_white_41,
        _update_pos_white_42,
        _update_pos_white_43,
        _update_pos_white_44,
        _update_pos_white_45,
        _update_pos_white_46,
        _update_pos_white_47,
        _update_pos_white_48,
        _update_pos_white_49,
        _update_pos_white_50,
        _update_pos_white_51,
        _update_pos_white_52,
        _update_pos_white_53,
        _update_pos_white_54,
        _update_pos_white_55,
        _update_pos_white_56,
        _update_pos_white_57,
        _update_pos_white_58,
        _update_pos_white_59,
        _update_pos_white_60,
        _update_pos_white_61,
        _update_pos_white_62,
        _update_pos_white_63,
    )
    UPDATE_FLIP_BLACK_FUNCS_STATIC = (
        _update_flip_black_0,
        _update_flip_black_1,
        _update_flip_black_2,
        _update_flip_black_3,
        _update_flip_black_4,
        _update_flip_black_5,
        _update_flip_black_6,
        _update_flip_black_7,
        _update_flip_black_8,
        _update_flip_black_9,
        _update_flip_black_10,
        _update_flip_black_11,
        _update_flip_black_12,
        _update_flip_black_13,
        _update_flip_black_14,
        _update_flip_black_15,
        _update_flip_black_16,
        _update_flip_black_17,
        _update_flip_black_18,
        _update_flip_black_19,
        _update_flip_black_20,
        _update_flip_black_21,
        _update_flip_black_22,
        _update_flip_black_23,
        _update_flip_black_24,
        _update_flip_black_25,
        _update_flip_black_26,
        _update_flip_black_27,
        _update_flip_black_28,
        _update_flip_black_29,
        _update_flip_black_30,
        _update_flip_black_31,
        _update_flip_black_32,
        _update_flip_black_33,
        _update_flip_black_34,
        _update_flip_black_35,
        _update_flip_black_36,
        _update_flip_black_37,
        _update_flip_black_38,
        _update_flip_black_39,
        _update_flip_black_40,
        _update_flip_black_41,
        _update_flip_black_42,
        _update_flip_black_43,
        _update_flip_black_44,
        _update_flip_black_45,
        _update_flip_black_46,
        _update_flip_black_47,
        _update_flip_black_48,
        _update_flip_black_49,
        _update_flip_black_50,
        _update_flip_black_51,
        _update_flip_black_52,
        _update_flip_black_53,
        _update_flip_black_54,
        _update_flip_black_55,
        _update_flip_black_56,
        _update_flip_black_57,
        _update_flip_black_58,
        _update_flip_black_59,
        _update_flip_black_60,
        _update_flip_black_61,
        _update_flip_black_62,
        _update_flip_black_63,
    )
    UPDATE_FLIP_WHITE_FUNCS_STATIC = (
        _update_flip_white_0,
        _update_flip_white_1,
        _update_flip_white_2,
        _update_flip_white_3,
        _update_flip_white_4,
        _update_flip_white_5,
        _update_flip_white_6,
        _update_flip_white_7,
        _update_flip_white_8,
        _update_flip_white_9,
        _update_flip_white_10,
        _update_flip_white_11,
        _update_flip_white_12,
        _update_flip_white_13,
        _update_flip_white_14,
        _update_flip_white_15,
        _update_flip_white_16,
        _update_flip_white_17,
        _update_flip_white_18,
        _update_flip_white_19,
        _update_flip_white_20,
        _update_flip_white_21,
        _update_flip_white_22,
        _update_flip_white_23,
        _update_flip_white_24,
        _update_flip_white_25,
        _update_flip_white_26,
        _update_flip_white_27,
        _update_flip_white_28,
        _update_flip_white_29,
        _update_flip_white_30,
        _update_flip_white_31,
        _update_flip_white_32,
        _update_flip_white_33,
        _update_flip_white_34,
        _update_flip_white_35,
        _update_flip_white_36,
        _update_flip_white_37,
        _update_flip_white_38,
        _update_flip_white_39,
        _update_flip_white_40,
        _update_flip_white_41,
        _update_flip_white_42,
        _update_flip_white_43,
        _update_flip_white_44,
        _update_flip_white_45,
        _update_flip_white_46,
        _update_flip_white_47,
        _update_flip_white_48,
        _update_flip_white_49,
        _update_flip_white_50,
        _update_flip_white_51,
        _update_flip_white_52,
        _update_flip_white_53,
        _update_flip_white_54,
        _update_flip_white_55,
        _update_flip_white_56,
        _update_flip_white_57,
        _update_flip_white_58,
        _update_flip_white_59,
        _update_flip_white_60,
        _update_flip_white_61,
        _update_flip_white_62,
        _update_flip_white_63,
    )

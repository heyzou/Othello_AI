"""Bitboard operations and board conversion utilities."""

try:
    from othellopy.core import Board, Cell, Move
except ImportError:
    try:
        from othellopy.board import Board, Cell, Move
    except ImportError:
        Board = list
        Cell = int
        Move = tuple[int, int]

from .constants import FULL_MASK, NOT_A_FILE, NOT_H_FILE


def shift_bits(bits: int, direction: int) -> int:
    if direction == 0:  # north-west
        return ((bits & NOT_A_FILE) >> 9) & FULL_MASK
    if direction == 1:  # north
        return (bits >> 8) & FULL_MASK
    if direction == 2:  # north-east
        return ((bits & NOT_H_FILE) >> 7) & FULL_MASK
    if direction == 3:  # west
        return ((bits & NOT_A_FILE) >> 1) & FULL_MASK
    if direction == 4:  # east
        return ((bits & NOT_H_FILE) << 1) & FULL_MASK
    if direction == 5:  # south-west
        return ((bits & NOT_A_FILE) << 7) & FULL_MASK
    if direction == 6:  # south
        return (bits << 8) & FULL_MASK
    return ((bits & NOT_H_FILE) << 9) & FULL_MASK


def board_to_bits(board: Board) -> tuple[int, int]:
    black_bits = 0
    white_bits = 0
    for row in range(8):
        for col in range(8):
            bit = 1 << (row * 8 + col)
            cell = board[row][col]
            if cell == Cell.BLACK:
                black_bits |= bit
            elif cell == Cell.WHITE:
                white_bits |= bit
    return black_bits, white_bits


def move_to_pos(move: Move) -> int:
    row, col = move
    return row * 8 + col


def pos_to_move(pos: int) -> Move:
    return (pos // 8, pos % 8)


def flips_bits(state: tuple[int, int], pos: int, color: Cell) -> int:
    black_bits, white_bits = state
    if color == Cell.BLACK:
        own_bits, opponent_bits = black_bits, white_bits
    else:
        own_bits, opponent_bits = white_bits, black_bits

    move_bit = 1 << pos
    if move_bit & (black_bits | white_bits):
        return 0

    flips = 0
    for direction in range(8):
        line = 0
        current = shift_bits(move_bit, direction)
        while current and current & opponent_bits:
            line |= current
            current = shift_bits(current, direction)
        if current & own_bits:
            flips |= line
    return flips


def apply_move_bits(state: tuple[int, int], pos: int, color: Cell) -> tuple[int, int]:
    flips = flips_bits(state, pos, color)
    move_bit = 1 << pos
    black_bits, white_bits = state
    if color == Cell.BLACK:
        black_bits |= flips | move_bit
        white_bits &= ~flips
    else:
        white_bits |= flips | move_bit
        black_bits &= ~flips
    return black_bits, white_bits


def legal_move_mask_bits(state: tuple[int, int], color: Cell) -> int:
    black_bits, white_bits = state
    occupied = black_bits | white_bits
    empty_bits = FULL_MASK ^ occupied
    own_bits = black_bits if color == Cell.BLACK else white_bits
    opponent_bits = white_bits if color == Cell.BLACK else black_bits
    legal_bits = 0
    for direction in range(8):
        candidates = opponent_bits & shift_bits(own_bits, direction)
        for _ in range(5):
            candidates |= opponent_bits & shift_bits(candidates, direction)
        legal_bits |= empty_bits & shift_bits(candidates, direction)
    return legal_bits


def legal_moves_bits_uncached(state: tuple[int, int], color: Cell) -> list[int]:
    legal_bits = legal_move_mask_bits(state, color)
    moves = []
    bits = legal_bits
    while bits:
        bit = bits & -bits
        moves.append(bit.bit_length() - 1)
        bits ^= bit
    return moves


def surround_counts_bits(state: tuple[int, int]) -> tuple[int, int]:
    black_bits, white_bits = state
    occupied = black_bits | white_bits
    empty_bits = FULL_MASK ^ occupied
    black_count = 0
    white_count = 0
    for direction in range(8):
        black_count += (empty_bits & shift_bits(black_bits, direction)).bit_count()
        white_count += (empty_bits & shift_bits(white_bits, direction)).bit_count()
    return (black_count, white_count)


def empty_count_bits(state: tuple[int, int]) -> int:
    black_bits, white_bits = state
    return 64 - (black_bits | white_bits).bit_count()


def terminal_score_for_color_bits(state: tuple[int, int], color: Cell) -> int:
    black_bits, white_bits = state
    black_score = black_bits.bit_count()
    white_score = white_bits.bit_count()
    score = black_score - white_score
    if color == Cell.BLACK:
        return score
    return -score

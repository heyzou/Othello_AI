"""Common package for player experiments."""

from .base_player import BaseExperimentPlayer
from .evaluator import Evaluator
from .patterns import PATTERN_INDEXES, PATTERN_SIZES
from .constants import ORDER_WEIGHTS, BOARD_INDEXES
from .weights import WEIGHTS
from .book import BOOK_LINES
from .bitboard import (
    shift_bits,
    board_to_bits,
    move_to_pos,
    pos_to_move,
    flips_bits,
    apply_move_bits,
    legal_move_mask_bits,
    legal_moves_bits_uncached,
)

__all__ = [
    "BaseExperimentPlayer",
    "Evaluator",
    "PATTERN_INDEXES",
    "PATTERN_SIZES",
    "ORDER_WEIGHTS",
    "BOARD_INDEXES",
    "WEIGHTS",
    "BOOK_LINES",
    "shift_bits",
    "board_to_bits",
    "move_to_pos",
    "pos_to_move",
    "flips_bits",
    "apply_move_bits",
    "legal_move_mask_bits",
    "legal_moves_bits_uncached",
]

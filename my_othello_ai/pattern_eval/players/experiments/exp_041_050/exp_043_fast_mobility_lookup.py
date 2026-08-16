"""exp_043_fast_mobility_lookup.py: Fast line lookup table and inlined bitwise mobility computation. (Reference / Non-submission experimental code)"""

import time
import os
from othellopy.core import Board, Cell, Move
from othellopy.players import BasePlayer

from players.experiments.common.patterns import (
    ACTIVE_PATTERN_NAMES,
    INIT_PRECOMPUTED_PATTERN_NAMES,
    INIT_WARM_TABLE_STEPS,
    PATTERN_INDEXES,
    PATTERN_SIZES,
    PRECOMPUTED_PATTERN_NAMES,
    WARM_PATTERN_NAMES,
    WARM_TABLE_CHUNK_SIZE,
    WARM_TABLE_STEPS_PER_MOVE,
)
from players.experiments.common.weights import WEIGHTS
from players.experiments.common.book import BOOK_LINES

class MyPlayer(BasePlayer):
    BOARD_INDEXES = range(8)
    SEARCH_DEPTH = 7
    ENDGAME_EXACT_EMPTY = 10
    SIMPLE_ALPHA_BETA_DEPTH = 2
    PROBCUT_MIN_DEPTH = 3
    PROBCUT_MARGIN = 0.16
    PROBCUT_SHALLOW_DEPTHS = (0, 0, 0, 1, 2, 1, 2, 3, 4, 3, 4, 3, 4, 5, 6)
    LEGAL_MOVES_CACHE_MAX_SIZE = 65536
    EVAL_CACHE_MAX_SIZE = 262144
    SEARCH_HASH_TABLE_SIZE = 16384
    SEARCH_HASH_MASK = SEARCH_HASH_TABLE_SIZE - 1
    FULL_MASK = (1 << 64) - 1
    NOT_A_FILE = 0xfefefefefefefefe
    NOT_H_FILE = 0x7f7f7f7f7f7f7f7f
    ORDER_WEIGHTS = (
        (120, -20, 20, 5, 5, 20, -20, 120),
        (-20, -40, -5, -5, -5, -5, -40, -20),
        (20, -5, 15, 3, 3, 15, -5, 20),
        (5, -5, 3, 3, 3, 3, -5, 5),
        (5, -5, 3, 3, 3, 3, -5, 5),
        (20, -5, 15, 3, 3, 15, -5, 20),
        (-20, -40, -5, -5, -5, -5, -40, -20),
        (120, -20, 20, 5, 5, 20, -20, 120),
    )

    DIRECTIONS = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    )
    PATTERN_INDEXES = PATTERN_INDEXES
    PATTERN_SIZES = PATTERN_SIZES
    ACTIVE_PATTERN_NAMES = ACTIVE_PATTERN_NAMES
    PRECOMPUTED_PATTERN_NAMES = PRECOMPUTED_PATTERN_NAMES
    WARM_PATTERN_NAMES = WARM_PATTERN_NAMES
    INIT_PRECOMPUTED_PATTERN_NAMES = INIT_PRECOMPUTED_PATTERN_NAMES
    INIT_WARM_TABLE_STEPS = INIT_WARM_TABLE_STEPS
    WARM_TABLE_CHUNK_SIZE = WARM_TABLE_CHUNK_SIZE
    WARM_TABLE_STEPS_PER_MOVE = WARM_TABLE_STEPS_PER_MOVE
    PATTERN_BIT_SPECS = None
    PATTERN_KEY_META = None
    BOOK_LINES = BOOK_LINES
    WEIGHTS = WEIGHTS
    _accum_eval_time = 0.0
    _accum_eval_hit_time = 0.0
    _accum_eval_pattern_time = 0.0
    _accum_eval_mobility_time = 0.0
    _accum_eval_surround_time = 0.0
    _accum_eval_add_mlp_time = 0.0
    PARAMS = None
    PATTERN_CACHE = {}
    ADD_CACHE = {}
    PATTERN_VALUE_TABLES = {}
    PARTIAL_PATTERN_VALUE_TABLES = {}
    PARTIAL_PATTERN_VALUE_INDEXES = {}
    ADD_VALUE_TABLE = None
    ADDITIONAL_KEY_CACHE = {}
    MOBILITY_CACHE = {}
    LEGAL_MOVE_MASK_CACHE = {}
    LEGAL_MOVES_CACHE = {}
    EVAL_CACHE = {}
    EVAL_TABLE_WARM_INDEX = 0
    SEARCH_HASH_TABLE = [None] * SEARCH_HASH_TABLE_SIZE
    SEARCH_HASH_GET_COUNT = 0
    SEARCH_HASH_REG_COUNT = 0
    BOOK_LINES = ('f5', 'f5d6', 'f5d6c3g5', 'f5d6c3g5c6c5', 'f5d6c3g5c6c5c4b6', 'f5d6c3g5c6c5c4b6f6f4', 'f5d6c3g5c6c5c4b6f6f4e6d7', 'f5d6c3g5c6c5c4b6f6f4e6d7c7g6', 'f5d6c3g5c6c5c4b6f6f4e6d7c7g6d8b5', 'f5d6c3g5c6c5c4b6f6f4e6d7c7g6d8b5e7b3', 'f5d6c3g5c6c5c4b6f6f4e6d7c7g6d8b5e7b3a6e3', 'f5d6c3g5c6c5c4b6f6f4e6d7c7g6d8b5e7b3a6e3a5d3', 'f5d6c3g5f6d3', 'f5d6c3g5f6d3e3c2', 'f5d6c3g5f6d3e3c2c1e6', 'f5d6c3g5f6d3e3c2c1e6f4f3', 'f5d6c3g5f6d3e3c2c1e6f4f3f2g4', 'f5d6c3g5f6d3e3c2c1e6f4f3f2g4g6d2', 'f5d6c3g5f6d3e3c2c1e6f4f3f2g4g6d2h3h4', 'f5d6c3g5f6d3e3c2c1e6f4f3f2g4g6d2h3h4h5f7', 'f5d6c3g5f6d3e3c2c1e6f4f3f2g4g6d2h3h4h5f7e7g3', 'f5d6c3g5g6d3', 'f5d6c3g5g6d3c4e3', 'f5d6c3g5g6d3c4e3f3b4', 'f5d6c3g5g6d3c4e3f3b4f6e6', 'f5d6c3g5g6d3c4e3f3b4f6e6f4g4', 'f5d6c3g5g6d3c4e3f3b4f6e6f4g4h4h5', 'f5d6c3g5g6d3c4e3f3b4f6e6f4g4h4h5h6g3', 'f5d6c3g5g6d3c4e3f3b4f6e6f4g4h4h5h6g3h3f7', 'f5d6c3g5g6d3c4e3f3b4f6e6f4g4h4h5h6g3h3f7f8c2', 'f5d6c4b3', 'f5d6c4b3b4f4', 'f5d6c4b3b4f4f6g5', 'f5d6c4b3b4f4f6g5f3e7', 'f5d6c4b3b4f4f6g5f3e7c5e6', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3f2b6', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3f2b6h4d3', 'f5d6c5b4', 'f5d6c5b4d7e7', 'f5d6c5b4d7e7c7d8', 'f5d6c5b4d7e7c7d8c3d3', 'f5d6c5b4d7e7c7d8c3d3c4b3', 'f5d6c5b4d7e7c7d8c3d3c4b3d2e2', 'f5d6c5b4d7e7c7d8c3d3c4b3d2e2c2e3', 'f5d6c5b4d7e7c7d8c3d3c4b3d2e2c2e3f4f2', 'f5d6c5b4d7e7c7d8c3d3c4b3d2e2c2e3f4f2c6b5', 'f5d6c5b4d7e7c7d8c3d3c4b3d2e2c2e3f4f2c6b5f3c8', 'f5d6c4', 'f5d6c4b3b4', 'f5d6c4b3b4f4f6', 'f5d6c4b3b4f4f6g5f3', 'f5d6c4b3b4f4f6g5f3e7c5', 'f5d6c4b3b4f4f6g5f3e7c5e6c3', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3f2', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3f2b6h4', 'f5d6c4b3b4f4f6g5f3e7c5e6c3g4c6g3h3e3f2b6h4d3e2', 'f5d6c4d3c3', 'f5d6c4d3c3b3d2', 'f5d6c4d3c3b3d2e1b5', 'f5d6c4d3c3b3d2e1b5c5b4', 'f5d6c4d3c3b3d2e1b5c5b4e3c2', 'f5d6c4d3c3b3d2e1b5c5b4e3c2a4c6', 'f5d6c4d3c3b3d2e1b5c5b4e3c2a4c6d1e2', 'f5d6c4d3c3b3d2e1b5c5b4e3c2a4c6d1e2c7b6', 'f5d6c4d3c3b3d2e1b5c5b4e3c2a4c6d1e2c7b6f1e6', 'f5d6c4d3c3b3d2e1b5c5b4e3c2a4c6d1e2c7b6f1e6f3f2', 'f5d6c4d3c3f4f6', 'f5d6c4d3c3f4f6f3e6', 'f5d6c4d3c3f4f6f3e6e7f7', 'f5d6c4d3c3f4f6f3e6e7f7c5b6', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g5e3', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g5e3d7c6', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g5e3d7c6e2g4', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g5e3d7c6e2g4h3d2', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g5e3d7c6e2g4h3d2g3f1', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g6e3', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g6e3e2f1', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g6e3e2f1d1g5', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g6e3e2f1d1g5c6d8', 'f5d6c4d3c3f4f6f3e6e7f7c5b6g6e3e2f1d1g5c6d8g4h6', 'f5d6c4d3c3f4f6b4c2', 'f5d6c4d3c3f4f6b4c2f3e3', 'f5d6c4d3c3f4f6b4c2f3e3e2c6', 'f5d6c4d3c3f4f6b4c2f3e3e2c6f2c5', 'f5d6c4d3c3f4f6b4c2f3e3e2c6f2c5e6d2', 'f5d6c4d3c3f4f6b4c2f3e3e2c6f2c5e6d2g4d7', 'f5d6c4d3c3f4f6b4c2f3e3e2c6f2c5e6d2g4d7b3g5', 'f5d6c4d3c3f4f6b4c2f3e3e2c6f2c5e6d2g4d7b3g5c8h4', 'f5d6c4d3c3f4f6g5e3', 'f5d6c4d3c3f4f6g5e3f3g6', 'f5d6c4d3c3f4f6g5e3f3g6e2h5', 'f5d6c4d3c3f4f6g5e3f3g6e2h5c5g4', 'f5d6c4d3c3f4f6g5e3f3g6e2h5c5g4g3f2', 'f5d6c4d3c3b5b4', 'f5d6c4d3c3b5b4f4c5', 'f5d6c4d3c3b5b4f4c5a4b3', 'f5d6c4d3c3b5b4f4c5a4b3d2a6', 'f5d6c4d3c3b5b4f4c5a4b3d2a6a3e3', 'f5d6c4d3c3b5b4f4c5a4b3d2a6a3e3f3g4', 'f5d6c4d3c3b5b4f4c5a4b3d2a6a3e3f3g4e6f6', 'f5d6c4d3c3b5b4f4c5a4b3d2a6a3e3f3g4e6f6g3e2', 'f5d6c4d3c3b5b4f4c5a4b3d2a6a3e3f3g4e6f6g3e2c2f2', 'f5d6c4g5f6', 'f5d6c4g5f6f4f3', 'f5d6c4g5f6f4f3d3c3', 'f5d6c4g5f6f4f3d3c3g6e3', 'f5d6c4g5f6f4f3d3c3g6e3e6h5', 'f5d6c4g5f6f4f3d3c3g6e3e6h5d2e2', 'f5d6c4g5f6f4f3d3c3g6e3e6h5d2e2c2c6', 'f5d6c4g5f6f4f3d3c3g6e3e6h5d2e2c2c6c5b6', 'f5d6c4g5f6f4f3d3c3g6e3e6h5d2e2c2c6c5b6b4b3', 'f5d6c4g5f6f4f3d3c3g6e3e6h5d2e2c2c6c5b6b4b3c7a4', 'f5f6e6', 'f5f6e6f4g6', 'f5f6e6f4g6c5f3', 'f5f6e6f4g6c5f3g4e3', 'f5f6e6f4g6c5f3g4e3d6g5', 'f5f6e6f4g6c5f3g4e3d6g5g3c3', 'f5f6e6f4g6c5f3g4e3d6g5g3c3h5c4', 'f5f6e6f4g6c5f3g4e3d6g5g3c3h5c4d7h6', 'f5f6e6f4g6c5f3g4e3d6g5g3c3h5c4d7h6h7h3', 'f5f6e6f4g6c5f3g4e3d6g5g3c3h5c4d7h6h7h3f7e7', 'f5f6e6f4g6c5f3g4e3d6g5g3c3h5c4d7h6h7h3f7e7f8h4', 'f5f6e6f4g6c5f3g5d6', 'f5f6e6f4g6c5f3g5d6e3h4', 'f5f6e6f4g6c5f3g5d6e3h4g3g4', 'f5f6e6f4g6c5f3g5d6e3h4g3g4h6e2', 'f5f6e6f4g6c5f3g5d6e3h4g3g4h6e2d3h5', 'f5f6e6f4g6c5f3g5d6e3h4g3g4h6e2d3h5h3c6', 'f5f6e6f4g6c5f3g5d6e3h4g3g4h6e2d3h5h3c6e7f2', 'f5f6e6f4g6c5f3g5d6e3h4g3g4h6e2d3h5h3c6e7f2c4d2', 'f5f6e6f4g6d6g4', 'f5f6e6f4g6d6g4g5h4', 'f5f6e6f4g6d6g4g5h4e7f3', 'f5f6e6f4g6d6g4g5h4e7f3h6f7', 'f5f6e6f4g6d6g4g5h4e7f3h6f7e8f8', 'f5f6e6f4g6d6g4g5h4e7f3h6f7e8f8g8d3', 'f5f6e6f4g6d6g4g5h4e7f3h6f7e8f8g8d3h5h7', 'f5f6e6f4g6d6g4g5h4e7f3h6f7e8f8g8d3h5h7e3c5', 'f5f6e6f4g6d6g4g5h4e7f3h6f7e8f8g8d3h5h7e3c5c4g3', 'f5f6e6d6f7', 'f5f6e6d6f7e3c6', 'f5f6e6d6f7e3c6e7f4', 'f5f6e6d6f7e3c6e7f4c5d8', 'f5f6e6d6f7e3c6e7f4c5d8c7d7', 'f5f6e6d6f7e3c6e7f4c5d8c7d7f8b5', 'f5f6e6d6f7e3c6e7f4c5d8c7d7f8b5c4e8', 'f5f6e6d6f7e3c6e7f4c5d8c7d7f8b5c4e8c8f3', 'f5f6e6d6f7e3c6e7f4c5d8c7d7f8b5c4e8c8f3g5b6', 'f5f6e6d6f7e3c6e7f4c5d8c7d7f8b5c4e8c8f3g5b6d3b4', 'f5f6e6d6f7f4d7', 'f5f6e6d6f7f4d7e7d8', 'f5f6e6d6f7f4d7e7d8g5c6', 'f5f6e6d6f7f4d7e7d8g5c6f8g6', 'f5f6e6d6f7f4d7e7d8g5c6f8g6h5h6', 'f5f6e6d6f7f4d7e7d8g5c6f8g6h5h6h7c4', 'f5f6e6d6f7f4d7e7d8g5c6f8g6h5h6h7c4e8g8', 'f5f6e6d6f7f4d7e7d8g5c6f8g6h5h6h7c4e8g8c5e3', 'f5f6e6d6f7f4d7e7d8g5c6f8g6h5h6h7c4e8g8c5e3d3c7')
    BOOK_CACHE = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MyPlayer._pattern_bit_specs()
        MyPlayer._pattern_key_meta()
        MyPlayer._precompute_init_evaluation_tables()
        MyPlayer._warm_init_evaluation_table_steps()

    def next_move(self, board: Board) -> Move:
        start_total = time.perf_counter()
        MyPlayer._accum_eval_time = 0.0
        MyPlayer._accum_eval_hit_time = 0.0
        MyPlayer._accum_eval_pattern_time = 0.0
        MyPlayer._accum_eval_mobility_time = 0.0
        MyPlayer._accum_eval_surround_time = 0.0
        MyPlayer._accum_eval_add_mlp_time = 0.0
        self._t_book = 0.0
        self._t_search = 0.0

        self._pattern_bit_specs()
        MyPlayer.SEARCH_HASH_GET_COUNT = 0
        MyPlayer.SEARCH_HASH_REG_COUNT = 0
        state = self._board_to_bits(board)
        actual_turn = (state[0] | state[1]).bit_count() - 3
        pattern_keys = self._pattern_keys_from_state(state)
        moves = self._legal_moves_bits(state, self.color)
        if not moves:
            return None
        MyPlayer._warm_evaluation_table_steps()

        t0_book = time.perf_counter()
        book_move = self._book_move_bits(state)
        self._t_book = time.perf_counter() - t0_book

        if book_move is not None and self._move_to_pos(book_move) in moves:
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, is_book=True, actual_turn=actual_turn)
            return book_move

        t0_search = time.perf_counter()

        best_move = moves[0]
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        if self._empty_count_bits(state) <= self.ENDGAME_EXACT_EMPTY:
            ordered_moves = self._order_moves_by_opponent_mobility(state, moves, self.color)
            for move in ordered_moves:
                next_state = self._apply_move_bits(state, move, self.color)
                score = -self._endgame_exact_search(
                    next_state,
                    self._opponent_of(self.color),
                    -65,
                    65,
                )
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)

            self._t_search = time.perf_counter() - t0_search
            total_time = time.perf_counter() - start_total
            self._log_profile(total_time, is_book=False, actual_turn=actual_turn)
            return self._pos_to_move(best_move)

        ordered_moves = self._order_move_positions_by_weight(moves)
        for move in ordered_moves:
            next_state, next_pattern_keys = self._apply_move_with_pattern_keys(
                state, pattern_keys, move, self.color
            )
            score = -self._negascout(
                next_state,
                next_pattern_keys,
                depth=self.SEARCH_DEPTH - 1,
                current_color=self._opponent_of(self.color),
                alpha=-beta,
                beta=-alpha,
            )
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        self._t_search = time.perf_counter() - t0_search
        total_time = time.perf_counter() - start_total
        self._log_profile(total_time, is_book=False, actual_turn=actual_turn)
        return self._pos_to_move(best_move)

    def _move_number(self, board: Board) -> int:
        stones = 0
        for row in board:
            for cell in row:
                if cell != Cell.EMPTY:
                    stones += 1
        return stones - 3








    def _order_move_positions_by_weight(self, moves: tuple[int, ...] | list[int]) -> list[int]:
        return sorted(moves, key=lambda pos: self.ORDER_WEIGHTS[pos // 8][pos % 8], reverse=True)

    def _order_moves_by_opponent_mobility(
        self,
        state: tuple[int, int],
        moves: tuple[int, ...] | list[int],
        current_color: Cell,
    ) -> list[int]:
        next_color = self._opponent_of(current_color)
        return sorted(
            moves,
            key=lambda move: self._legal_move_mask_bits(
                self._apply_move_bits(state, move, current_color),
                next_color,
            ).bit_count(),
        )

    def _endgame_exact_search(
        self,
        state: tuple[int, int],
        current_color: Cell,
        alpha: int,
        beta: int,
    ) -> int:
        moves = self._legal_moves_bits(state, current_color)
        next_color = self._opponent_of(current_color)

        if not moves:
            if not self._legal_moves_bits(state, next_color):
                return self._terminal_score_for_color_bits(state, current_color)
            return -self._endgame_exact_search(state, next_color, -beta, -alpha)

        best_score = -65
        moves = self._order_moves_by_opponent_mobility(state, moves, current_color)
        for move in moves:
            next_state = self._apply_move_bits(state, move, current_color)
            score = -self._endgame_exact_search(next_state, next_color, -beta, -alpha)
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return best_score

    def _negascout(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        depth: int,
        current_color: Cell,
        alpha: float,
        beta: float,
        allow_probcut: bool = True,
    ) -> float:
        # 葉ノードでは、現在手番から見た盤面評価を返す。
        if depth == 0:
            return self._evaluate_for_color_bits(state, current_color, pattern_keys)

        original_alpha = alpha
        original_beta = beta
        search_key = self._search_hash_key(state, depth, current_color, allow_probcut)
        cached = self._search_hash_get(search_key, alpha, beta)
        if cached is not None:
            return cached

        # 葉に近い浅い探索では、NegaScoutではなく通常のalpha-betaを使う。
        if depth <= self.SIMPLE_ALPHA_BETA_DEPTH:
            score = self._alpha_beta_simple(state, pattern_keys, depth, current_color, alpha, beta)
            self._search_hash_register(search_key, score, original_alpha, original_beta)
            return score

        moves = self._legal_moves_bits(state, current_color)
        next_color = self._opponent_of(current_color)

        # 現在手番だけ合法手がなければパスし、両者なければ終局として評価する。
        if not moves:
            if not self._legal_moves_bits(state, next_color):
                score = self._terminal_score_for_color_bits(state, current_color)
            else:
                score = -self._negascout(state, pattern_keys, depth, next_color, -beta, -alpha, allow_probcut)
            self._search_hash_register(search_key, score, original_alpha, original_beta)
            return score

        # 深く読む前に、浅い評価で枝刈りできるか試す。
        if allow_probcut and depth >= self.PROBCUT_MIN_DEPTH:
            cut_score = self._probcut(state, pattern_keys, depth, current_color, alpha, beta)
            if cut_score is not None:
                self._search_hash_register(search_key, cut_score, original_alpha, original_beta)
                return cut_score

        # 良さそうな手から読むことで、alpha-betaの枝刈りを起こしやすくする。
        moves = self._order_move_positions_by_weight(moves)
        children = []
        for move in moves:
            next_state, next_pattern_keys = self._apply_move_with_pattern_keys(
                state, pattern_keys, move, current_color
            )
            order_score = 0.0
            if depth >= 2 and len(moves) > 1:
                order_score = self._evaluate_for_color_bits(next_state, current_color, next_pattern_keys)
            children.append((move, next_state, next_pattern_keys, order_score))
        if depth >= 2 and len(children) > 1:
            children.sort(key=lambda child: child[3], reverse=True)

        search_window = beta
        best_score = float("-inf")

        for index, child in enumerate(children):
            next_state = child[1]
            next_pattern_keys = child[2]
            # 1手目は通常窓、2手目以降は狭い窓で先に読む。
            score = -self._negascout(
                next_state, next_pattern_keys, depth - 1, next_color, -search_window, -alpha, allow_probcut
            )

            # 狭い窓で有望そうなら、通常窓で読み直す。
            if alpha < score < beta and index > 0 and depth > 1:
                score = -self._negascout(
                    next_state, next_pattern_keys, depth - 1, next_color, -beta, -score, allow_probcut
                )

            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
            search_window = alpha + 1

        self._search_hash_register(search_key, best_score, original_alpha, original_beta)
        return best_score

    def _search_hash_key(
        self,
        state: tuple[int, int],
        depth: int,
        current_color: Cell,
        allow_probcut: bool,
    ) -> tuple[int, int, int, int, bool]:
        color_key = 1 if current_color == Cell.BLACK else 2
        black_bits, white_bits = state
        return (black_bits, white_bits, color_key, depth, allow_probcut)

    @classmethod
    def _search_hash_index(cls, key: tuple[int, int, int, int, bool]) -> int:
        black_bits, white_bits, color, depth, allow_probcut = key
        value = black_bits ^ ((white_bits << 1) & cls.FULL_MASK)
        value ^= color * 131 + depth * 17 + int(allow_probcut)
        value = (value ^ (value >> 33) ^ (value >> 17)) & 0xFFFFFFFFFFFFFFFF
        return value & cls.SEARCH_HASH_MASK

    @classmethod
    def _search_hash_get(
        cls,
        key: tuple[int, int, int, int, bool],
        alpha: float,
        beta: float,
    ) -> float | None:
        entry = cls.SEARCH_HASH_TABLE[cls._search_hash_index(key)]
        if entry is None:
            return None
        entry_key, lower, upper = entry
        if entry_key != key:
            return None
        if lower >= beta:
            cls.SEARCH_HASH_GET_COUNT += 1
            return lower
        if upper <= alpha:
            cls.SEARCH_HASH_GET_COUNT += 1
            return upper
        if lower == upper:
            cls.SEARCH_HASH_GET_COUNT += 1
            return lower
        return None

    @classmethod
    def _search_hash_register(
        cls,
        key: tuple[int, int, int, int, bool],
        score: float,
        alpha: float,
        beta: float,
    ) -> None:
        lower = float("-inf")
        upper = float("inf")
        if score <= alpha:
            upper = score
        elif score >= beta:
            lower = score
        else:
            lower = score
            upper = score
        cls.SEARCH_HASH_REG_COUNT += 1
        cls.SEARCH_HASH_TABLE[cls._search_hash_index(key)] = (key, lower, upper)

    def _alpha_beta_simple(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        depth: int,
        current_color: Cell,
        alpha: float,
        beta: float,
    ) -> float:
        if depth == 0:
            return self._evaluate_for_color_bits(state, current_color, pattern_keys)

        moves = self._legal_moves_bits(state, current_color)
        next_color = self._opponent_of(current_color)

        if not moves:
            if not self._legal_moves_bits(state, next_color):
                return self._terminal_score_for_color_bits(state, current_color)
            return -self._alpha_beta_simple(state, pattern_keys, depth, next_color, -beta, -alpha)

        best_score = float("-inf")
        for move in moves:
            next_state, next_pattern_keys = self._apply_move_with_pattern_keys(
                state, pattern_keys, move, current_color
            )
            score = -self._alpha_beta_simple(next_state, next_pattern_keys, depth - 1, next_color, -beta, -alpha)
            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_score

    def _empty_count_bits(self, state: tuple[int, int]) -> int:
        black_bits, white_bits = state
        return 64 - (black_bits | white_bits).bit_count()

    def _terminal_score_for_color_bits(self, state: tuple[int, int], color: Cell) -> int:
        black_bits, white_bits = state
        black_score = black_bits.bit_count()
        white_score = white_bits.bit_count()
        score = black_score - white_score
        if color == Cell.BLACK:
            return score
        return -score

    def _probcut(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        depth: int,
        current_color: Cell,
        alpha: float,
        beta: float,
    ):
        margin = self.PROBCUT_MARGIN + 0.02 * depth
        estimate = self._evaluate_for_color_bits(state, current_color, pattern_keys)
        if estimate >= beta + margin:
            return beta
        if estimate <= alpha - margin:
            return alpha
        if depth < self.PROBCUT_MIN_DEPTH:
            return None

        if depth < len(self.PROBCUT_SHALLOW_DEPTHS):
            probe_depth = self.PROBCUT_SHALLOW_DEPTHS[depth]
        else:
            probe_depth = max(1, depth - 8)
        if probe_depth <= 0:
            return None
        if estimate + margin >= beta:
            high = beta + margin
            high_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, high - 0.001, high, allow_probcut=False
            )
            if high_score >= high:
                return beta

        if estimate - margin <= alpha:
            low = alpha - margin
            low_score = self._negascout(
                state, pattern_keys, probe_depth, current_color, low, low + 0.001, allow_probcut=False
            )
            if low_score <= low:
                return alpha

        return None

    def _evaluate_for_color_bits(
        self,
        state: tuple[int, int],
        color: Cell,
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        score = self._evaluate_black_perspective_bits(state, pattern_keys)
        if color == Cell.BLACK:
            return score
        return -score

    def _evaluate_black_perspective_bits(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None = None,
    ) -> float:
        t0 = time.perf_counter()
        cached = MyPlayer.EVAL_CACHE.get(state)
        if cached is not None:
            dt = time.perf_counter() - t0
            MyPlayer._accum_eval_time += dt
            MyPlayer._accum_eval_hit_time += dt
            return cached

        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)

        t_pat_start = time.perf_counter()
        final_dense, final_bias = self._params()[2]
        pattern_name_to_final_index = MyPlayer._pattern_name_to_final_index()
        group_infos = MyPlayer._pattern_key_group_infos()
        result = final_bias
        for name, start, end in group_infos:
            group_sum = 0.0
            pattern_table = MyPlayer.PATTERN_VALUE_TABLES.get(name)
            for index in range(start, end):
                key = pattern_keys[index]
                if pattern_table is None:
                    group_sum += MyPlayer._compute_pattern_value(name, key)
                else:
                    group_sum += pattern_table[key]
            result += group_sum * final_dense[pattern_name_to_final_index[name]]
        MyPlayer._accum_eval_pattern_time += time.perf_counter() - t_pat_start

        add_key = self._additional_key_bits(state)
        add_value = self._add_value(add_key)
        result += add_value * final_dense[len(self.PATTERN_SIZES)]

        cache = MyPlayer.EVAL_CACHE
        if len(cache) >= self.EVAL_CACHE_MAX_SIZE:
            cache.clear()
        cache[state] = result
        MyPlayer._accum_eval_time += time.perf_counter() - t0
        return result

    @classmethod
    def _pattern_name_to_final_index(cls):
        return {
            "diagonal8": 0,
            "diagonal7": 1,
            "diagonal6": 2,
            "diagonal5": 3,
            "edge": 4,
            "edge2X": 5,
            "triangle": 6,
            "corner3x3": 7,
        }

    @classmethod
    def _params(cls):
        if cls.PARAMS is not None:
            return cls.PARAMS
        if not cls.WEIGHTS:
            raise RuntimeError("current.py needs embedded model_8patterns weights before use")

        weights = cls.WEIGHTS
        pos = 0

        def take():
            nonlocal pos
            value = weights[pos]
            pos += 1
            return value

        patterns = {}
        for name, size in cls.PATTERN_SIZES.items():
            dense0 = tuple(tuple(take() for _ in range(size * 2)) for _ in range(16))
            bias0 = tuple(take() for _ in range(16))
            dense1 = tuple(tuple(take() for _ in range(16)) for _ in range(16))
            bias1 = tuple(take() for _ in range(16))
            dense2 = tuple(take() for _ in range(16))
            bias2 = take()
            patterns[name] = (size, dense0, bias0, dense1, bias1, dense2, bias2)

        add_dense0 = tuple(tuple(take() for _ in range(3)) for _ in range(8))
        add_bias0 = tuple(take() for _ in range(8))
        add_dense1 = tuple(take() for _ in range(8))
        add_bias1 = take()
        final_dense = tuple(take() for _ in range(len(cls.PATTERN_SIZES) + 1))
        final_bias = take()
        cls.PARAMS = (patterns, (add_dense0, add_bias0, add_dense1, add_bias1), (final_dense, final_bias))
        return cls.PARAMS

    @classmethod
    def _pattern_value(cls, name: str, key: int) -> float:
        cached_table = cls.PATTERN_VALUE_TABLES.get(name)
        if cached_table is not None:
            return cached_table[key]
        return cls._compute_pattern_value(name, key)

    @classmethod
    def _pattern_value_table(cls, name: str):
        cached = cls.PATTERN_VALUE_TABLES.get(name)
        if cached is not None:
            return cached

        size = cls.PATTERN_SIZES[name]
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            table = tuple(cls._compute_pattern_value(name, key) for key in range(3 ** size))
        else:
            for key in range(3 ** size):
                if partial[key] is None:
                    partial[key] = cls._compute_pattern_value(name, key)
            table = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
        cls.PATTERN_VALUE_TABLES[name] = table
        cls.PATTERN_CACHE = {}
        return table

    @classmethod
    def _compute_pattern_value(cls, name: str, key: int) -> float:
        cache_key = (name, key)
        cached = cls.PATTERN_CACHE.get(cache_key)
        if cached is not None:
            return cached

        size, dense0, bias0, dense1, bias1, dense2, bias2 = cls._params()[0][name]
        arr = [0.0] * (size * 2)
        n = key
        for i in range(size - 1, -1, -1):
            digit = n % 3
            n //= 3
            if digit == 0:
                arr[i] = 1.0
            elif digit == 1:
                arr[size + i] = 1.0

        hidden0 = []
        for out_i in range(16):
            value = bias0[out_i]
            row = dense0[out_i]
            for in_i in range(size * 2):
                value += arr[in_i] * row[in_i]
            hidden0.append(cls._leaky_relu(value))

        result = bias2
        for out_i in range(16):
            value = bias1[out_i]
            row = dense1[out_i]
            for in_i in range(16):
                value += hidden0[in_i] * row[in_i]
            result += cls._leaky_relu(value) * dense2[out_i]

        result = cls._leaky_relu(result)
        cls.PATTERN_CACHE[cache_key] = result
        return result

    @classmethod
    def _add_value(cls, key: int) -> float:
        t0_mlp = time.perf_counter()
        res = cls._compute_add_value(key)
        cls._accum_eval_add_mlp_time += time.perf_counter() - t0_mlp
        return res

    @classmethod
    def _compute_add_value(cls, key: int) -> float:
        cached = cls.ADD_CACHE.get(key)
        if cached is not None:
            return cached

        tmp = key
        sur1 = tmp % 51
        tmp //= 51
        sur0 = tmp % 51
        mobility = tmp // 51 - 30
        arr = (mobility / 30.0, (sur0 - 15.0) / 15.0, (sur1 - 15.0) / 15.0)
        dense0, bias0, dense1, bias1 = cls._params()[1]

        hidden = []
        for out_i in range(8):
            value = bias0[out_i]
            row = dense0[out_i]
            for in_i in range(3):
                value += arr[in_i] * row[in_i]
            hidden.append(cls._leaky_relu(value))

        result = bias1
        for i in range(8):
            result += hidden[i] * dense1[i]
        result = cls._leaky_relu(result)
        cls.ADD_CACHE[key] = result
        return result

    @classmethod
    def _precompute_evaluation_tables(cls) -> None:
        for name in cls.PRECOMPUTED_PATTERN_NAMES:
            cls._pattern_value_table(name)

    @classmethod
    def _precompute_init_evaluation_tables(cls) -> None:
        for name in cls.INIT_PRECOMPUTED_PATTERN_NAMES:
            cls._pattern_value_table(name)

    @classmethod
    def _warm_init_evaluation_table_steps(cls) -> None:
        for _ in range(cls.INIT_WARM_TABLE_STEPS):
            if not cls._warm_evaluation_table_step():
                return

    @classmethod
    def _warm_evaluation_table_steps(cls) -> None:
        for _ in range(cls.WARM_TABLE_STEPS_PER_MOVE):
            if not cls._warm_evaluation_table_step():
                return

    @classmethod
    def _warm_evaluation_table_step(cls) -> bool:
        for name in cls.WARM_PATTERN_NAMES:
            if name not in cls.PATTERN_VALUE_TABLES:
                cls._warm_pattern_value_table_chunk(name)
                return True
        return False

    @classmethod
    def _warm_pattern_value_table_chunk(cls, name: str) -> None:
        size = cls.PATTERN_SIZES[name]
        total = 3 ** size
        partial = cls.PARTIAL_PATTERN_VALUE_TABLES.get(name)
        if partial is None:
            partial = [None] * total
            cls.PARTIAL_PATTERN_VALUE_TABLES[name] = partial

        start = cls.PARTIAL_PATTERN_VALUE_INDEXES.get(name, 0)
        end = min(total, start + cls.WARM_TABLE_CHUNK_SIZE)
        for key in range(start, end):
            partial[key] = cls._compute_pattern_value(name, key)

        if end >= total:
            cls.PATTERN_VALUE_TABLES[name] = tuple(partial)
            cls.PARTIAL_PATTERN_VALUE_TABLES.pop(name, None)
            cls.PARTIAL_PATTERN_VALUE_INDEXES.pop(name, None)
            cls.PATTERN_CACHE = {}
        else:
            cls.PARTIAL_PATTERN_VALUE_INDEXES[name] = end

    @staticmethod
    def _leaky_relu(value: float) -> float:
        if value >= 0.0:
            return value
        return 0.01 * value

    @classmethod
    def _pattern_bit_specs(cls):
        if cls.PATTERN_BIT_SPECS is not None:
            return cls.PATTERN_BIT_SPECS

        specs = {}
        for name, patterns in cls.PATTERN_INDEXES.items():
            group_specs = []
            for pattern in patterns:
                weight = 1
                empty_key = 0
                parts = []
                for index in reversed(pattern):
                    bit = 1 << index
                    empty_key += weight + weight
                    parts.append((bit, weight, weight + weight))
                    weight *= 3
                group_specs.append((empty_key, tuple(parts)))
            specs[name] = tuple(group_specs)
        cls.PATTERN_BIT_SPECS = specs
        return specs

    @classmethod
    def _pattern_key_meta(cls):
        if cls.PATTERN_KEY_META is not None:
            return cls.PATTERN_KEY_META

        specs = cls._pattern_bit_specs()
        empty_keys = []
        group_infos = []
        position_updates = [[] for _ in range(64)]
        key_index = 0
        for name in cls.ACTIVE_PATTERN_NAMES:
            start = key_index
            for empty_key, parts in specs[name]:
                empty_keys.append(empty_key)
                for bit, white_delta, _ in parts:
                    position = bit.bit_length() - 1
                    position_updates[position].append((key_index, white_delta))
                key_index += 1
            group_infos.append((name, start, key_index))

        cls.PATTERN_KEY_META = (
            tuple(empty_keys),
            tuple(tuple(items) for items in position_updates),
            tuple(group_infos),
        )
        return cls.PATTERN_KEY_META

    @classmethod
    def _pattern_key_group_infos(cls):
        return cls._pattern_key_meta()[2]

    def _pattern_keys_from_state(self, state: tuple[int, int]) -> tuple[int, ...]:
        empty_keys, position_updates, _ = MyPlayer._pattern_key_meta()
        keys = list(empty_keys)
        black_bits, white_bits = state

        bits = black_bits
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                keys[key_index] -= weight + weight
            bits ^= bit

        bits = white_bits
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                keys[key_index] -= weight
            bits ^= bit

        return tuple(keys)

    def _additional_key_bits(self, state: tuple[int, int]) -> int:
        cached = MyPlayer.ADDITIONAL_KEY_CACHE.get(state)
        if cached is not None:
            return cached

        t0_mob = time.perf_counter()
        mobility = self._mobility_diff_bits(state)
        MyPlayer._accum_eval_mobility_time += time.perf_counter() - t0_mob

        t0_sur = time.perf_counter()
        surround_black, surround_white = self._surround_counts_bits(state)
        MyPlayer._accum_eval_surround_time += time.perf_counter() - t0_sur

        mobility = max(-30, min(30, mobility))
        surround_black = max(0, min(50, surround_black))
        surround_white = max(0, min(50, surround_white))
        result = ((mobility + 30) * 51 + surround_black) * 51 + surround_white
        MyPlayer.ADDITIONAL_KEY_CACHE[state] = result
        return result

    def _mobility_diff_bits(self, state: tuple[int, int]) -> int:
        cached = MyPlayer.MOBILITY_CACHE.get(state)
        if cached is not None:
            return cached

        mobility = (
            self._legal_move_mask_bits(state, Cell.BLACK).bit_count()
            - self._legal_move_mask_bits(state, Cell.WHITE).bit_count()
        )
        MyPlayer.MOBILITY_CACHE[state] = mobility
        return mobility

    def _surround_counts_bits(self, state: tuple[int, int]) -> tuple[int, int]:
        black_bits, white_bits = state
        occupied = black_bits | white_bits
        empty_bits = self.FULL_MASK ^ occupied
        black_count = 0
        white_count = 0
        for direction in range(8):
            black_count += (empty_bits & self._shift_bits(black_bits, direction)).bit_count()
            white_count += (empty_bits & self._shift_bits(white_bits, direction)).bit_count()
        return (black_count, white_count)

    def _legal_moves_bits(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:
        key = self._legal_moves_cache_key_bits(state, color)
        cached = MyPlayer.LEGAL_MOVES_CACHE.get(key)
        if cached is not None:
            return cached

        moves = self._legal_moves_bits_uncached(state, color)
        self._legal_moves_cache_register(key, moves)
        return tuple(moves)

    def _legal_moves_bits_uncached(self, state: tuple[int, int], color: Cell) -> list[int]:
        legal_bits = self._legal_move_mask_bits(state, color)
        moves = []
        bits = legal_bits
        while bits:
            bit = bits & -bits
            moves.append(bit.bit_length() - 1)
            bits ^= bit
        return moves

    def _legal_move_mask_bits(self, state: tuple[int, int], color: Cell) -> int:
        key = self._legal_moves_cache_key_bits(state, color)
        cached = MyPlayer.LEGAL_MOVE_MASK_CACHE.get(key)
        if cached is not None:
            return cached

        black_bits, white_bits = state
        occupied = black_bits | white_bits
        empty = self.FULL_MASK ^ occupied
        own = black_bits if color == Cell.BLACK else white_bits
        opp = white_bits if color == Cell.BLACK else black_bits
        NOT_A = self.NOT_A_FILE
        NOT_H = self.NOT_H_FILE

        # Northwest (-9)
        c = opp & ((own & NOT_A) >> 9)
        c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9); c |= opp & ((c & NOT_A) >> 9)
        legal = empty & ((c & NOT_A) >> 9)

        # North (-8)
        c = opp & (own >> 8)
        c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8); c |= opp & (c >> 8)
        legal |= empty & (c >> 8)

        # Northeast (-7)
        c = opp & ((own & NOT_H) >> 7)
        c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7); c |= opp & ((c & NOT_H) >> 7)
        legal |= empty & ((c & NOT_H) >> 7)

        # West (-1)
        c = opp & ((own & NOT_A) >> 1)
        c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1); c |= opp & ((c & NOT_A) >> 1)
        legal |= empty & ((c & NOT_A) >> 1)

        # East (+1)
        c = opp & ((own & NOT_H) << 1)
        c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1); c |= opp & ((c & NOT_H) << 1)
        legal |= empty & ((c & NOT_H) << 1)

        # Southwest (+7)
        c = opp & ((own & NOT_A) << 7)
        c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7); c |= opp & ((c & NOT_A) << 7)
        legal |= empty & ((c & NOT_A) << 7)

        # South (+8)
        c = opp & (own << 8)
        c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8); c |= opp & (c << 8)
        legal |= empty & (c << 8)

        # Southeast (+9)
        c = opp & ((own & NOT_H) << 9)
        c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9); c |= opp & ((c & NOT_H) << 9)
        legal |= empty & ((c & NOT_H) << 9)

        MyPlayer.LEGAL_MOVE_MASK_CACHE[key] = legal
        return legal

    @classmethod
    def _shift_bits(cls, bits: int, direction: int) -> int:
        if direction == 0:  # north-west
            return ((bits & cls.NOT_A_FILE) >> 9) & cls.FULL_MASK
        if direction == 1:  # north
            return (bits >> 8) & cls.FULL_MASK
        if direction == 2:  # north-east
            return ((bits & cls.NOT_H_FILE) >> 7) & cls.FULL_MASK
        if direction == 3:  # west
            return ((bits & cls.NOT_A_FILE) >> 1) & cls.FULL_MASK
        if direction == 4:  # east
            return ((bits & cls.NOT_H_FILE) << 1) & cls.FULL_MASK
        if direction == 5:  # south-west
            return ((bits & cls.NOT_A_FILE) << 7) & cls.FULL_MASK
        if direction == 6:  # south
            return (bits << 8) & cls.FULL_MASK
        return ((bits & cls.NOT_H_FILE) << 9) & cls.FULL_MASK

    def _legal_moves_cache_key_bits(self, state: tuple[int, int], color: Cell) -> tuple[int, int, int]:
        color_key = 1 if color == Cell.BLACK else 2
        black_bits, white_bits = state
        return (black_bits, white_bits, color_key)

    @classmethod
    def _legal_moves_cache_register(
        cls,
        key: tuple[int, int, int],
        moves: tuple[int, ...] | list[int],
    ) -> None:
        if key not in cls.LEGAL_MOVES_CACHE and len(cls.LEGAL_MOVES_CACHE) >= cls.LEGAL_MOVES_CACHE_MAX_SIZE:
            cls.LEGAL_MOVES_CACHE.pop(next(iter(cls.LEGAL_MOVES_CACHE)))
        cls.LEGAL_MOVES_CACHE[key] = tuple(moves)

    def _apply_move_bits(self, state: tuple[int, int], pos: int, color: Cell) -> tuple[int, int]:
        flips = self._flips_bits(state, pos, color)
        move_bit = 1 << pos
        black_bits, white_bits = state
        if color == Cell.BLACK:
            black_bits |= flips | move_bit
            white_bits &= ~flips
        else:
            white_bits |= flips | move_bit
            black_bits &= ~flips
        return black_bits, white_bits

    def _apply_move_with_pattern_keys(
        self,
        state: tuple[int, int],
        pattern_keys: tuple[int, ...] | None,
        pos: int,
        color: Cell,
    ) -> tuple[tuple[int, int], tuple[int, ...]]:
        if pattern_keys is None:
            pattern_keys = self._pattern_keys_from_state(state)

        flips = self._flips_bits(state, pos, color)
        move_bit = 1 << pos
        black_bits, white_bits = state
        if color == Cell.BLACK:
            next_state = ((black_bits | flips | move_bit), (white_bits & ~flips))
        else:
            next_state = ((black_bits & ~flips), (white_bits | flips | move_bit))

        _, position_updates, _ = MyPlayer._pattern_key_meta()
        keys = list(pattern_keys)

        for key_index, weight in position_updates[pos]:
            if color == Cell.BLACK:
                keys[key_index] -= weight + weight
            else:
                keys[key_index] -= weight

        bits = flips
        while bits:
            bit = bits & -bits
            position = bit.bit_length() - 1
            for key_index, weight in position_updates[position]:
                if color == Cell.BLACK:
                    keys[key_index] -= weight
                else:
                    keys[key_index] += weight
            bits ^= bit

        return next_state, tuple(keys)

    def _flips_bits(self, state: tuple[int, int], pos: int, color: Cell) -> int:
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
            current = self._shift_bits(move_bit, direction)
            while current and current & opponent_bits:
                line |= current
                current = self._shift_bits(current, direction)
            if current & own_bits:
                flips |= line
        return flips

    @classmethod
    def _book_cache(cls):
        if cls.BOOK_CACHE is not None:
            return cls.BOOK_CACHE

        cache = {}
        for line in cls.BOOK_LINES:
            prefix = line[:-2]
            move_text = line[-2:]
            for transform in range(4):
                board = cls._initial_board()
                current_color = Cell.BLACK
                for i in range(0, len(prefix), 2):
                    move = cls._coord_to_move(prefix[i:i + 2], transform)
                    board = cls._apply_move_for_color(board, move, current_color)
                    current_color = Cell.WHITE if current_color == Cell.BLACK else Cell.BLACK
                cache[(cls._board_key(board), current_color)] = cls._coord_to_move(move_text, transform)

        cls.BOOK_CACHE = cache
        return cache

    def _book_move_bits(self, state: tuple[int, int]) -> Move:
        return self._book_cache().get((self._board_key_bits(state), self.color))

    @staticmethod
    def _initial_board() -> Board:
        board = [[Cell.EMPTY for _ in range(8)] for _ in range(8)]
        board[3][3] = Cell.WHITE
        board[3][4] = Cell.BLACK
        board[4][3] = Cell.BLACK
        board[4][4] = Cell.WHITE
        return board

    @staticmethod
    def _coord_to_move(coord: str, transform: int) -> Move:
        col = ord(coord[0]) - ord("a")
        row = int(coord[1]) - 1
        if transform == 0:
            return (row, col)
        if transform == 1:
            return (col, row)
        if transform == 2:
            return (7 - row, 7 - col)
        return (7 - col, 7 - row)

    @classmethod
    def _apply_move_for_color(cls, board: Board, move: Move, color: Cell) -> Board:
        row, col = move
        next_board = [board_row[:] for board_row in board]
        next_board[row][col] = color
        opponent_color = Cell.WHITE if color == Cell.BLACK else Cell.BLACK

        for delta_row, delta_col in cls.DIRECTIONS:
            direction_flips = []
            current_row = row + delta_row
            current_col = col + delta_col
            while (
                0 <= current_row < 8
                and 0 <= current_col < 8
                and board[current_row][current_col] == opponent_color
            ):
                direction_flips.append((current_row, current_col))
                current_row += delta_row
                current_col += delta_col

            if (
                direction_flips
                and 0 <= current_row < 8
                and 0 <= current_col < 8
                and board[current_row][current_col] == color
            ):
                for flip_row, flip_col in direction_flips:
                    next_board[flip_row][flip_col] = color

        return next_board

    @staticmethod
    def _board_key(board: Board) -> tuple[int, ...]:
        values = []
        for row in board:
            for cell in row:
                if cell == Cell.BLACK:
                    values.append(1)
                elif cell == Cell.WHITE:
                    values.append(2)
                else:
                    values.append(0)
        return tuple(values)

    @staticmethod
    def _board_key_bits(state: tuple[int, int]) -> tuple[int, ...]:
        black_bits, white_bits = state
        values = []
        for pos in range(64):
            bit = 1 << pos
            if black_bits & bit:
                values.append(1)
            elif white_bits & bit:
                values.append(2)
            else:
                values.append(0)
        return tuple(values)

    @staticmethod
    def _board_to_bits(board: Board) -> tuple[int, int]:
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

    @staticmethod
    def _move_to_pos(move: Move) -> int:
        row, col = move
        return row * 8 + col

    @staticmethod
    def _pos_to_move(pos: int) -> Move:
        return (pos // 8, pos % 8)

    def _opponent_of(self, color: Cell) -> Cell:
        if color == self.color:
            return self.opponent_color
        if color == self.opponent_color:
            return self.color
        return Cell.WHITE if color == Cell.BLACK else Cell.BLACK

    def _log_profile(self, total_time: float, is_book: bool, actual_turn: int):
        move_num = actual_turn

        eval_time = getattr(MyPlayer, "_accum_eval_time", 0.0)
        eval_hit_time = getattr(MyPlayer, "_accum_eval_hit_time", 0.0)
        eval_pat_time = getattr(MyPlayer, "_accum_eval_pattern_time", 0.0)
        eval_mob_time = getattr(MyPlayer, "_accum_eval_mobility_time", 0.0)
        eval_sur_time = getattr(MyPlayer, "_accum_eval_surround_time", 0.0)
        eval_mlp_time = getattr(MyPlayer, "_accum_eval_add_mlp_time", 0.0)

        book_time = getattr(self, "_t_book", 0.0)
        search_total = getattr(self, "_t_search", 0.0)
        search_other = max(0.0, search_total - eval_time)

        MyPlayer._accum_eval_time = 0.0
        MyPlayer._accum_eval_hit_time = 0.0
        MyPlayer._accum_eval_pattern_time = 0.0
        MyPlayer._accum_eval_mobility_time = 0.0
        MyPlayer._accum_eval_surround_time = 0.0
        MyPlayer._accum_eval_add_mlp_time = 0.0

        if total_time > 0:
            book_pct = (book_time / total_time) * 100
            eval_pct = (eval_time / total_time) * 100
            search_other_pct = (search_other / total_time) * 100
        else:
            book_pct = eval_pct = search_other_pct = 0.0

        tag = "[BOOK]  " if is_book else "[SEARCH]"
        log_str = f"{tag} Turn {move_num:2d} | Total: {total_time * 1000:7.2f} ms | Book: {book_time * 1000:6.2f} ms ({book_pct:5.1f}%) | Eval: {eval_time * 1000:7.2f} ms ({eval_pct:5.1f}%) | Search(Other): {search_other * 1000:7.2f} ms ({search_other_pct:5.1f}%)\n"

        if eval_time > 0:
            pat_pct = (eval_pat_time / eval_time) * 100
            mob_pct = (eval_mob_time / eval_time) * 100
            sur_pct = (eval_sur_time / eval_time) * 100
            mlp_pct = (eval_mlp_time / eval_time) * 100
            hit_pct = (eval_hit_time / eval_time) * 100
            eval_sub_str = f"         └─ [Eval Breakdown] Patterns: {eval_pat_time * 1000:7.2f} ms ({pat_pct:5.1f}%) | Mobility: {eval_mob_time * 1000:7.2f} ms ({mob_pct:5.1f}%) | Surround: {eval_sur_time * 1000:7.2f} ms ({sur_pct:5.1f}%) | AddMLP: {eval_mlp_time * 1000:7.2f} ms ({mlp_pct:5.1f}%) | CacheHit: {eval_hit_time * 1000:7.2f} ms ({hit_pct:5.1f}%)\n"
            log_str += eval_sub_str

        print(log_str, end="")
        log_file = "exp_043_profile_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_str)

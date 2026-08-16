"""Base experiment player with search algorithms and caching."""

try:
    from othellopy.core import Board, Cell, Move
    from othellopy.players import BasePlayer
except ImportError:
    try:
        from othellopy.board import Board, Cell, Move
        from othellopy.player import BasePlayer
    except ImportError:
        class BasePlayer:
            pass
        Board = list
        Cell = int
        Move = tuple[int, int]

from .constants import (
    BOARD_INDEXES,
    ORDER_WEIGHTS,
    DIRECTIONS,
    FULL_MASK,
    NOT_A_FILE,
    NOT_H_FILE,
)
from .patterns import (
    PATTERN_INDEXES,
    PATTERN_SIZES,
    ACTIVE_PATTERN_NAMES,
    PRECOMPUTED_PATTERN_NAMES,
    WARM_PATTERN_NAMES,
    INIT_PRECOMPUTED_PATTERN_NAMES,
    WARM_TABLE_CHUNK_SIZE,
    INIT_WARM_TABLE_STEPS,
    WARM_TABLE_STEPS_PER_MOVE,
)
from .weights import WEIGHTS
from .book import book_move_bits
from .bitboard import (
    shift_bits,
    board_to_bits,
    move_to_pos,
    pos_to_move,
    flips_bits,
    apply_move_bits,
    legal_move_mask_bits,
    legal_moves_bits_uncached,
    surround_counts_bits,
    empty_count_bits,
    terminal_score_for_color_bits,
)
from .evaluator import Evaluator


class BaseExperimentPlayer(BasePlayer):
    BOARD_INDEXES = BOARD_INDEXES
    SEARCH_DEPTH = 6
    ENDGAME_EXACT_EMPTY = 12
    SIMPLE_ALPHA_BETA_DEPTH = 2
    PROBCUT_MIN_DEPTH = 3
    PROBCUT_MARGIN = 0.16
    PROBCUT_SHALLOW_DEPTHS = (0, 0, 0, 1, 2, 1, 2, 3, 4, 3, 4, 3, 4, 5, 6)

    LEGAL_MOVES_CACHE_MAX_SIZE = 65536
    EVAL_CACHE_MAX_SIZE = 262144
    SEARCH_HASH_TABLE_SIZE = 16384
    SEARCH_HASH_MASK = SEARCH_HASH_TABLE_SIZE - 1

    FULL_MASK = FULL_MASK
    NOT_A_FILE = NOT_A_FILE
    NOT_H_FILE = NOT_H_FILE
    ORDER_WEIGHTS = ORDER_WEIGHTS
    DIRECTIONS = DIRECTIONS

    PATTERN_INDEXES = PATTERN_INDEXES
    PATTERN_SIZES = PATTERN_SIZES
    ACTIVE_PATTERN_NAMES = ACTIVE_PATTERN_NAMES
    PRECOMPUTED_PATTERN_NAMES = PRECOMPUTED_PATTERN_NAMES
    WARM_PATTERN_NAMES = WARM_PATTERN_NAMES
    INIT_PRECOMPUTED_PATTERN_NAMES = INIT_PRECOMPUTED_PATTERN_NAMES
    WARM_TABLE_CHUNK_SIZE = WARM_TABLE_CHUNK_SIZE
    INIT_WARM_TABLE_STEPS = INIT_WARM_TABLE_STEPS
    WARM_TABLE_STEPS_PER_MOVE = WARM_TABLE_STEPS_PER_MOVE
    WEIGHTS = WEIGHTS

    PARAMS = None
    PATTERN_CACHE = Evaluator.PATTERN_CACHE
    ADD_CACHE = Evaluator.ADD_CACHE
    PATTERN_VALUE_TABLES = Evaluator.PATTERN_VALUE_TABLES
    PARTIAL_PATTERN_VALUE_TABLES = Evaluator.PARTIAL_PATTERN_VALUE_TABLES
    PARTIAL_PATTERN_VALUE_INDEXES = Evaluator.PARTIAL_PATTERN_VALUE_INDEXES
    ADDITIONAL_KEY_CACHE = Evaluator.ADDITIONAL_KEY_CACHE
    MOBILITY_CACHE = Evaluator.MOBILITY_CACHE
    LEGAL_MOVE_MASK_CACHE = {}
    LEGAL_MOVES_CACHE = {}
    EVAL_CACHE = Evaluator.EVAL_CACHE
    SEARCH_HASH_TABLE = [None] * SEARCH_HASH_TABLE_SIZE
    SEARCH_HASH_GET_COUNT = 0
    SEARCH_HASH_REG_COUNT = 0

    PATTERN_BIT_SPECS = None
    PATTERN_KEY_META = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Evaluator.pattern_bit_specs()
        Evaluator.pattern_key_meta()
        Evaluator.precompute_init_evaluation_tables()
        Evaluator.warm_init_evaluation_table_steps()

    def next_move(self, board: Board) -> Move:
        Evaluator.pattern_bit_specs()
        BaseExperimentPlayer.SEARCH_HASH_GET_COUNT = 0
        BaseExperimentPlayer.SEARCH_HASH_REG_COUNT = 0
        state = board_to_bits(board)
        pattern_keys = Evaluator.pattern_keys_from_state(state)
        moves = self._legal_moves_bits(state, self.color)
        if not moves:
            return None
        Evaluator.warm_evaluation_table_steps()

        book_move = book_move_bits(state, self.color)
        if book_move is not None and move_to_pos(book_move) in moves:
            return book_move

        best_move = moves[0]
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        if empty_count_bits(state) <= self.ENDGAME_EXACT_EMPTY:
            ordered_moves = self._order_moves_by_opponent_mobility(state, moves, self.color)
            for move in ordered_moves:
                next_state = apply_move_bits(state, move, self.color)
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

            return pos_to_move(best_move)

        ordered_moves = self._order_move_positions_by_weight(moves)
        for move in ordered_moves:
            next_state, next_pattern_keys = Evaluator.apply_move_with_pattern_keys(
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

        return pos_to_move(best_move)

    def _opponent_of(self, color: Cell) -> Cell:
        return Cell.WHITE if color == Cell.BLACK else Cell.BLACK

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
            key=lambda move: legal_move_mask_bits(
                apply_move_bits(state, move, current_color),
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
                return terminal_score_for_color_bits(state, current_color)
            return -self._endgame_exact_search(state, next_color, -beta, -alpha)

        best_score = -65
        moves = self._order_moves_by_opponent_mobility(state, moves, current_color)
        for move in moves:
            next_state = apply_move_bits(state, move, current_color)
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
        if depth == 0:
            return Evaluator.evaluate_for_color_bits(state, current_color, pattern_keys)

        original_alpha = alpha
        original_beta = beta
        search_key = self._search_hash_key(state, depth, current_color, allow_probcut)
        cached = self._search_hash_get(search_key, alpha, beta)
        if cached is not None:
            return cached

        if depth <= self.SIMPLE_ALPHA_BETA_DEPTH:
            score = self._alpha_beta_simple(state, pattern_keys, depth, current_color, alpha, beta)
            self._search_hash_register(search_key, score, original_alpha, original_beta)
            return score

        moves = self._legal_moves_bits(state, current_color)
        next_color = self._opponent_of(current_color)

        if not moves:
            if not self._legal_moves_bits(state, next_color):
                score = terminal_score_for_color_bits(state, current_color)
            else:
                score = -self._negascout(state, pattern_keys, depth, next_color, -beta, -alpha, allow_probcut)
            self._search_hash_register(search_key, score, original_alpha, original_beta)
            return score

        if allow_probcut and depth >= self.PROBCUT_MIN_DEPTH:
            cut_score = self._probcut(state, pattern_keys, depth, current_color, alpha, beta)
            if cut_score is not None:
                self._search_hash_register(search_key, cut_score, original_alpha, original_beta)
                return cut_score

        moves = self._order_move_positions_by_weight(moves)
        children = []
        for move in moves:
            next_state, next_pattern_keys = Evaluator.apply_move_with_pattern_keys(
                state, pattern_keys, move, current_color
            )
            order_score = 0.0
            if depth >= 2 and len(moves) > 1:
                order_score = Evaluator.evaluate_for_color_bits(next_state, current_color, next_pattern_keys)
            children.append((move, next_state, next_pattern_keys, order_score))
        if depth >= 2 and len(children) > 1:
            children.sort(key=lambda child: child[3], reverse=True)

        search_window = beta
        best_score = float("-inf")

        for index, child in enumerate(children):
            next_state = child[1]
            next_pattern_keys = child[2]
            score = -self._negascout(
                next_state, next_pattern_keys, depth - 1, next_color, -search_window, -alpha, allow_probcut
            )

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
            return Evaluator.evaluate_for_color_bits(state, current_color, pattern_keys)

        moves = self._legal_moves_bits(state, current_color)
        next_color = self._opponent_of(current_color)

        if not moves:
            if not self._legal_moves_bits(state, next_color):
                return terminal_score_for_color_bits(state, current_color)
            return -self._alpha_beta_simple(state, pattern_keys, depth, next_color, -beta, -alpha)

        best_score = float("-inf")
        for move in moves:
            next_state, next_pattern_keys = Evaluator.apply_move_with_pattern_keys(
                state, pattern_keys, move, current_color
            )
            score = -self._alpha_beta_simple(next_state, next_pattern_keys, depth - 1, next_color, -beta, -alpha)
            best_score = max(best_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_score

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
        estimate = Evaluator.evaluate_for_color_bits(state, current_color, pattern_keys)
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

    def _legal_moves_bits(self, state: tuple[int, int], color: Cell) -> tuple[int, ...]:
        key = self._legal_moves_cache_key_bits(state, color)
        cached = BaseExperimentPlayer.LEGAL_MOVES_CACHE.get(key)
        if cached is not None:
            return cached

        moves = legal_moves_bits_uncached(state, color)
        self._legal_moves_cache_register(key, moves)
        return tuple(moves)

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

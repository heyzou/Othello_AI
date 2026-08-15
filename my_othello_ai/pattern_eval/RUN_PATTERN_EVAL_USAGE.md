# run_pattern_eval.sh Usage

Run from `my_othello_ai/pattern_eval`:

```bash
bash ./scripts/run_pattern_eval.sh current.py 1
```

Run an experiment:

```bash
bash ./scripts/run_pattern_eval.sh exp_010_bitboard.py 1
```

The second argument is the number of games per side. `1` means one black game and one white game.

## Test Mode

Use `-test` to disable the 2.0 second move timeout. This lets a slow `next_move()` keep running so you can see how long it actually takes.

```bash
bash ./scripts/run_pattern_eval.sh -test exp_010_bitboard.py 1
```

In normal mode, `OthelloGame` receives `move_timeout_seconds=2.0`.

In test mode, the script sets:

```bash
MOVE_TIMEOUT_SECONDS=none
```

The timing logs printed by the player still appear in the terminal.

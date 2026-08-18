import sys

def run_test():
    from players.experiments.exp_071_080.exp_079 import MyPlayer
    from othellopy.game import Cell
    
    player = MyPlayer(Cell.BLACK)
    print("After init:")
    print("PATTERN_VALUE_TABLES keys:", list(MyPlayer.PATTERN_VALUE_TABLES.keys()))
    print("EVALUATE_PATTERNS_TABLES is None:", MyPlayer.EVALUATE_PATTERNS_TABLES is None)

    for turn in range(1, 40):
        MyPlayer._warm_evaluation_table_steps_black(turn)

    print("After warmup:")
    print("PATTERN_VALUE_TABLES keys:", list(MyPlayer.PATTERN_VALUE_TABLES.keys()))
    
    res = MyPlayer._ensure_evaluate_patterns_tables_black()
    print("_ensure_evaluate_patterns_tables_black returned:", res)
    print("EVALUATE_PATTERNS_TABLES is None:", MyPlayer.EVALUATE_PATTERNS_TABLES is None)

if __name__ == "__main__":
    code = ""
    with open("players/experiments/exp_071_080/exp_079.py", "r") as f:
        code = f.read()
    
    import othellopy.game
    namespace = {"BasePlayer": othellopy.game.BasePlayer, "Move": othellopy.game.Move, "Cell": othellopy.game.Cell, "Board": othellopy.game.Board}
    exec(code, namespace)
    
    MyPlayer = namespace["MyPlayer"]
    Cell = othellopy.game.Cell
    player = MyPlayer(Cell.BLACK)
    print("After init:")
    print("PATTERN_VALUE_TABLES keys:", list(MyPlayer.PATTERN_VALUE_TABLES.keys()))
    
    for turn in range(1, 40):
        MyPlayer._warm_evaluation_table_steps_black(turn)

    print("After warmup:")
    print("PATTERN_VALUE_TABLES keys:", list(MyPlayer.PATTERN_VALUE_TABLES.keys()))
    
    res = MyPlayer._ensure_evaluate_patterns_tables_black()
    print("_ensure_evaluate_patterns_tables_black returned:", res)
    print("EVALUATE_PATTERNS_TABLES is None:", MyPlayer.EVALUATE_PATTERNS_TABLES is None)

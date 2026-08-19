import glob
import os
from pathlib import Path


def parse_wtb_file(fpath):
    records = []
    with open(fpath, "rb") as f:
        header = f.read(16)
        while True:
            rec = f.read(68)
            if not rec or len(rec) < 68:
                break
            moves = rec[8:68]
            move_str = ""
            for m in moves:
                if m == 0:
                    break
                col = (m % 10) - 1
                row = (m // 10) - 1
                if 0 <= col <= 7 and 0 <= row <= 7:
                    move_str += chr(ord("a") + col) + str(row + 1)
            if len(move_str) >= 8:
                records.append(move_str)
    return records


def load_all_records(base_dir: Path):
    records = []
    # 1. Existing text records
    txt_files = sorted(glob.glob(str(base_dir / "training_records" / "[0-9]*.txt")))
    print(f"Loading {len(txt_files)} txt record files...")
    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as f:
            records.extend(list(f.read().splitlines()))

    # 2. WTH_2017.wtb ~ WTH_2023.wtb
    wtb_files = sorted(glob.glob(str(base_dir / "WTH_*.wtb")))
    print(f"Loading {len(wtb_files)} WTB files (2017-2023)...")
    for wtb_file in wtb_files:
        wtb_records = parse_wtb_file(wtb_file)
        print(f"  - {os.path.basename(wtb_file)}: {len(wtb_records)} games")
        records.extend(wtb_records)

    print(f"Total games loaded: {len(records)}")
    return records


# --- Fast Bitboard Othello Simulator ---
SHIFT_DIRS = (
    (1, 0x7E7E7E7E7E7E7E7E),   # East
    (-1, 0x7E7E7E7E7E7E7E7E),  # West
    (8, 0x00FFFFFFFFFFFF00),   # South
    (-8, 0x00FFFFFFFFFFFF00),  # North
    (7, 0x007E7E7E7E7E7E00),   # SW
    (-7, 0x007E7E7E7E7E7E00),  # NE
    (9, 0x007E7E7E7E7E7E00),   # SE
    (-9, 0x007E7E7E7E7E7E00),  # NW
)


def get_flips(black, white, pos, is_black):
    own = black if is_black else white
    opp = white if is_black else black
    move_bit = 1 << pos
    if (black | white) & move_bit:
        return 0

    flips = 0
    for shift, mask in SHIFT_DIRS:
        c = 0
        if shift > 0:
            cursor = (move_bit << shift) & mask & opp
            while cursor:
                c |= cursor
                cursor = (cursor << shift) & mask & opp
            if (move_bit << shift) and ((c << shift) & own):
                flips |= c
        else:
            ushift = -shift
            cursor = (move_bit >> ushift) & mask & opp
            while cursor:
                c |= cursor
                cursor = (cursor >> ushift) & mask & opp
            if (move_bit >> ushift) and ((c >> ushift) & own):
                flips |= c
    return flips


def has_legal_moves(black, white, is_black):
    for pos in range(64):
        if get_flips(black, white, pos, is_black):
            return True
    return False


def pos_to_coord(pos):
    col = pos % 8
    row = pos // 8
    return chr(ord("a") + col) + str(row + 1)


def coord_to_pos(coord):
    col = ord(coord[0]) - ord("a")
    row = int(coord[1]) - 1
    return row * 8 + col


def build_book(records, max_ln=45, num_threshold=4):
    record_all = {}
    print("Simulating games with fast bitboard engine...")
    
    valid_count = 0
    for record in records:
        # Initial board
        # e4(pos 28): Black, d5(pos 35): Black
        # d4(pos 27): White, e5(pos 36): White
        black = (1 << 28) | (1 << 35)
        white = (1 << 27) | (1 << 36)
        is_black = True
        
        valid = True
        move_history = []
        for i in range(0, len(record), 2):
            move_str = record[i:i + 2]
            pos = coord_to_pos(move_str)
            
            flips = get_flips(black, white, pos, is_black)
            if not flips:
                # Check if current player had to pass
                if not has_legal_moves(black, white, is_black):
                    is_black = not is_black
                    flips = get_flips(black, white, pos, is_black)
                if not flips:
                    valid = False
                    break
            
            move_bit = 1 << pos
            if is_black:
                black |= move_bit | flips
                white &= ~flips
            else:
                white |= move_bit | flips
                black &= ~flips
            
            is_black = not is_black
            move_history.append(move_str)

        if not valid or len(move_history) < 4:
            continue

        valid_count += 1
        b_stones = black.bit_count()
        w_stones = white.bit_count()
        vacant = 64 - (b_stones + w_stones)
        result = b_stones - w_stones
        if result > 0:
            result += vacant
        elif result < 0:
            result -= vacant

        # Aggregate stats for each prefix
        prefix = ""
        for m in move_history:
            prefix += m
            if prefix in record_all:
                record_all[prefix][0] += 1
                record_all[prefix][1] += result
            else:
                record_all[prefix] = [1, result]

    print(f"Successfully processed {valid_count} games! (Unique state prefixes: {len(record_all)})")

    book = {}
    inf = 100000000

    def calc_value(r, player):
        if r in record_all:
            count, total_res = record_all[r]
            if count < num_threshold:
                return -inf
            val = total_res / count
            return -val if player == 1 else val
        return -inf

    def create_book(record, player):
        if len(record) > max_ln:
            return

        policy = -1
        max_val = -inf
        for pos in range(64):
            coord = pos_to_coord(pos)
            r = record + coord
            val = calc_value(r, player)
            if val > max_val:
                max_val = val
                policy = coord

        if policy != -1:
            book[record] = policy
            for pos in range(64):
                coord = pos_to_coord(pos)
                next_record = record + policy + coord
                if next_record in record_all:
                    create_book(next_record, player)

    print("Creating book tree...")
    create_book("f5", 1)
    print(f"Book size after f5: {len(book)}")
    create_book("f5d6", 0)
    create_book("f5f6", 0)
    create_book("f5f4", 0)
    print(f"Book size after all openings: {len(book)}")

    return book


def main():
    base_dir = Path(__file__).resolve().parent
    records = load_all_records(base_dir)
    book = build_book(records, max_ln=45, num_threshold=4)

    # Save to new file: book_2017_2023.txt
    output_path = base_dir / "book" / "book_2017_2023.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("f5\n")
        for r in sorted(book.keys(), key=lambda k: (len(k), k)):
            f.write(r + book[r] + "\n")

    print(f"\n[SUCCESS] New opening book saved to: {output_path}")
    print(f"Total unique book positions: {len(book) + 1}")


if __name__ == "__main__":
    main()

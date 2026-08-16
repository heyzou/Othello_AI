import urllib.request
import os

base_url = 'http://www.ffothello.org/wthor/base/'
files_to_download = ['WTHOR.WTB', 'WTH_2023.wtb', 'WTH_2022.wtb', 'WTH_2021.wtb', 'WTH_2020.wtb', 'WTH_2019.wtb', 'WTH_2018.wtb', 'WTH_2017.wtb']

output_txt = '/home/nakai/Othello_AI/reference_non_submission/training_records/WTHOR_all.txt'

all_records = []

for file_name in files_to_download:
    url = base_url + file_name
    print(f"Downloading {file_name}...")
    try:
        urllib.request.urlretrieve(url, file_name)
        with open(file_name, 'rb') as f:
            header = f.read(16)
            while True:
                record = f.read(68)
                if not record or len(record) < 68:
                    break
                moves = record[8:68]
                move_str = ""
                for m in moves:
                    if m == 0:
                        break
                    col = (m % 10) - 1
                    row = (m // 10) - 1
                    if 0 <= col <= 7 and 0 <= row <= 7:
                        move_str += chr(ord('a') + col) + str(row + 1)
                
                if len(move_str) >= 20: # At least 10 moves
                    all_records.append(move_str)
        print(f"Parsed {file_name}")
    except Exception as e:
        print(f"Failed to process {file_name}: {e}")

with open(output_txt, 'w') as f:
    f.write("\n".join(all_records))

print(f"Successfully processed {len(all_records)} games into {output_txt}")

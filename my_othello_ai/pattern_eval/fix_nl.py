with open("players/experiments/exp_071_080/exp_079.py", "r") as f:
    text = f.read()

text = text.replace('%)\n")', '%)\\n")')

with open("players/experiments/exp_071_080/exp_079.py", "w") as f:
    f.write(text)

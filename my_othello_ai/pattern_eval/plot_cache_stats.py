import json
import matplotlib.pyplot as plt
import numpy as np

with open('cache_stats_32.json', 'r') as f:
    stats = json.load(f)

tables = []
hits = []
misses = []
totals = []
hit_rates = []

for k, v in stats.items():
    tables.append(k)
    h = v[0]
    m = v[1]
    t = h + m
    hits.append(h)
    misses.append(m)
    totals.append(t)
    hit_rates.append((h / t * 100) if t > 0 else 0)

x = np.arange(len(tables))
width = 0.35

fig, ax1 = plt.subplots(figsize=(10, 6))

bars1 = ax1.bar(x - width/2, hits, width, label='Hits', color='limegreen')
bars2 = ax1.bar(x - width/2, misses, width, bottom=hits, label='Misses', color='lightcoral')

ax1.set_ylabel('Total Queries (Calls)')
ax1.set_title('Cache Table Effectiveness (Turn 32)')
ax1.set_xticks(x)
ax1.set_xticklabels(tables, rotation=45, ha='right')
ax1.legend(loc='upper left')

ax2 = ax1.twinx()
ax2.set_ylabel('Hit Rate (%)', color='royalblue')
lines = ax2.plot(x + width/2, hit_rates, color='royalblue', marker='o', linestyle='-', linewidth=2, markersize=8, label='Hit Rate %')
ax2.tick_params(axis='y', labelcolor='royalblue')
ax2.set_ylim(-5, 105)

for i, v in enumerate(hit_rates):
    ax2.text(x[i] + width/2, v + 2, f"{v:.1f}%", color='royalblue', ha='center', fontweight='bold')

fig.tight_layout()
plt.savefig('/home/nakai/Othello_AI/my_othello_ai/pattern_eval/cache_stats_plot.png')
print("Plotted successfully!")

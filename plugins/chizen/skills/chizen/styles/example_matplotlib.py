"""Tiny example of the CHI Zen matplotlib style.

    python3 example_matplotlib.py            # writes example_matplotlib.pdf next to this file

Two series over time, distinguishable in black and white (colour, dash and marker), with the
legend centred below the plot. The numbers are made up for the example only.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
plt.style.use(HERE / "chizen.mplstyle")

months = list(range(1, 13))
users = [150, 180, 210, 260, 300, 320, 360, 400, 430, 470, 520, 560]    # example values
threads = [120, 130, 160, 170, 210, 230, 240, 280, 300, 310, 350, 380]  # example values

fig, ax = plt.subplots(layout="constrained")
ax.plot(months, users, label="Distinct users")
ax.plot(months, threads, label="Active threads")
ax.set_xlabel("Month")
ax.set_ylabel("Count per month")
ax.set_ylim(bottom=0)
fig.legend(loc="outside lower center", ncols=3)
fig.savefig(HERE / "example_matplotlib.pdf")
print("wrote", HERE / "example_matplotlib.pdf")

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from pathlib import Path


def plot_variant_1(
    X1: npt.NDArray[np.float64], X2: npt.NDArray[np.float64], dest: Path
) -> None:
    fig = plt.figure(figsize=(9, 6), dpi=300)
    ax = plt.subplot()
    X = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

    rects = ax.bar(X[::2] + 0.2, X1.mean(axis=1).astype(np.int64), width=0.5)
    ax.bar_label(rects, padding=3)

    rects = ax.bar(X[1::2] - 0.2, X2.mean(axis=1).astype(np.int64), width=0.5)
    ax.bar_label(rects, padding=3)

    ax.xaxis.set_ticks(
        X[::2] + 0.5,
        [
            "4\xD74",
            "8\xD78",
            "16\xD716",
            "32\xD732",
            "64\xD764",
        ],
        fontsize=12,
        family="serif",
    )
    ax.grid(alpha=0.5)
    fig.savefig(dest.as_posix())

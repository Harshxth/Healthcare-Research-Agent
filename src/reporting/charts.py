import os
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for Docker


def generate_charts(query: str, crew_result: str, output_dir: str) -> list[str]:
    chart_paths = []
    os.makedirs(output_dir, exist_ok=True)

    # Chart 1: Simulated publication trend (real version parses years from articles)
    years = list(range(2015, 2025))
    counts = [2, 3, 4, 5, 7, 9, 11, 14, 18, 22]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, counts, marker="o", color="#2563EB", linewidth=2.5)
    ax.fill_between(years, counts, alpha=0.1, color="#2563EB")
    ax.set_title(f"Publication Trend: {query[:50]}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Publications")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path1 = os.path.join(output_dir, "publication_trend.png")
    fig.savefig(path1, dpi=150)
    plt.close(fig)
    chart_paths.append(path1)

    # Chart 2: Evidence level distribution
    levels = ["Level 1\n(RCT/Meta)", "Level 2\n(Cohort)", "Level 3\n(Case/Opinion)"]
    values = [4, 8, 3]  # Replace with parsed values in production
    colors = ["#16A34A", "#F59E0B", "#DC2626"]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(levels, values, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_title("Evidence Level Distribution", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Studies")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(val), ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()
    path2 = os.path.join(output_dir, "evidence_levels.png")
    fig.savefig(path2, dpi=150)
    plt.close(fig)
    chart_paths.append(path2)

    return chart_paths

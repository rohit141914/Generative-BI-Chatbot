import os, re, uuid
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_COL_RE = re.compile(r"(date|month|year|period|week|quarter)", re.IGNORECASE)

def _detect_chart_type(columns, rows):
    if len(columns) < 2:
        return "bar"
    if DATE_COL_RE.search(columns[0]):
        return "line"
    if len(columns) == 2 and len(rows) <= 8:
        return "pie"
    return "bar"

def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": "#ffffff", "axes.facecolor": "#f8f8f8",
        "axes.edgecolor": "#cccccc", "axes.labelcolor": "#333333",
        "text.color": "#333333", "xtick.color": "#555555",
        "ytick.color": "#555555", "grid.color": "#e0e0e0",
        "font.size": 11,
    })

def render_chart(rows, session_id, chart_type=None):
    if not rows:
        return "none", ""
    columns = list(rows[0].keys())
    if len(columns) < 2:
        return "none", ""

    label_col = columns[0]
    value_col = columns[1]
    labels = [str(r[label_col]) for r in rows]
    values = [r[value_col] for r in rows]
    detected = chart_type or _detect_chart_type(columns, rows)

    COLORS = ["#4A7FD4","#E87C45","#52A77A","#C95FAB","#D4A843","#6A6AD4","#D45A5A","#5AB8D4"]
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5))

    if detected == "line":
        ax.plot(labels, values, marker="o", color="#4A7FD4", linewidth=2, markersize=5)
        ax.fill_between(range(len(labels)), values, alpha=0.12, color="#4A7FD4")
        ax.set_xlabel(label_col)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    elif detected == "pie":
        ax.pie(values, labels=labels, colors=COLORS[:len(labels)],
               autopct="%1.1f%%", startangle=140)
        ax.axis("equal")
    else:
        bar_colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
        bars = ax.bar(labels, values, color=bar_colors, edgecolor="white")
        ax.tick_params(axis="x", rotation=45)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.01,
                    f"{val:,.0f}", ha="center", va="bottom", fontsize=9)

    ax.set_title(f"{value_col} by {label_col}", pad=12, fontsize=13)
    fig.tight_layout()
    filename = f"chart_{session_id}_{uuid.uuid4().hex[:6]}.png"
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=120, bbox_inches="tight")
    plt.close(fig)
    return detected, f"/outputs/{filename}"

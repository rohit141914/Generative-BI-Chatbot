import os, re, uuid
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_COL_RE = re.compile(r"(date|month|year|period|week|quarter)", re.IGNORECASE)

COLORS = ["#4A7FD4","#E87C45","#52A77A","#C95FAB","#D4A843","#6A6AD4","#D45A5A","#5AB8D4"]

def _detect_chart_type(columns, rows):
    num_value_cols = len(columns) - 1
    has_date = DATE_COL_RE.search(columns[0])

    if num_value_cols >= 2 and has_date:
        return "multi_line"
    if num_value_cols >= 2:
        return "grouped_bar"
    if has_date:
        return "line"
    if num_value_cols == 1 and len(rows) <= 4:
        return "pie"
    return "bar"

def _apply_style():
    plt.rcParams.update({
        "figure.facecolor": "#0d1117", "axes.facecolor": "#161b22",
        "axes.edgecolor": "#30363d", "axes.labelcolor": "#c9d1d9",
        "text.color": "#c9d1d9", "xtick.color": "#8b949e",
        "ytick.color": "#8b949e", "grid.color": "#21262d",
        "font.size": 11,
    })

def _safe_floats(rows, col):
    out = []
    for r in rows:
        try:
            out.append(float(r[col]) if r[col] is not None else 0.0)
        except (ValueError, TypeError):
            out.append(0.0)
    return out

def render_chart(rows, session_id, chart_type=None):
    if not rows:
        return "none", ""
    columns = list(rows[0].keys())
    if len(columns) < 2:
        return "none", ""

    label_col = columns[0]
    value_cols = columns[1:]
    labels = [str(r[label_col]) for r in rows]

    chart_type = _detect_chart_type(columns, rows)
    print(f"chart{chart_type}")

    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5))

    if chart_type == "multi_line":
        x = np.arange(len(labels))
        for i, vc in enumerate(value_cols):
            vals = _safe_floats(rows, vc)
            color = COLORS[i % len(COLORS)]
            ax.plot(x, vals, marker="o", color=color, linewidth=2,
                    markersize=5, label=vc)
            ax.fill_between(x, vals, alpha=0.07, color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.margins(x=0)
        ax.set_xlim(x[0] - 0.3, x[-1] + 0.3)
        ax.set_xlabel(label_col)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.legend(facecolor="#1c2128", edgecolor="#30363d", labelcolor="#c9d1d9")

    elif chart_type == "grouped_bar":
        x = np.arange(len(labels))
        width = 0.8 / len(value_cols)
        for i, vc in enumerate(value_cols):
            vals = _safe_floats(rows, vc)
            offset = (i - (len(value_cols) - 1) / 2) * width
            bars = ax.bar(x + offset, vals, width, color=COLORS[i % len(COLORS)],
                          label=vc, edgecolor="#0d1117")
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                        f"{val:,.0f}", ha="center", va="bottom", fontsize=8, color="#c9d1d9")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.legend(facecolor="#1c2128", edgecolor="#30363d", labelcolor="#c9d1d9")

    elif chart_type == "line":
        x = np.arange(len(labels))
        vals = _safe_floats(rows, value_cols[0])
        ax.plot(x, vals, marker="o", color="#4A7FD4", linewidth=2, markersize=5)
        ax.fill_between(x, vals, alpha=0.12, color="#4A7FD4")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.margins(x=0)
        ax.set_xlim(x[0] - 0.3, x[-1] + 0.3)
        ax.set_xlabel(label_col)
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    elif chart_type == "pie":
        vals = _safe_floats(rows, value_cols[0])
        ax.pie(vals, labels=labels, colors=COLORS[:len(labels)],
               autopct="%1.1f%%", startangle=140)
        ax.axis("equal")

    else:  # bar
        vals = _safe_floats(rows, value_cols[0])
        bar_colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
        bars = ax.bar(labels, vals, color=bar_colors, edgecolor="white")
        ax.tick_params(axis="x", rotation=45)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                    f"{val:,.0f}", ha="center", va="bottom", fontsize=9, color="#c9d1d9")

    title_vals = ", ".join(value_cols)
    ax.set_title(f"{title_vals} by {label_col}", pad=12, fontsize=13)
    fig.tight_layout()
    filename = f"chart_{session_id}_{uuid.uuid4().hex[:6]}.png"
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=120, bbox_inches="tight")
    plt.close(fig)
    return chart_type, f"/outputs/{filename}"

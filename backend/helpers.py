def answer_text(rows):
    if not rows:
        return "No results found."
    cols = list(rows[0].keys())
    label_col = cols[0]
    value_col = cols[1] if len(cols) > 1 else None
    if value_col:
        top = rows[0]
        try:
            val = f"{float(top[value_col]):,.2f}"
        except:
            val = str(top[value_col])
        return f"{top[label_col]} has the highest {value_col} ({val}) across {len(rows)} result(s)."
    return f"Query returned {len(rows)} result(s)."

def suggestions(question):
    q = question.lower()
    tips = []
    if "state" in q:
        tips.append("Break this down by product type")
    if "trend" not in q:
        tips.append("Show the monthly trend for 2024")
    if "npa" not in q:
        tips.append("Filter for NPA loans only")
    return tips[:3]

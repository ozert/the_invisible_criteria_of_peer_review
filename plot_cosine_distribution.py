"""
Distribution of the chunk-level fidelity scores (Sentence-BERT cosine similarity,
`cosine_similarity_after_regex`) for all 809 question chunks extracted from the 304 reviews with
successful question separation. Same plotting style as the EDA notebook (plotly, "seaborn"
template, black bar outlines, PNG at scale 3). Scores below 0.80 are capped into the first bar
("<0.80"), as the word-count histograms cap their long tail.

Usage: python plot_cosine_distribution.py <replication repo root> <output dir>
"""
import json, sys, collections
from pathlib import Path
import numpy as np
import plotly.graph_objects as go

repo, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
src = repo / "data/Main Corpus/1 - Question Separation/llm_found_informative_question_separation_found_informant_reviews.json"
reviews = json.loads(src.read_text(encoding="utf-8"))
chunks = [(r["review_id"], float(c["cosine_similarity_after_regex"])) for r in reviews for c in (r["separated_questions"] or [])]
x = np.array([s for _, s in chunks]); TAU = 0.85

# 1. Cap the long lower tail: the 34 chunks below 0.80 are shown together in one bar ("<0.80").
#    Bin edges fall on multiples of 0.01, so the threshold 0.85 lies on a bin edge; scores of 1.0
#    (and floating-point values of 1.0000001) fall into the last bin, 0.99-1.00.
cap_limit = 0.80
x_capped = np.where(x < cap_limit, cap_limit - 0.005, np.minimum(x, 0.99999))

# 2. Plot: bins of width 0.01 from 0.80 to 1.00, plus the capped bar; logarithmic count axis
#    because 720 of the 809 chunks score exactly 1.0.
fig = go.Figure(
    data=[
        go.Histogram(
            x=x_capped,
            xbins=dict(start=cap_limit - 0.01, end=1.00, size=0.01),
            marker=dict(line=dict(color="black", width=1)),
        )
    ]
)
fig.update_layout(
    xaxis_title="Cosine Similarity (Fidelity Score)",
    yaxis_title="Number of Question Chunks",
    showlegend=False,
    margin=dict(l=5, r=10, t=10, b=5),
    template="seaborn",
)
fig.add_vline(x=TAU, line_dash="dash", line_color="firebrick", line_width=2,
              annotation_text="τ = 0.85", annotation_position="top left")

# 3. X-axis stops at 1.00, the first tick marks the capped bar
ticks = [cap_limit - 0.005, 0.85, 0.90, 0.95, 1.00]
fig.update_xaxes(range=[cap_limit - 0.012, 1.003], tickvals=ticks, ticktext=["<0.80", "0.85", "0.90", "0.95", "1.00"], tickangle=0)
fig.update_yaxes(type="log", tickvals=[1, 10, 100, 1000], ticktext=["1", "10", "100", "1000"])

# 4. Save
fig.write_image(str(out / "cosine_similarity_histogram_capped.png"), scale=3)
fig.write_image(str(out / "cosine_similarity_histogram_capped.pdf"))

# tables for the appendix
q = dict(zip(["Min", "P1", "P5", "P10", "Q1", "Median", "Max"], np.quantile(x, [0, .01, .05, .10, .25, .5, 1])))
print("n =", len(x), "| mean = %.3f" % x.mean(), "| " + " | ".join(f"{k} = {v:.3f}" for k, v in q.items()))
bands = [(0, .80), (.80, .85), (.85, .90), (.90, .95), (.95, .99), (.99, 1.0001)]
print("bands:", [int(((x >= lo) & (x < hi)).sum()) for lo, hi in bands])
counts, edges = np.histogram(x_capped, bins=np.round(np.arange(cap_limit - 0.01, 1.0001, 0.01), 2))
print("capped bar (<0.80):", int(counts[0]), "| last bar (0.99-1.00):", int(counts[-1]), "| all bars:", int(counts.sum()))
print("bars 0.80-0.85:", counts[1:6].tolist(), "| 0.85-0.90:", counts[6:11].tolist())
by = collections.defaultdict(list)
for r, s in chunks: by[r].append(s)
best = {r: max(v) for r, v in by.items()}
for t in (0.75, 0.80, 0.85, 0.90, 0.95):
    print(f"tau {t:.2f}: reviews with no chunk above tau = {sum(v <= t for v in best.values())} | chunks at or below tau = {int((x <= t).sum())}")

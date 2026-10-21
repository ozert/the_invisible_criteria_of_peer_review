"""Review-level permutation test of the association between rating category and topic.

Run from the repository root. Reads the released main-corpus files, links each classified
question to its review and rating, and compares the observed chi-square statistic with a
null distribution obtained by shuffling rating labels across reviews (all units of a review
stay together). Reported in Section 5.3 and Table 7 of the revised manuscript.
"""
import json
import numpy as np
from scipy.stats import chi2_contingency

TOPICS = "data/Main Corpus/3 - Topic Assignment/topic_assignment_output_760_samples.json"
UNITS = ("data/Main Corpus/2 - LLM as a Judge - Question Separation/"
         "question_separated_majority_vote_passed_question_list_all_samples.jsonl")
N_PERM, SEED, K = 10_000, 2026, 13


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def chi_square(table):
    table = table[:, table.sum(0) > 0]
    expected = np.outer(table.sum(1), table.sum(0)) / table.sum()
    return ((table - expected) ** 2 / expected).sum()


def cramers_v(x2, table):
    r, c = table.shape
    return np.sqrt(x2 / (table.sum() * (min(r, c) - 1)))


def contingency(counts, groups, n_groups):
    return np.stack([counts[groups == g].sum(0) for g in range(n_groups)]).astype(float)


topics = read_jsonl(TOPICS)
link = {u["question"]: (u["review_id"], u["rating"]) for u in read_jsonl(UNITS)}
reviews = sorted({link[t["question"]][0] for t in topics})
index = {r: i for i, r in enumerate(reviews)}
counts = np.zeros((len(reviews), K), dtype=int)
rating = np.zeros(len(reviews), dtype=int)
for t in topics:
    rid, rat = link[t["question"]]
    counts[index[rid], int(t["assigned_topic"])] += 1
    rating[index[rid]] = rat

comparisons = {
    "Rating 1 vs. other ratings": np.where(rating == 1, 0, 1),
    "Borderline (5 & 6) vs. other ratings": np.where(np.isin(rating, [5, 6]), 0, 1),
    "All six rating categories": np.searchsorted([1, 3, 5, 6, 8, 10], rating),
}

rng = np.random.default_rng(SEED)
print(f"{len(topics)} units in {len(reviews)} reviews; {N_PERM} permutations, seed {SEED}")
for name, groups in comparisons.items():
    n_groups = groups.max() + 1
    table = contingency(counts, groups, n_groups)
    x2 = chi_square(table)
    _, p_asym, df, expected = chi2_contingency(table)
    v = cramers_v(x2, table)
    null_x2, null_v = np.empty(N_PERM), np.empty(N_PERM)
    for b in range(N_PERM):
        t_perm = contingency(counts, rng.permutation(groups), n_groups)
        null_x2[b] = chi_square(t_perm)
        null_v[b] = cramers_v(null_x2[b], t_perm)
    p_perm = (1 + (null_x2 >= x2).sum()) / (N_PERM + 1)
    print(f"{name}: chi2({df}) = {x2:.2f}, p_asym = {p_asym:.3f}, p_perm = {p_perm:.3f}, "
          f"V = {v:.3f}, null V median = {np.median(null_v):.3f}, "
          f"null V 95th pct = {np.percentile(null_v, 95):.3f}, "
          f"cells with expected < 5: {(expected < 5).sum()} of {expected.size}")

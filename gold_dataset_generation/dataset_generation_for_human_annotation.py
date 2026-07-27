import json
import pickle
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
TARGET_N = 50

# ---> THIS MUST POINT TO YOUR MONGODB PICKLE FILE <---
# Change this path if your matched_reviews.pkl is located somewhere else!
REVIEWS_PKL = "/Users/ozer/Documents/Workspace/thesis_work/data/artifacts/matched_reviews.pkl" 
OUT_TASK = "data/artifacts/study_a_task.json"

random.seed(SEED)

# 1. Load raw reviews from the pickle file
print(f"Loading raw reviews from {REVIEWS_PKL}...")
with open(REVIEWS_PKL, "rb") as f:
    reviews = pickle.load(f)

def get_field(doc, key):
    content = doc.get("content", {})
    val = doc.get(key, content.get(key))
    if isinstance(val, dict) and "value" in val:
        return val["value"]
    return val

# 2. Extract raw questions and ratings
valid_reviews = []
for d in reviews:
    rid = d.get("id", d.get("review_id"))
    rating = get_field(d, "rating")
    raw_q = get_field(d, "questions")
    
    # We only want reviews that actually have a questions field
    if rid and rating and raw_q:
        valid_reviews.append({
            "review_id": rid,
            "rating": rating,
            "raw_questions": raw_q,
            "human_chunks": [] # We will fill this in the UI
        })

# 3. Stratify by rating
by_rating = defaultdict(list)
for r in valid_reviews:
    by_rating[r["rating"]].append(r)

total = len(valid_reviews)
raw_alloc = {r: TARGET_N * len(by_rating[r]) / total for r in by_rating}
alloc = {r: int(raw_alloc[r]) for r in raw_alloc}

# Largest remainder method to hit exactly 50
remainder = TARGET_N - sum(alloc.values())
for r in sorted(raw_alloc, key=lambda x: raw_alloc[x] - alloc[x], reverse=True)[:remainder]:
    alloc[r] += 1

# 4. Sample
sample = []
for r, k in alloc.items():
    random.shuffle(by_rating[r])
    sample.extend(by_rating[r][:k])

random.shuffle(sample)

# 5. Save
Path(OUT_TASK).parent.mkdir(parents=True, exist_ok=True)
json.dump({"seed": SEED, "task": sample}, open(OUT_TASK, "w", encoding="utf-8"), indent=2)

print(f"\nSampled {len(sample)} reviews for Study A.")
print(f"Allocation per rating: {dict(sorted(alloc.items()))}")
print(f"Task saved to: {OUT_TASK}")
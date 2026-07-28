# Data Directory

This directory contains the processed data artifacts for the peer review analysis of the **ICLR 2024** corpus. The data is organized into three corpora, each produced by the same multi-stage LLM pipeline described in the manuscript.

- **Main Corpus** — Core development corpus. A single review per submission, stratified by rating (N=427 reviews → 760 validated question chunks).
- **Main Corpus - Extended** — Variant that includes the remaining reviews (not restricted to one per submission) for robustness checks (2,353 chunks).
- **Validation Corpus** — Held-out corpus built with identical stratification logic, used to audit generalizability (N=431 reviews → 810 chunks).

Each corpus follows the same three-stage layout.

---

## 1 - Question Separation

Output of the **Source-Anchored Information Extraction** stage. This stage applies two levels of filtering to the raw `Questions` field of the reviews.

**Level 1 — Non-Informative Filtering** (`Gemini 2.5 Flash`): separates reviews that contain actionable questions from empty/referential ones (e.g., _"See weaknesses"_, _"None"_).

- `llm_found_informative_reviews.json` — Reviews classified as **informative** (contain actionable content).
- `llm_found_noninformative_reviews.json` — Reviews classified as **non-informative** (excluded from further processing).

**Level 2 — Context-Aware Extraction** (`Gemini 2.5 Pro`): segments the informative reviews into semantically coherent question chunks and performs a second, deeper informativeness check.

- `llm_found_informative_question_separation_found_informative_reviews.json` — Extracted question chunks from reviews confirmed as informative.
- `llm_found_informative_question_separation_found_noninformative_reviews.json` — Reviews that passed Level 1 but were found non-informative during the deeper Level 2 extraction.

> In the _Extended_ corpus, these files are generated from the same submissions as Main corpus, but share no common review, indicating the remaining reviews (beyond one-per-submission) were included.

---

## 2 - LLM as a Judge - Question Separation

Output of the **Multi-Stage Data Validation** stage, where a panel of three models (`GPT-4o`, `Claude 3.7 Sonnet`, `Gemini 2.5 Flash`) validates the semantic coherence of each chunk via majority vote.

- `question_separated_majority_vote_passed_question_list_all_samples.jsonl` — Final validated question chunks that passed the majority-vote consensus. This is the input for topic assignment.
- `judge_question_separation_no_mutual_aggreement_samples.json` — Chunks discarded due to lack of majority consensus among the judges.

---

## 3 - Topic Assignment

Output of the **Logit-Based Soft Classification** stage (`GPT-4o`), assigning each chunk a probability distribution over the 13-topic schema.

- `topic_assignment_output_760_samples.json` — Soft-classification results for the Main Corpus.
- `topic_assignment_output_2353_samples.json` — Results for the Extended corpus.
- `topic_assignment_output_validation_810_samples.json` — Results for the Validation corpus.

Each entry includes the top topic, the full probability vector, and the derived uncertainty metrics (Probability Margin, Normalized Entropy, Total Valid Mass).

---

## TopicGPT Artifacts

Outputs of the **Generative Topic Modeling** stage.

**Intermediate Topics** — Raw candidate topics from three independent TopicGPT runs:

- `gemini_2_5_flash_first_half_topics.md` — Run 1 (Gemini 2.5 Flash, first data subset).
- `gpt_4o_second_half_topics.md` — Run 2 (GPT-4o, second data subset).
- `gpt_4o_all_samples_topics.md` — Run 3 (GPT-4o, full corpus).

**Final Topics**

- `consolidated_topics.md` — The final, consolidated **13-topic schema** used for all subsequent classification and alignment analyses.

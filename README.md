# Replication Package

This repository contains the complete replication package for our study on review informativeness, question separation, topic modeling, and LLM-based analysis. It includes the data acquisition pipeline, LLM processing chains, prompts, datasets across multiple processing stages, gold-standard human annotations, and topic modeling artifacts.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Detailed Description](#detailed-description)
  - [Root-Level Files](#root-level-files)
  - [Configuration (`conf/`)](#configuration-conf)
  - [Data Acquisition](#data-acquisition)
  - [MongoDB Access (`mongodb/`)](#mongodb-access-mongodb)
  - [LLM Pipeline (`llm_pipeline/`)](#llm-pipeline-llm_pipeline)
  - [Gold Dataset Generation (`gold_dataset_generation/`)](#gold-dataset-generation-gold_dataset_generation)
  - [Data (`data/`)](#data-data)
  - [Topic Samples (`Topic Samples/`)](#topic-samples-topic-samples)
- [Data Processing Pipeline](#data-processing-pipeline)
- [Licenses](#licenses)

---

## Overview

The pipeline processes user reviews through a series of stages:

1. **Data Acquisition** — Collect raw reviews and store them in MongoDB.
2. **Informativeness Filtering** — Use an LLM to separate informative from non-informative reviews.
3. **Question Separation** — Split reviews into discrete question/statement units.
4. **LLM-as-a-Judge Validation** — Validate the question separation via majority-vote agreement.
5. **Topic Assignment** — Assign reviews/questions to topics generated using TopicGPT.
6. **Evaluation** — Compare LLM outputs against a human-annotated gold dataset.

The package provides three corpora: the **Main Corpus**, an **Extended Main Corpus**, and a **Validation Corpus**.

---

## Repository Structure

```
.
├── README.md                      # This file
├── LICENSE                        # Primary code license
├── DATA_LICENSES.md               # Licensing details for the datasets
├── LICENSE_CC0_1.0.txt            # CC0 1.0 license text
├── LICENSE_CC_4.0.txt             # CC BY 4.0 license text
├── pyproject.toml                 # Project dependencies & build configuration
│
├── conf/                          # Configuration files
├── data_acquisition.py            # Entry point for collecting raw review data
├── mongodb/                       # MongoDB data-access utilities
├── llm_pipeline/                  # LLM chains, prompts, and utilities
├── gold_dataset_generation/       # Human-annotation & LLM-evaluation code
├── data/                          # All datasets across processing stages
├── Topic Samples/                 # Example topic visualizations (PNG)
│
├── human_annotated_informativeness_corpus_427_samples.json
└── topicgpt_topic_generation_prompt_template_generation_1.txt
```

---

## Detailed Description

### Root-Level Files

| File                                                         | Description                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------ |
| `README.md`                                                  | This documentation file.                                                 |
| `Setup.md`                                                   | Environment setup guide.                                                 |
| `LICENSE`                                                    | Main license governing the code in this repository.                      |
| `DATA_LICENSES.md`                                           | Explains the licenses that apply to the datasets.                        |
| `LICENSE_CC0_1.0.txt`                                        | Full text of the Creative Commons CC0 1.0 license.                       |
| `LICENSE_CC_4.0.txt`                                         | Full text of the Creative Commons Attribution 4.0 license.               |
| `pyproject.toml`                                             | Python project metadata, dependencies, and build configuration.          |
| `data_acquisition.py`                                        | Script to acquire/collect raw review data.                               |
| `human_annotated_informativeness_corpus_427_samples.json`    | Gold-standard corpus of 427 human-annotated samples for informativeness. |
| `topicgpt_topic_generation_prompt_template_generation_1.txt` | Prompt template used to generate topics with TopicGPT.                   |

### Configuration (`conf/`)

| File          | Description                                                   |
| ------------- | ------------------------------------------------------------- |
| `config.yaml` | Central configuration (paths, model names, parameters, etc.). |
| `config.py`   | Loads and exposes the YAML configuration to the Python code.  |

### Data Acquisition

- **`data_acquisition.py`** — Collects raw reviews from the source and persists them (via the MongoDB layer) for downstream processing.

### MongoDB Access (`mongodb/`)

| File                   | Description                                                           |
| ---------------------- | --------------------------------------------------------------------- |
| `mongo_data_access.py` | Data-access layer providing read/write helpers for the MongoDB store. |

### LLM Pipeline (`llm_pipeline/`)

The core of the LLM-based processing.

```
llm_pipeline/
├── ai/
│   └── chat.py                    # LLM client / chat interface wrapper
├── chains/
│   └── chains.py                  # Orchestrates multi-step LLM chains
├── prompts/                       # Prompt definitions for each task
│   ├── correspondance_assignment.py
│   ├── judge_question_separation.py
│   ├── judge_topic_assignment.py
│   ├── non_informant_review_filtering.py
│   ├── question_separation.py
│   ├── summarization.py
│   └── topic_assignment.py
└── utils/
    └── embedding_generation.py    # Generates embeddings (e.g., for similarity)
```

| Prompt File                         | Purpose                                           |
| ----------------------------------- | ------------------------------------------------- |
| `non_informant_review_filtering.py` | Detect and filter non-informative reviews.        |
| `question_separation.py`            | Split reviews into individual questions/units.    |
| `judge_question_separation.py`      | LLM-as-a-judge validation of question separation. |
| `topic_assignment.py`               | Assign topics to reviews/questions.               |
| `judge_topic_assignment.py`         | LLM-as-a-judge validation of topic assignment.    |
| `correspondance_assignment.py`      | Establish correspondence/mapping between items.   |
| `summarization.py`                  | Summarize content.                                |

### Gold Dataset Generation (`gold_dataset_generation/`)

Code and artifacts to build the human-annotated gold set and evaluate LLM performance against it.

| File                                                           | Description                                                      |
| -------------------------------------------------------------- | ---------------------------------------------------------------- |
| `dataset_generation_for_human_annotation.py`                   | Prepares data samples for human annotation.                      |
| `human_annotation_question_separation_and_topic_assignment.py` | Tooling for annotating question separation and topic assignment. |
| `llm_performance_analysis.ipynb`                               | Notebook analyzing LLM performance vs. human annotations.        |
| `data/artifacts/study_a_task.json`                             | Task definition/data for annotation study A.                     |
| `data/artifacts/study_a_manual_matches.json`                   | Manually verified matches from study A.                          |

### Data (`data/`)

Contains all corpora, organized by processing stage. Each corpus follows the same three-stage folder layout.

```
data/
├── Readme.md                                # Data-specific documentation
├── Topic Modeling Consolidation.xlsx        # Spreadsheet consolidating topic modeling results
├── cosine_similarity_eliminated_samples.json# Samples removed via cosine-similarity dedup
├── question_weakness_strength_relation.json # Relations between question strengths/weaknesses
│
├── Main Corpus/
├── Main Corpus - Extended/
├── Validation Corpus/
└── TopicGPT Artifacts/
```

**Per-corpus stage layout** (`Main Corpus`, `Main Corpus - Extended`, `Validation Corpus`):

| Subfolder                                  | Contents                                                                                                    |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `1 - Question Separation`                  | Reviews split into informative/non-informative sets and separated into informant / non-informant questions. |
| `2 - LLM as a Judge - Question Separation` | Majority-vote validated question lists and samples lacking mutual agreement.                                |
| `3 - Topic Assignment`                     | Topic-assigned outputs, extended with rating and review ID.                                                 |

Representative files:

| File                                                                        | Description                                              |
| --------------------------------------------------------------------------- | -------------------------------------------------------- |
| `llm_found_informative_reviews.json`                                        | Reviews classified as informative.                       |
| `llm_found_noninformative_reviews.json`                                     | Reviews classified as non-informative.                   |
| `llm_found_informative_question_separation_found_informant_reviews.json`    | Informant-question units from informative reviews.       |
| `llm_found_informative_question_separation_found_noninformant_reviews.json` | Non-informant-question units from informative reviews.   |
| `question_separated_majority_vote_passed_question_list_all_samples.jsonl`   | Question lists that passed majority-vote judging.        |
| `judge_question_separation_no_mutual_aggreement_samples.json`               | Samples where judges did not reach agreement.            |
| `topic_assignment_output_*_samples.json`                                    | Raw topic-assignment outputs (sample count in filename). |
| `topic_assignment_*_extended_with_rating_and_review_id.jsonl`               | Topic assignments enriched with rating and review ID.    |

> The **Extended** corpus files mirror the Main Corpus but include remaining/additional samples (suffixed `_remaining_included` / `_extended`).

**TopicGPT Artifacts:**

| Path                                                        | Description                                    |
| ----------------------------------------------------------- | ---------------------------------------------- |
| `Intermediate Topics/gpt_4o_all_samples_topics.md`          | Topics generated by GPT-4o over all samples.   |
| `Intermediate Topics/gpt_4o_second_half_topics.md`          | GPT-4o topics for the second half of the data. |
| `Intermediate Topics/gemini_2_5_flash_first_half_topics.md` | Gemini 2.5 Flash topics for the first half.    |
| `Final Topics/consolidated_topics.md`                       | Final consolidated topic list.                 |

### Topic Samples (`Topic Samples/`)

Contains `Topic-1.png` through `Topic-13.png` — example visualizations for each of the 13 identified topics.

---

## Data Processing Pipeline

```
data_acquisition.py
        │
        ▼
   MongoDB store  ──►  llm_pipeline (chains + prompts)
        │
        ├─ 1. Informativeness Filtering
        ├─ 2. Question Separation
        ├─ 3. LLM-as-a-Judge Validation
        └─ 4. Topic Assignment  ◄── TopicGPT topics
                    │
                    ▼
        Evaluation vs. Gold Dataset
        (gold_dataset_generation/)
```

Outputs of each stage are stored under `data/<Corpus>/<Stage>/`.

---

## Licenses

- **Code** is released under the terms in [`LICENSE`](LICENSE).
- **Data** licensing is described in [`DATA_LICENSES.md`](DATA_LICENSES.md), and may be governed by:
  - [CC0 1.0](LICENSE_CC0_1.0.txt) (public domain dedication), and/or
  - [CC BY 4.0](LICENSE_CC_4.0.txt) (attribution).

Please review the applicable license before reusing any component of this package.

---

_For questions about data-specific details, see [`data/Readme.md`](data/Readme.md)._

from dataclasses import dataclass
from typing import List

@dataclass
class OpenReview:
    """OpenReview API configuration."""
    api_version: str
    root_conference_names: List[str]

@dataclass
class GPTReasoningModels:
    """OpenReview API configuration."""
    google: str
    openai: str
    anthropic: str
    google_topic_assignment_judge: str
    anthropic_topic_assignment_judge: str

@dataclass
class LLMModels:
    """OpenReview API configuration."""
    question_separation: str
    question_filtering: str
    
@dataclass
class MongoDB:
    """MongoDB connection configuration."""
    host: str
    port: int
    db_name: str
    username: str
    password: str

@dataclass
class DataAcquisitionConfig:
    """Data acquisition configuration."""
    open_review_conf: OpenReview
    mongodb: MongoDB
    gpt_reasoning_models: GPTReasoningModels
    embedding_model:str
    topic_assignment_model:str
    llm_models: LLMModels
    iclr_2024_venue: str
    iclr_2025_venue: str
    pdf_directory: str
    
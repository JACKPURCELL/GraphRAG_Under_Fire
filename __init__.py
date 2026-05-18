"""
GRAGPOISON: GraphRAG Adversarial Attack Implementation

Implementation of the GRAGPOISON algorithm for adversarial attacks on GraphRAG systems.
"""

from .data_loader import load_question_sets, get_question_sets
from .config import GRAGPOISONConfig, DEFAULT_CONFIG, RECOMMENDED_DATASET_PATH
from .pipeline import run_gragpoison_pipeline, run_graphrag_indexing, process_questions_v2

__version__ = "1.0.0"

__all__ = [
    "load_question_sets",
    "get_question_sets",
    "GRAGPOISONConfig",
    "DEFAULT_CONFIG",
    "RECOMMENDED_DATASET_PATH",
    "run_gragpoison_pipeline",
    "run_graphrag_indexing",
    "process_questions_v2",
]

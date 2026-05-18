"""Attack module initialization"""

from .prompts import (
    BLACKBOX_PROMPT,
    SEARCH_NEW_MIDDLE_PROMPT,
    SEARCH_NEW_MIDDLE_PROMPT_NOSIMILAR,
    SEARCH_NEW_MIDDLE_PROMPT_MIDDLELEAF,
    GEN_CORPUS_PROMPT,
    GEN_CORPUS_PROMPT_RM2,
    GEN_CORPUS_PROMPT_MIDDLELEAF,
)
from .middle_node_finder import find_modified_middle_node
from .injector import process_response, check_json_keys
from .enhancer import process_response_attack_middlewithleaf, process_question_set_blackbox

__all__ = [
    "BLACKBOX_PROMPT",
    "SEARCH_NEW_MIDDLE_PROMPT",
    "SEARCH_NEW_MIDDLE_PROMPT_NOSIMILAR",
    "SEARCH_NEW_MIDDLE_PROMPT_MIDDLELEAF",
    "GEN_CORPUS_PROMPT",
    "GEN_CORPUS_PROMPT_RM2",
    "GEN_CORPUS_PROMPT_MIDDLELEAF",
    "find_modified_middle_node",
    "process_response",
    "check_json_keys",
    "process_response_attack_middlewithleaf",
    "process_question_set_blackbox",
]

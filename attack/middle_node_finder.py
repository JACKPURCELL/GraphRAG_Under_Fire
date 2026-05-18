"""
Middle Node Finder Module

查找Modified Middle Node (vr*)
从build_corpus_1207.py lines 984-990提取
"""

from typing import Dict, Union, List, Any
from ..utils.llm_interface import ask_llm
from .prompts import SEARCH_NEW_MIDDLE_PROMPT, SEARCH_NEW_MIDDLE_PROMPT_NOSIMILAR


def find_modified_middle_node(
    root_node: Union[str, List[str]],
    original_middle_node: str,
    chain_of_thoughts: str,
    similar: bool = True,
    pipe: Any = None
) -> Dict:
    """
    查找Modified Middle Node (vr*)

    Args:
        root_node: Root node(s)
        original_middle_node: Original middle node
        chain_of_thoughts: Chain of thoughts describing the relationship
        similar: If True, find similar node; if False, find same-type but dissimilar node
        pipe: Pipeline object for VLLM (None for GPT)

    Returns:
        Dict with keys: "Root Node", "Original Middle Node", "Modified Middle Node"

    Example:
        >>> result = find_modified_middle_node(
        ...     root_node=["China"],
        ...     original_middle_node="Beijing",
        ...     chain_of_thoughts="The capital of China is Beijing.",
        ...     similar=True
        ... )
        >>> print(result["Modified Middle Node"])
        'Shanghai'
    """
    # 构建prompt
    target_relationship = [[root_node, original_middle_node]] if isinstance(root_node, str) else \
                         [[rn, original_middle_node] for rn in root_node]

    prompt_middle_node = f"\n Given [Root Node, Original Middle Node] is {str(target_relationship)} " \
                        f"The chain of thoughts of their relationships is {chain_of_thoughts}"

    # 选择prompt
    if similar:
        new_middle_node_json = ask_llm(SEARCH_NEW_MIDDLE_PROMPT, prompt_middle_node, pipe)
    else:
        new_middle_node_json = ask_llm(SEARCH_NEW_MIDDLE_PROMPT_NOSIMILAR, prompt_middle_node, pipe)

    return new_middle_node_json

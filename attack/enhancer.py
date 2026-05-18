"""
Attack Enhancer Module - Stage 3: Relation Enhancement

生成Indirect & Enhanced Attack Texts (Vr+)
从build_corpus_1207.py提取
"""

import json
from typing import Dict, Any
from ..utils.llm_interface import ask_llm
from .prompts import GEN_CORPUS_PROMPT_MIDDLELEAF
from .injector import check_json_keys


def process_response_attack_middlewithleaf(
    new_leaf_node_json: Dict,
    middle_node: str,
    original_leaf_node: str,
    modified_leaf_node: str,
    response_cot_json: Dict,
    pipe: Any = None
) -> Dict:
    """
    生成Middle-Leaf攻击文本

    Args:
        new_leaf_node_json: Modified leaf node信息
        middle_node: Middle node
        original_leaf_node: Original leaf node
        modified_leaf_node: Modified leaf node
        response_cot_json: Chain of thoughts JSON
        pipe: Pipeline for VLLM

    Returns:
        Dict: 包含攻击文本的JSON

    Note: From build_corpus_1207.py lines 853-874
    """
    new_leaf_node_json["Original Relationship"] = response_cot_json["Template Relationship between middle and leaf node"][0].format(
        middle_node=middle_node, leaf_node=original_leaf_node
    )
    new_leaf_node_json["Modified Relationship"] = response_cot_json["Template Relationship between middle and leaf node"][0].format(
        middle_node=middle_node, leaf_node=modified_leaf_node
    )

    new_leaf_node_json["Template Relationship between root and middle node"] = \
        response_cot_json["Template Relationship between root and middle node"][0]
    new_leaf_node_json["Template Relationship between middle and leaf node"] = \
        response_cot_json["Template Relationship between middle and leaf node"][0]
    new_leaf_node_json["Template Relationship between root and leaf node"] = \
        response_cot_json["Template Relationship between root and leaf node"][0]

    attack_nodes_str = "The JSON is as follows: \n"
    attack_nodes_str += json.dumps(new_leaf_node_json, ensure_ascii=False, indent=4)
    attack_nodes_str += f"\n The question is {response_cot_json['question']}"

    while True:
        attack_json = ask_llm(GEN_CORPUS_PROMPT_MIDDLELEAF, attack_nodes_str, pipe)
        if check_json_keys(attack_json):
            break

    attack_json = {**attack_json, **response_cot_json, **new_leaf_node_json}
    attack_json["type"] = "middlewithleaf"
    return attack_json


def process_question_set_blackbox(question: Dict, pipe: Any = None) -> Dict:
    """
    处理单个问题集 (Black-box模式)

    Args:
        question: 问题字典
        pipe: Pipeline for VLLM

    Returns:
        Dict: Chain of thoughts JSON

    Note: From build_corpus_1207.py lines 877-884
    """
    from .prompts import BLACKBOX_PROMPT

    response_cot_json = ask_llm(BLACKBOX_PROMPT, "The given question is " + question["question"], pipe)

    if isinstance(response_cot_json, list):
        response_cot_json = response_cot_json[0]

    response_cot_json["BLACK_BOX"] = True

    return response_cot_json

"""
Attack Injector Module - Stage 2: Relation Injection

生成Direct Attack Texts (dr*)
从build_corpus_1207.py lines 803-851提取
"""

import json
from typing import Dict, Union, List, Any
from ..utils.llm_interface import ask_llm
from .prompts import GEN_CORPUS_PROMPT, GEN_CORPUS_PROMPT_RM2


def check_json_keys(data: Dict) -> bool:
    """
    检查JSON是否包含所有必需的键

    Args:
        data: JSON数据

    Returns:
        bool: 是否包含所有必需键
    """
    required_keys = [
        "direct_adv_texts",
        "direct_new_relationships",
        "indirect_adv_texts",
        "indirect_new_entities",
        "indirect_new_relationships",
        "enhanced_texts",
        "enhanced_new_relationships"
    ]

    if not isinstance(data, dict):
        print("Not a dict")
        return False

    try:
        for key in required_keys:
            if key not in data:
                print(f'\n Key {key} not found')
                return False
    except:
        print("Key Error")
        return False

    return True


def process_response(
    new_middle_node_json: Dict,
    root_node: Union[str, List[str]],
    original_middle_node: str,
    modified_middle_node: str,
    response_cot_json: Dict,
    pipe: Any = None,
    remove_negation: bool = False
) -> Dict:
    """
    生成攻击文本 (Direct + Indirect + Enhanced)

    Args:
        new_middle_node_json: Modified middle node信息
        root_node: Root node(s)
        original_middle_node: Original middle node
        modified_middle_node: Modified middle node
        response_cot_json: Chain of thoughts JSON
        pipe: Pipeline for VLLM
        remove_negation: 是否移除negation (使用GEN_CORPUS_PROMPT_RM2)

    Returns:
        Dict: 包含所有攻击文本的JSON

    Note: From build_corpus_1207.py lines 803-851
    """
    try:
        if remove_negation:
            print("Remove negation - using GEN_CORPUS_PROMPT_RM2")
            new_middle_node_json["Modified Relationship"] = response_cot_json["Template Relationship between root and middle node"][0].format(
                root_node=root_node, middle_node=modified_middle_node
            )
            new_middle_node_json["Template Relationship between root and middle node"] = \
                response_cot_json["Template Relationship between root and middle node"][0]
            new_middle_node_json["Template Relationship between middle and leaf node"] = \
                response_cot_json["Template Relationship between middle and leaf node"][0]
            new_middle_node_json["Template Relationship between root and leaf node"] = \
                response_cot_json["Template Relationship between root and leaf node"][0]

            attack_nodes_str = "The JSON is as follows: \n"
            attack_nodes_str += json.dumps(new_middle_node_json, ensure_ascii=False, indent=4)
            attack_nodes_str += f"\n The question is {response_cot_json['question']}"

            while True:
                attack_json = ask_llm(GEN_CORPUS_PROMPT_RM2, attack_nodes_str, pipe)
                if check_json_keys(attack_json):
                    break
        else:
            # 处理多个root nodes
            root_nodes = [root_node] if isinstance(root_node, str) else root_node
            new_middle_node_json["Original Relationship"] = []
            new_middle_node_json["Modified Relationship"] = []

            for rn in root_nodes:
                new_middle_node_json["Original Relationship"].append(
                    response_cot_json["Template Relationship between root and middle node"][0].format(
                        root_node=rn, middle_node=original_middle_node
                    )
                )
                new_middle_node_json["Modified Relationship"].append(
                    response_cot_json["Template Relationship between root and middle node"][0].format(
                        root_node=rn, middle_node=modified_middle_node
                    )
                )

            new_middle_node_json["Template Relationship between root and middle node"] = \
                response_cot_json["Template Relationship between root and middle node"][0]
            new_middle_node_json["Template Relationship between middle and leaf node"] = \
                response_cot_json["Template Relationship between middle and leaf node"][0]
            new_middle_node_json["Template Relationship between root and leaf node"] = \
                response_cot_json["Template Relationship between root and leaf node"][0]

            attack_nodes_str = "The JSON is as follows: \n"
            attack_nodes_str += json.dumps(new_middle_node_json, ensure_ascii=False, indent=4)
            attack_nodes_str += f"\n The question is {response_cot_json['question']}"

            while True:
                attack_json = ask_llm(GEN_CORPUS_PROMPT, attack_nodes_str, pipe)
                if check_json_keys(attack_json):
                    break

        # 合并所有信息
        attack_json = {**attack_json, **response_cot_json, **new_middle_node_json}
        attack_json["type"] = "normal"
        return attack_json

    except Exception as e:
        print(f"Error at process_response: {e}")
        print(f"Need to remove question {response_cot_json.get('question', 'N/A')}")
        return None

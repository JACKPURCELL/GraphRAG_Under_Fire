"""
Data Loader Module

加载question_multi_v3.json或question_multi_v3_filtered.json
这是GRAGPOISON算法的第一步（简化版的Relation Selection）
"""

import os
import json
from typing import List, Dict


def load_question_sets(base_path: str, use_filtered: bool = False) -> List[Dict]:
    """
    加载question_multi_v3.json或question_multi_v3_filtered.json

    Args:
        base_path: 数据集路径，例如 /home/stufs1/jiachliang/graphrag/sp/misuque_3_black_shuffle_0601
        use_filtered: 是否使用filtered版本（已过滤的问题集）

    Returns:
        List of question sets, each containing:
        - questions: List of questions with root_nodes, middle_node, leaf_nodes
        - shared_index: (optional) 共享关系的标识

    Note:
    - 实际代码中没有实现论文的greedy set cover算法
    - 关系已经在JSON中预先定义好
    - 关系合并逻辑在text_processor.py的filter_texts_with_relation_merging中实现

    Example:
        >>> question_sets = load_question_sets('/path/to/dataset', use_filtered=True)
        >>> print(f"Loaded {len(question_sets)} question sets")
    """
    filename = 'question_multi_v3_filtered.json' if use_filtered else 'question_multi_v3.json'
    question_path_multi = os.path.join(base_path, filename)

    if not os.path.exists(question_path_multi):
        raise FileNotFoundError(f"Question file not found: {question_path_multi}")

    with open(question_path_multi, 'r', encoding='utf-8') as f:
        multi_candidate_questions_sets = json.load(f)

    print(f"Loaded {len(multi_candidate_questions_sets)} question sets from {question_path_multi}")

    return multi_candidate_questions_sets


def get_question_sets(base_path: str) -> List[Dict]:
    """
    兼容旧代码的接口，默认加载question_multi_v3.json

    Args:
        base_path: 数据集路径

    Returns:
        List of question sets

    Note: 这是从build_corpus_1207.py lines 506-510提取的原始函数
    """
    return load_question_sets(base_path, use_filtered=False)

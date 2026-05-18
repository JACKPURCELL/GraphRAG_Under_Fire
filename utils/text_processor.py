"""
Text Processor Module

文本处理和关系合并逻辑
从build_corpus_1207.py lines 521-675提取
"""

import os
import json
import random
from pathlib import Path
from typing import List, Tuple, Dict


def ensure_minimum_word_count_and_save(
    texts: List[str],
    output_path: str,
    repeat_count: int = 1,
    shuffle: bool = False
):
    """
    保存文本到文件，支持重复和shuffle

    Args:
        texts: 文本列表
        output_path: 输出文件路径
        repeat_count: 每个文本重复次数
        shuffle: 是否shuffle

    Note: From build_corpus_1207.py lines 521-552
    """
    processed_texts = []

    for text in texts:
        # 处理dict类型的text
        if isinstance(text, dict):
            try:
                text = text['text']
            except:
                continue

        # 重复文本
        for i in range(repeat_count):
            processed_texts.append(text)

    # Shuffle if needed
    if shuffle:
        random.shuffle(processed_texts)

    # 合并文本
    combined_text = '\n\n'.join(processed_texts)

    # 写入文件
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving the combined text to {output_path_obj}")
    output_path_obj.write_text(combined_text, encoding='utf-8')


def calculate_need_to_keep(
    num_texts: int,
    num_text_per_root: int,
    num_keep: int
) -> List[int]:
    """
    计算需要保留的文本索引

    Args:
        num_texts: 总文本数
        num_text_per_root: 每个root node的文本数
        num_keep: 需要保留的数量

    Returns:
        List[int]: 需要保留的索引列表

    Note: From build_corpus_1207.py lines 593-597
    """
    need_to_keep = []
    for i in range(0, num_texts, num_text_per_root):
        need_to_keep.extend(range(i, i + num_keep))
    return need_to_keep


def filter_texts_with_relation_merging(
    all_jsons: List[Dict],
    num_keep_direct: int = 10,
    num_keep_indirect: int = 5
) -> Tuple[List[str], List[str], List[str]]:
    """
    过滤文本并实现关系合并逻辑

    关系合并规则（from build_corpus_1207.py lines 645-663）：
    - 如果当前问题的 (root_nodes, middle_node) 与前一个问题相同
    - 则共用direct attack texts，不重复生成
    - 但indirect和enhanced texts仍然为每个问题生成

    这实现了论文中的关系复用，减少poisoning text数量

    Args:
        all_jsons: 所有问题的JSON列表
        num_keep_direct: 保留的direct texts数量 (Nα)
        num_keep_indirect: 保留的indirect texts数量 (Nβ)

    Returns:
        Tuple[List[str], List[str], List[str]]: (direct_adv_texts, indirect_adv_texts, enhanced_adv_texts)

    Note: From build_corpus_1207.py lines 599-675
    """
    indirect_adv_texts = []
    direct_adv_texts = []
    enhanced_adv_texts = []
    recent_root_nodes = ""
    recent_middle_node = ""

    for set_data in all_jsons:
        if set_data is None:
            continue

        if set_data.get("type") == "normal":
            # 计算root node数量
            if isinstance(set_data["root_nodes"], str):
                num_root_node = 1
            else:
                num_root_node = len(set_data["root_nodes"])

            # 处理indirect texts (middle-leaf)
            if set_data.get("indirect_adv_texts") is not None:
                indirect_adv_texts.extend(set_data["indirect_adv_texts"][:num_keep_indirect])

            # 处理enhanced texts
            if set_data.get("enhanced_texts") is not None:
                num_enhanced_texts = len(set_data["enhanced_texts"])
                num_text_per_root = num_enhanced_texts // num_root_node if num_root_node > 0 else 0

                if num_text_per_root != 0:
                    need_to_keep = calculate_need_to_keep(num_enhanced_texts, num_text_per_root, num_keep_indirect)
                    temp_enhanced_adv_texts = [set_data["enhanced_texts"][i] for i in need_to_keep if i < len(set_data["enhanced_texts"])]
                    enhanced_adv_texts.extend(temp_enhanced_adv_texts)
                else:
                    print(set_data.get("question", "N/A"), "num_enhanced_texts is None")

            # 关系合并逻辑：只有当(root_nodes, middle_node)不同时才添加direct texts
            if recent_root_nodes != set_data["root_nodes"] or recent_middle_node != set_data.get("middle_node"):
                if set_data.get("direct_adv_texts") is not None:
                    num_direct_texts = len(set_data["direct_adv_texts"])
                    num_text_per_root = num_direct_texts // num_root_node if num_root_node > 0 else 0

                    if num_text_per_root != 0:
                        need_to_keep = calculate_need_to_keep(num_direct_texts, num_text_per_root, num_keep_direct)
                        temp_direct_adv_texts = [set_data["direct_adv_texts"][i] for i in need_to_keep if i < len(set_data["direct_adv_texts"])]
                        direct_adv_texts.extend(temp_direct_adv_texts)
                    else:
                        print(set_data.get("question", "N/A"), "direct_adv_texts is None")

                # 更新recent状态
                recent_root_nodes = set_data["root_nodes"]
                recent_middle_node = set_data.get("middle_node")

    return direct_adv_texts, indirect_adv_texts, enhanced_adv_texts


def rewrite_txt_v2_only_writeone(
    new_base_path: str,
    repeat_count: int = 1,
    num_keep_direct: int = 10,
    num_keep_indirect: int = 5,
    shuffle: bool = False
):
    """
    重写文本文件，实现关系合并和文本过滤

    Args:
        new_base_path: 基础路径
        repeat_count: 重复次数
        num_keep_direct: 保留的direct texts数量 (Nα)
        num_keep_indirect: 保留的indirect texts数量 (Nβ)
        shuffle: 是否shuffle

    Note: From build_corpus_1207.py lines 599-675
    """
    adv_prompt_path = Path(os.path.join(new_base_path, 'test0_corpus.json'))

    with open(adv_prompt_path, 'r', encoding='utf-8') as f:
        all_jsons = json.load(f)

    print(f"Questions loaded successfully from {adv_prompt_path}")

    # 使用关系合并逻辑过滤文本
    direct_adv_texts, indirect_adv_texts, enhanced_adv_texts = filter_texts_with_relation_merging(
        all_jsons, num_keep_direct, num_keep_indirect
    )

    # 保存文本
    ensure_minimum_word_count_and_save(
        direct_adv_texts,
        os.path.join(new_base_path, 'input/adv_texts_direct_test0.txt'),
        repeat_count=repeat_count,
        shuffle=shuffle
    )
    ensure_minimum_word_count_and_save(
        indirect_adv_texts,
        os.path.join(new_base_path, 'input/adv_texts_indirect_test0.txt'),
        repeat_count=repeat_count,
        shuffle=shuffle
    )
    ensure_minimum_word_count_and_save(
        enhanced_adv_texts,
        os.path.join(new_base_path, 'input/adv_texts_enhanced_test0.txt'),
        repeat_count=repeat_count,
        shuffle=shuffle
    )

    print(f"Adversarial texts generated successfully and saved")

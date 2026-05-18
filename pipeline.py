"""
Main Pipeline Module

GRAGPOISON完整攻击流程
从pipeline_1207.py和build_corpus_1207.py的process_questions_v2提取
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
import concurrent.futures

from .data_loader import load_question_sets
from .config import GRAGPOISONConfig
from .attack.middle_node_finder import find_modified_middle_node
from .attack.injector import process_response
from .attack.enhancer import process_response_attack_middlewithleaf, process_question_set_blackbox
from .attack.prompts import SEARCH_NEW_MIDDLE_PROMPT_MIDDLELEAF
from .utils.llm_interface import ask_llm
from .utils.text_processor import rewrite_txt_v2_only_writeone


def run_graphrag_indexing(new_path: str, graphrag_target_dir: str = '/home/ljc/data/graphrag/'):
    """
    运行GraphRAG索引

    Args:
        new_path: 数据路径
        graphrag_target_dir: GraphRAG目标目录

    Note: From pipeline_1207.py lines 11-42
    """
    original_dir = new_path

    try:
        os.chdir(graphrag_target_dir)

        command = [
            'python', '-m', 'graphrag.index', '--root', original_dir
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        print('Standard Output:', result.stdout)
        print('Standard Error:', result.stderr)

        if result.returncode == 0:
            print('命令执行成功')
        else:
            print('命令执行失败')

    finally:
        os.chdir(original_dir)


def process_questions_v2(
    clean_path: str,
    new_base_path: str,
    config: GRAGPOISONConfig
):
    """
    处理问题集并生成攻击文本

    Args:
        clean_path: 原始数据路径
        new_base_path: 输出路径
        config: GRAGPOISON配置

    Note: From build_corpus_1207.py lines 886-1013
    """
    # 设置pipe
    pipe = "llama" if config.use_llama else None

    # 复制数据
    try:
        shutil.copytree(clean_path, new_base_path)
        print(f"Copy clean output to {new_base_path}")
        shutil.rmtree(os.path.join(new_base_path, 'output'), ignore_errors=True)
        shutil.rmtree(os.path.join(new_base_path, 'cache'), ignore_errors=True)
        print(f"Remove output and cache folders in {new_base_path}")
    except FileExistsError:
        print(f"Path {new_base_path} already exists, skipping copy")
    except Exception as e:
        print(f"Error during copy: {e}")

    # 加载问题集
    multi_candidate_questions_sets = load_question_sets(new_base_path, use_filtered=config.use_filtered_questions)

    attack_jsons = []

    for question_set in tqdm(multi_candidate_questions_sets, desc="Processing question sets"):
        response_cot_jsons = []

        # 处理pre_node_pending_questions
        if "pre_node_pending_questions" in question_set:
            pre_node_pending_questions = question_set["pre_node_pending_questions"]
        else:
            pre_node_pending_questions = []
        pre_node_tossave_list = []

        # Black-box或White-box模式
        if config.black_box:
            print("\nUsing black box")
            questions = question_set["questions"]
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futures = [executor.submit(process_question_set_blackbox, q, pipe) for q in questions]
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                                 desc="Processing questions to generate cot", leave=False):
                    response_cot_jsons.append(future.result())
        else:
            print("\nUsing white box")
            response_cot_jsons = question_set["questions"]

        # Attack middle-leaf或root-middle-leaf
        if config.attack_middlewithleaf:
            # Middle-Leaf攻击
            target_relationship = question_set["as_source"][0]
            target_chain_of_thoughts = response_cot_jsons[0]["chain_of_thoughts"][1]
            prompt_leaf_node = f"\n Given [Middle Node, Original Leaf Node] is {str(target_relationship)} " \
                              f"The chain of thoughts of their relationships is {target_chain_of_thoughts}. " \
                              f"The question is {response_cot_jsons[0]['question']}. " \
                              f"The correct answer is {response_cot_jsons[0].get('answer', 'N/A')}"

            new_leaf_node_json = ask_llm(SEARCH_NEW_MIDDLE_PROMPT_MIDDLELEAF, prompt_leaf_node, pipe)
            middle_node = new_leaf_node_json["Middle Node"]
            original_leaf_node = new_leaf_node_json["Original Leaf Node"]
            modified_leaf_node = new_leaf_node_json["Modified Leaf Node"]

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                futures = [
                    executor.submit(process_response_attack_middlewithleaf, new_leaf_node_json,
                                  middle_node, original_leaf_node, modified_leaf_node, response_cot_json, pipe)
                    for response_cot_json in response_cot_jsons
                ]
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                                 desc="Processing responses", leave=False):
                    if future.result() is not None:
                        attack_jsons.append(future.result())

            attack_jsons.extend(pre_node_tossave_list)

        else:
            # Root-Middle-Leaf攻击
            try:
                if len(response_cot_jsons) == 0:
                    continue

                # 提取target relationship
                if isinstance(response_cot_jsons[0]["root_nodes"], str):
                    target_relationship = [[response_cot_jsons[0]["root_nodes"], response_cot_jsons[0]["middle_node"]]]
                else:
                    target_relationship = [[each_rootnode, response_cot_jsons[0]["middle_node"]]
                                         for each_rootnode in response_cot_jsons[0]["root_nodes"]]

                target_chain_of_thoughts = response_cot_jsons[0]["chain_of_thoughts"][0]

                # 查找Modified Middle Node
                new_middle_node_json = find_modified_middle_node(
                    root_node=response_cot_jsons[0]["root_nodes"],
                    original_middle_node=response_cot_jsons[0]["middle_node"],
                    chain_of_thoughts=target_chain_of_thoughts,
                    similar=not config.remove_negation,  # remove_1对应similar参数
                    pipe=pipe
                )

                root_node = new_middle_node_json["Root Node"]
                original_middle_node = new_middle_node_json["Original Middle Node"]
                modified_middle_node = new_middle_node_json["Modified Middle Node"]

                # 处理pre_node_pending_questions
                for pre_node_pending_question_set in pre_node_pending_questions:
                    for pre_node_pending_question in pre_node_pending_question_set["questions"]:
                        pre_node_tossave = pre_node_pending_question
                        pre_node_tossave["indirect_new_entities"] = [modified_middle_node]
                        pre_node_tossave["Modified Middle Node"] = None
                        pre_node_tossave["type"] = "pre_node"
                        pre_node_tossave_list.append(pre_node_tossave)

                # 生成攻击文本
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    futures = [
                        executor.submit(process_response, new_middle_node_json, root_node,
                                      original_middle_node, modified_middle_node, response_cot_json,
                                      pipe, config.remove_negation)
                        for response_cot_json in response_cot_jsons
                    ]
                    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures),
                                     desc="Processing responses", leave=False):
                        result = future.result()
                        if result is not None:
                            attack_jsons.append(result)

                attack_jsons.extend(pre_node_tossave_list)

            except Exception as e:
                print(f"Error at process_questions_v2: {e}")
                continue

    # 保存结果
    adv_prompt_path = Path(os.path.join(new_base_path, 'test0_corpus.json'))
    adv_prompt_path.write_text(json.dumps(attack_jsons, ensure_ascii=False, indent=4), encoding='utf-8')
    print(f"Questions generated successfully and saved to {adv_prompt_path}")


def run_gragpoison_pipeline(
    clean_path: str,
    new_base_path: str,
    config: GRAGPOISONConfig = None
):
    """
    运行完整的GRAGPOISON攻击流程

    Args:
        clean_path: 原始数据路径
        new_base_path: 输出路径
        config: GRAGPOISON配置，如果为None则使用默认配置

    Example:
        >>> from gragpoison import GRAGPOISONConfig, RECOMMENDED_DATASET_PATH
        >>> config = GRAGPOISONConfig(N_alpha=10, N_beta=5, black_box=True)
        >>> run_gragpoison_pipeline(
        ...     RECOMMENDED_DATASET_PATH,
        ...     RECOMMENDED_DATASET_PATH + "_output",
        ...     config
        ... )
    """
    if config is None:
        from .config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG

    print("="*60)
    print("GRAGPOISON Pipeline Started")
    print("="*60)
    print(f"Clean path: {clean_path}")
    print(f"Output path: {new_base_path}")
    print(f"Config: Nα={config.N_alpha}, Nβ={config.N_beta}, black_box={config.black_box}")
    print("="*60)

    # Step 1: 生成攻击文本
    print("\n[Step 1/4] Generating attack texts...")
    process_questions_v2(clean_path, new_base_path, config)

    # Step 2: 重写文本（关系合并）
    print("\n[Step 2/4] Rewriting texts with relation merging...")
    rewrite_txt_v2_only_writeone(
        new_base_path,
        repeat_count=config.repeat_count,
        num_keep_direct=config.N_alpha,
        num_keep_indirect=config.N_beta,
        shuffle=config.shuffle
    )

    # Step 3: 运行GraphRAG索引
    print("\n[Step 3/4] Running GraphRAG indexing...")
    run_graphrag_indexing(new_base_path, config.graphrag_target_dir)

    # Step 4: 评估（如果有evaluator模块）
    print("\n[Step 4/4] Evaluation...")
    corpus_file = os.path.join(new_base_path, 'test0_corpus.json')
    try:
        from .evaluation.evaluator import process_corpus_file
        process_corpus_file(new_base_path, corpus_file)
    except ImportError:
        print("Evaluation module not implemented yet. Skipping evaluation.")

    print("\n" + "="*60)
    print("GRAGPOISON Pipeline Completed!")
    print("="*60)

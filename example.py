"""
GRAGPOISON Pipeline Example

完整的可运行示例，展示如何使用gragpoison包执行攻击流程
类似于原始的pipeline_1207.py
"""

import os
import sys
import shutil
import subprocess

# 添加gragpoison到Python路径
sys.path.insert(0, '/data3/jiacheng/graphrag')

from gragpoison import load_question_sets, GRAGPOISONConfig, RECOMMENDED_DATASET_PATH
from gragpoison.attack import (
    BLACKBOX_PROMPT,
    SEARCH_NEW_MIDDLE_PROMPT,
    GEN_CORPUS_PROMPT,
    GEN_CORPUS_PROMPT_RM2
)
from gragpoison.utils import ask_llm


def run_graphrag_indexing(new_path: str):
    """
    运行GraphRAG索引

    从pipeline_1207.py lines 11-42提取
    """
    original_dir = new_path
    target_dir = '/home/ljc/data/graphrag/'

    try:
        os.chdir(target_dir)

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


def example_1_load_data():
    """示例1: 加载数据"""
    print("\n" + "="*60)
    print("示例1: 加载数据")
    print("="*60)

    # 使用推荐的数据集路径
    base_path = RECOMMENDED_DATASET_PATH

    # 加载filtered版本的问题集
    question_sets = load_question_sets(base_path, use_filtered=True)

    print(f"✓ 成功加载 {len(question_sets)} 个问题集")

    # 显示第一个问题集的信息
    if question_sets:
        first_set = question_sets[0]
        print(f"\n第一个问题集包含 {len(first_set.get('questions', []))} 个问题")

        if 'questions' in first_set and first_set['questions']:
            first_q = first_set['questions'][0]
            print(f"第一个问题: {first_q.get('question', 'N/A')}")
            print(f"Root nodes: {first_q.get('root_nodes', 'N/A')}")
            print(f"Middle node: {first_q.get('middle_node', 'N/A')}")
            print(f"Leaf nodes: {first_q.get('leaf_nodes', 'N/A')}")


def example_2_use_config():
    """示例2: 使用配置"""
    print("\n" + "="*60)
    print("示例2: 配置管理")
    print("="*60)

    # 创建black-box配置
    config_blackbox = GRAGPOISONConfig(
        N_alpha=10,
        N_beta=5,
        black_box=True,
        use_filtered_questions=True
    )

    print(f"✓ Black-box配置:")
    print(f"  - Nα (direct variants): {config_blackbox.N_alpha}")
    print(f"  - Nβ (supporting relations): {config_blackbox.N_beta}")
    print(f"  - Black-box模式: {config_blackbox.black_box}")
    print(f"  - 使用filtered问题: {config_blackbox.use_filtered_questions}")

    # 创建white-box配置
    config_whitebox = GRAGPOISONConfig(
        N_alpha=10,
        N_beta=5,
        black_box=False,
        remove_negation=True  # 不使用negation
    )

    print(f"\n✓ White-box配置:")
    print(f"  - Black-box模式: {config_whitebox.black_box}")
    print(f"  - 移除negation: {config_whitebox.remove_negation}")


def example_3_use_prompts():
    """示例3: 使用攻击提示词"""
    print("\n" + "="*60)
    print("示例3: 使用攻击提示词")
    print("="*60)

    print("✓ 可用的提示词:")
    print("  1. BLACKBOX_PROMPT - 用于KG-agnostic模式")
    print("  2. SEARCH_NEW_MIDDLE_PROMPT - 查找Modified Middle Node")
    print("  3. GEN_CORPUS_PROMPT - 生成攻击文本 (with negation)")
    print("  4. GEN_CORPUS_PROMPT_RM2 - 生成攻击文本 (without negation)")

    # 示例：查找Modified Middle Node
    print("\n示例：查找Modified Middle Node")
    print("-" * 40)

    example_prompt = """
Given [Root Node, Original Middle Node] is [China, Beijing]
The chain of thoughts of their relationships is "The capital of China is Beijing."
"""

    print(f"输入: {example_prompt.strip()}")
    print("\n注意: 实际使用时需要调用 ask_llm(SEARCH_NEW_MIDDLE_PROMPT, example_prompt)")
    print("这会返回类似: {'Root Node': ['China'], 'Original Middle Node': 'Beijing', 'Modified Middle Node': 'Shanghai'}")


def example_4_simple_pipeline():
    """示例4: 简单的pipeline流程"""
    print("\n" + "="*60)
    print("示例4: 简单Pipeline流程")
    print("="*60)

    # 配置
    config = GRAGPOISONConfig(
        N_alpha=10,
        N_beta=5,
        black_box=True,
        use_filtered_questions=True
    )

    print("步骤1: 加载数据")
    base_path = RECOMMENDED_DATASET_PATH
    question_sets = load_question_sets(base_path, use_filtered=config.use_filtered_questions)
    print(f"  ✓ 加载了 {len(question_sets)} 个问题集")

    print("\n步骤2: 处理每个问题集")
    print("  (实际实现需要attack模块)")
    print("  - 对每个问题集:")
    print("    a. 提取root_nodes, middle_node, leaf_nodes")
    print("    b. 使用SEARCH_NEW_MIDDLE_PROMPT查找Modified Middle Node")
    print("    c. 使用GEN_CORPUS_PROMPT生成攻击文本")
    print("       - Direct attack texts (Nα=10)")
    print("       - Indirect attack texts (Nβ=5)")
    print("       - Enhanced attack texts")

    print("\n步骤3: 保存攻击文本")
    print("  - adv_texts_direct_test0.txt")
    print("  - adv_texts_indirect_test0.txt")
    print("  - adv_texts_enhanced_test0.txt")

    print("\n步骤4: 运行GraphRAG索引")
    print("  - 调用 run_graphrag_indexing(new_base_path)")

    print("\n步骤5: 评估攻击成功率")
    print("  - 计算ASR, R-ASR等指标")


def example_5_full_pipeline_template():
    """示例5: 完整Pipeline模板（需要实现attack模块）"""
    print("\n" + "="*60)
    print("示例5: 完整Pipeline模板")
    print("="*60)

    # 这是一个模板，展示完整流程应该如何组织
    template_code = '''
def run_full_pipeline(clean_path, new_base_path, config):
    """
    完整的GRAGPOISON攻击流程

    Args:
        clean_path: 原始数据路径
        new_base_path: 输出路径
        config: GRAGPOISONConfig配置对象
    """
    # 1. 复制数据到新路径
    shutil.copytree(clean_path, new_base_path)
    shutil.rmtree(os.path.join(new_base_path, 'output'), ignore_errors=True)
    shutil.rmtree(os.path.join(new_base_path, 'cache'), ignore_errors=True)

    # 2. 加载问题集
    question_sets = load_question_sets(new_base_path, use_filtered=config.use_filtered_questions)

    # 3. 生成攻击文本（需要实现attack模块）
    attack_jsons = []
    for question_set in question_sets:
        # a. 提取关系
        questions = question_set['questions']

        # b. 查找Modified Middle Node
        # new_middle_node = find_modified_middle_node(...)

        # c. 生成攻击文本
        # attack_json = generate_attack_texts(...)
        # attack_jsons.append(attack_json)
        pass

    # 4. 保存攻击文本
    # save_attack_texts(attack_jsons, new_base_path, config)

    # 5. 运行GraphRAG索引
    run_graphrag_indexing(new_base_path)

    # 6. 评估
    # evaluate_attack_success(new_base_path)

    print("Pipeline完成!")
'''

    print("完整Pipeline模板代码:")
    print(template_code)

    print("\n注意: 此模板需要以下模块才能运行:")
    print("  - attack/middle_node_finder.py")
    print("  - attack/injector.py")
    print("  - attack/enhancer.py")
    print("  - utils/text_processor.py")
    print("  - evaluation/evaluator.py")


def example_6_original_pipeline_equivalent():
    """示例6: 等价于原始pipeline_1207.py的代码"""
    print("\n" + "="*60)
    print("示例6: 原始Pipeline等价代码")
    print("="*60)

    # 这是原始pipeline_1207.py的等价代码
    original_equivalent = '''
# 原始pipeline_1207.py的主要逻辑
clean_paths = [
    "/home/ljc/data/graphrag/sp/misuque_3_v2",
]

for clean_path in clean_paths:
    new_base_path = clean_path + "_black_shuffle_0601"

    # 使用gragpoison重构后的代码:
    from gragpoison import GRAGPOISONConfig

    config = GRAGPOISONConfig(
        N_alpha=10,           # num_keep_direct
        N_beta=5,             # num_keep_indirect
        black_box=True,
        shuffle=True,
        repeat_count=1
    )

    # 步骤1: 生成攻击文本
    # process_questions_v2(clean_path, new_base_path,
    #                      black_box=config.black_box,
    #                      attack_middlewithleaf=False,
    #                      llama_model=False,
    #                      remove_2=False,
    #                      remove_1=False)

    # 步骤2: 重写文本
    # rewrite_txt_v2_only_writeone(new_base_path,
    #                              repeat_count=config.repeat_count,
    #                              num_keep_direct=config.N_alpha,
    #                              num_keep_indirect=config.N_beta,
    #                              shuffle=config.shuffle)

    # 步骤3: 运行GraphRAG索引
    run_graphrag_indexing(new_base_path)

    # 步骤4: 评估
    corpus_file = new_base_path + '/test0_corpus.json'
    # process_corpus_file(new_base_path, corpus_file)
'''

    print("原始pipeline_1207.py的等价代码:")
    print(original_equivalent)


def main():
    """主函数：运行所有示例"""
    print("\n" + "="*60)
    print("GRAGPOISON Pipeline 示例集合")
    print("="*60)

    # 运行所有示例
    example_1_load_data()
    example_2_use_config()
    example_3_use_prompts()
    example_4_simple_pipeline()
    example_5_full_pipeline_template()
    example_6_original_pipeline_equivalent()

    print("\n" + "="*60)
    print("所有示例运行完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 实现attack模块的剩余函数")
    print("2. 实现utils/text_processor.py")
    print("3. 实现evaluation/evaluator.py")
    print("4. 创建完整的pipeline.py")
    print("\n参考: /data3/jiacheng/graphrag/gragpoison/README.md")


if __name__ == "__main__":
    main()

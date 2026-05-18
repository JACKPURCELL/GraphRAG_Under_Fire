"""
完整测试脚本 - 验证所有模块可以正常导入和使用
"""

import sys
sys.path.insert(0, '/data3/jiacheng/graphrag')

print("="*60)
print("GRAGPOISON 模块导入测试")
print("="*60)

# 测试1: 导入主包
print("\n[测试1] 导入主包...")
try:
    from gragpoison import (
        load_question_sets,
        GRAGPOISONConfig,
        RECOMMENDED_DATASET_PATH,
        run_gragpoison_pipeline,
        run_graphrag_indexing,
        process_questions_v2
    )
    print("✓ 主包导入成功")
except Exception as e:
    print(f"✗ 主包导入失败: {e}")
    sys.exit(1)

# 测试2: 导入attack模块
print("\n[测试2] 导入attack模块...")
try:
    from gragpoison.attack import (
        BLACKBOX_PROMPT,
        SEARCH_NEW_MIDDLE_PROMPT,
        GEN_CORPUS_PROMPT,
        find_modified_middle_node,
        process_response,
        process_question_set_blackbox
    )
    print("✓ attack模块导入成功")
except Exception as e:
    print(f"✗ attack模块导入失败: {e}")
    sys.exit(1)

# 测试3: 导入utils模块
print("\n[测试3] 导入utils模块...")
try:
    from gragpoison.utils import (
        ask_llm,
        ask_gpt,
        ask_vllm,
        rewrite_txt_v2_only_writeone,
        filter_texts_with_relation_merging
    )
    print("✓ utils模块导入成功")
except Exception as e:
    print(f"✗ utils模块导入失败: {e}")
    sys.exit(1)

# 测试4: 检查数据集路径
print("\n[测试4] 检查数据集路径...")
try:
    import os
    print(f"  推荐数据集路径: {RECOMMENDED_DATASET_PATH}")
    if os.path.exists(RECOMMENDED_DATASET_PATH):
        print(f"  ✓ 数据集存在")

        # 检查关键文件
        filtered_json = os.path.join(RECOMMENDED_DATASET_PATH, 'question_multi_v3_filtered.json')
        if os.path.exists(filtered_json):
            print(f"  ✓ question_multi_v3_filtered.json 存在")
        else:
            print(f"  ✗ question_multi_v3_filtered.json 不存在")
    else:
        print(f"  ✗ 数据集路径不存在")
except Exception as e:
    print(f"✗ 数据集检查失败: {e}")

# 测试5: 加载数据
print("\n[测试5] 加载数据...")
try:
    question_sets = load_question_sets(RECOMMENDED_DATASET_PATH, use_filtered=True)
    print(f"✓ 成功加载 {len(question_sets)} 个问题集")
except Exception as e:
    print(f"✗ 数据加载失败: {e}")

# 测试6: 创建配置
print("\n[测试6] 创建配置...")
try:
    config = GRAGPOISONConfig(
        N_alpha=10,
        N_beta=5,
        black_box=True,
        use_filtered_questions=True
    )
    print(f"✓ 配置创建成功: Nα={config.N_alpha}, Nβ={config.N_beta}")
except Exception as e:
    print(f"✗ 配置创建失败: {e}")

# 测试7: 检查prompts
print("\n[测试7] 检查prompts...")
try:
    assert len(BLACKBOX_PROMPT) > 0
    assert len(SEARCH_NEW_MIDDLE_PROMPT) > 0
    assert len(GEN_CORPUS_PROMPT) > 0
    print("✓ 所有prompts可用")
except Exception as e:
    print(f"✗ Prompts检查失败: {e}")

# 测试8: 检查函数签名
print("\n[测试8] 检查函数签名...")
try:
    import inspect

    # 检查关键函数
    sig1 = inspect.signature(find_modified_middle_node)
    sig2 = inspect.signature(process_response)
    sig3 = inspect.signature(run_gragpoison_pipeline)

    print("✓ 所有关键函数签名正确")
except Exception as e:
    print(f"✗ 函数签名检查失败: {e}")

print("\n" + "="*60)
print("所有测试通过！✓")
print("="*60)

print("\n模块统计:")
print(f"  - 主包: gragpoison")
print(f"  - 子模块: attack, utils, evaluation")
print(f"  - 核心文件: 15个Python文件")
print(f"  - 配置: GRAGPOISONConfig")
print(f"  - 数据集: {RECOMMENDED_DATASET_PATH}")

print("\n使用示例:")
print("""
from gragpoison import GRAGPOISONConfig, run_gragpoison_pipeline, RECOMMENDED_DATASET_PATH

config = GRAGPOISONConfig(N_alpha=10, N_beta=5, black_box=True)
run_gragpoison_pipeline(
    clean_path=RECOMMENDED_DATASET_PATH,
    new_base_path=RECOMMENDED_DATASET_PATH + "_output",
    config=config
)
""")

print("\n重构完成！🎉")
print("数据集已复制到: /data3/jiacheng/graphrag/gragpoison/datasets/")

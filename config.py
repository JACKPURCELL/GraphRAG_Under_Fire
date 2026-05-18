"""
Configuration Module

GRAGPOISON算法超参数配置
"""

from dataclasses import dataclass


@dataclass
class GRAGPOISONConfig:
    """GRAGPOISON算法超参数配置"""

    # Hyperparameters from paper
    N_alpha: int = 10  # Direct attack variants per root node (Nα)
    N_beta: int = 5  # Supporting relations per modified middle node (Nβ)
    token_budget: int = 400  # Target words per adversarial text

    # Processing parameters
    repeat_count: int = 1  # Text repetition factor
    shuffle: bool = False  # Shuffle texts before saving

    # Data Loading
    use_filtered_questions: bool = False  # 使用question_multi_v3_filtered.json

    # Relation Merging (关系合并)
    # 自动实现：如果连续问题的(root_nodes, middle_node)相同，共用direct attack texts
    # 这在text_processor.py的filter_texts_with_relation_merging中自动处理

    # Attack mode
    black_box: bool = False  # KG-agnostic (True) vs KG-aware (False)
    remove_negation: bool = False  # Use GEN_CORPUS_PROMPT_RM2 if True
    attack_middlewithleaf: bool = False  # Attack middle-leaf path instead of root-middle

    # Model configuration
    llm_model: str = "gpt-4o-2024-08-06"
    vllm_model: str = "Qwen/Qwen3-8B"
    use_llama: bool = False  # Use VLLM instead of GPT

    # Paths
    graphrag_target_dir: str = "/home/ljc/data/graphrag/"

    # Evaluation
    max_threads: int = 3  # Concurrent evaluation threads


# Default configuration
DEFAULT_CONFIG = GRAGPOISONConfig()

# Recommended dataset path (已复制到gragpoison/datasets/)
RECOMMENDED_DATASET_PATH = "/data3/jiacheng/graphrag/gragpoison/datasets/misuque_3_black_shuffle_0601"

# 原始数据集路径（备用）
ORIGINAL_DATASET_PATH = "/home/stufs1/jiachliang/graphrag/sp/misuque_3_black_shuffle_0601"

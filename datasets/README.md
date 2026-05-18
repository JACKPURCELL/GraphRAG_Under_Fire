# GRAGPOISON Datasets

本目录包含GRAGPOISON算法使用的数据集。

## 数据集列表

### 1. misuque_3_black_shuffle_0601

**路径**: `datasets/misuque_3_black_shuffle_0601/`

**大小**: 155MB

**描述**: Musique数据集的处理版本，用于black-box攻击测试

**包含文件**:
- `question_multi_v3_filtered.json` (1.1MB) - 过滤后的问题集（推荐使用）
- `question_multi_v3.json` (1.6MB) - 完整问题集
- `test0_corpus_filtered.json` (563KB) - 过滤后的攻击文本
- `test0_corpus.json` (779KB) - 完整攻击文本
- `settings.yaml` (5.1KB) - GraphRAG配置
- `input/` - 输入文本目录
- `output/` - GraphRAG输出目录
- `cache/` - 缓存目录
- `prompts/` - 提示词目录

**使用方法**:
```python
from gragpoison import load_question_sets, RECOMMENDED_DATASET_PATH

# 加载filtered版本（推荐）
question_sets = load_question_sets(RECOMMENDED_DATASET_PATH, use_filtered=True)

# 加载完整版本
question_sets = load_question_sets(RECOMMENDED_DATASET_PATH, use_filtered=False)
```

## 数据集结构

每个数据集应包含以下文件：

```
dataset_name/
├── question_multi_v3.json              # 问题集（必需）
├── question_multi_v3_filtered.json     # 过滤后的问题集（可选）
├── settings.yaml                       # GraphRAG配置（必需）
├── input/                              # 输入文本目录
│   ├── adv_texts_direct_test0.txt
│   ├── adv_texts_indirect_test0.txt
│   └── adv_texts_enhanced_test0.txt
├── output/                             # GraphRAG输出目录
└── cache/                              # 缓存目录
```

## question_multi_v3.json 格式

```json
[
  {
    "questions": [
      {
        "question": "问题文本",
        "root_nodes": "根节点或根节点列表",
        "middle_node": "中间节点",
        "leaf_nodes": ["叶子节点列表"],
        "chain_of_thoughts": ["推理步骤"],
        "Template Relationship between root and middle node": ["模板"],
        "Template Relationship between middle and leaf node": ["模板"],
        "Template Relationship between root and leaf node": ["模板"]
      }
    ]
  }
]
```

## 添加新数据集

1. 将数据集复制到 `datasets/` 目录
2. 确保包含必需的文件（见上文）
3. 在代码中使用：

```python
from gragpoison import load_question_sets

custom_dataset_path = "/data3/jiacheng/graphrag/gragpoison/datasets/your_dataset"
question_sets = load_question_sets(custom_dataset_path, use_filtered=True)
```

## 数据集来源

- **misuque_3_black_shuffle_0601**: 从 `/home/stufs1/jiachliang/graphrag/sp/misuque_3_black_shuffle_0601` 复制
- 基于Musique数据集处理生成
- 用于GraphRAG adversarial attack研究

## 注意事项

1. 数据集文件较大（155MB），请确保有足够的磁盘空间
2. 推荐使用 `filtered` 版本以获得更好的性能
3. `output/` 和 `cache/` 目录会在运行pipeline时自动生成
4. 不要手动修改 `test0_corpus.json`，它由pipeline自动生成

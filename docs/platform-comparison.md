# Platform Comparison

## 结论

目前已经有一些平台分别覆盖了：

- 数据整理与数据清洗
- 微调与继续训练
- 低代码或无代码界面
- 训练编排

但我没有看到一个成熟平台，能够同时把下面这组能力完整组合起来：

- 面向科学/材料领域的多源数据接入
- provenance / license / dedup / schema 统一
- 训练数据编译视图
- pretraining / continued pretraining / fine-tuning / post-training 的统一平台叙事
- 本地开发 + Spark 批处理 + Flink 流处理
- 最终走向对话式 / 拖拽式工作流

Lattice 的真正差异点，不是单个功能，而是这组能力的**组合**。

## 说明

表格中的标记含义：

- `✅`：官方文档明确支持或当前仓库已验证
- `◐`：部分支持 / 间接支持 / 不是核心定位
- `❌`：未看到明确支持
- `🎯`：Lattice 的目标能力，当前仓库未完全实现

## 平台能力对比

| 平台 | 开源 | 科学/材料垂域聚焦 | 多源数据编译 | provenance / license / dedup 作为核心 | pretraining / continued pretraining / fine-tuning / post-training 的统一平台叙事 | 本地执行 | Spark | Flink | 对话/拖拽式工作流 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Lattice（当前）** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ◐ | ❌ |
| **Lattice（目标）** | ✅ | ✅ | ✅ | ✅ | 🎯 | 🎯 | 🎯 | 🎯 | 🎯 |
| NVIDIA NeMo Curator | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ◐ | ❌ | ❌ |
| Databricks Mosaic AI Model Training | ❌ | ❌ | ◐ | ◐ | ✅ | ❌ | ✅ | ❌ | ◐ |
| H2O Enterprise LLM Studio / DataStudio | ❌ | ❌ | ◐ | ◐ | ◐ | ◐ | ❌ | ❌ | ✅ |
| Sparkflows | ❌ | ❌ | ◐ | ❌ | ◐ | ◐ | ✅ | ❌ | ✅ |
| Kubeflow | ✅ | ❌ | ❌ | ❌ | ◐ | ✅ | ❌ | ❌ | ❌ |

## 这些平台分别强在哪里

### NVIDIA NeMo Curator

强项：

- 开源
- 大规模数据整理能力强
- 数据清洗、过滤、去重、质量控制能力强
- 从单机到集群的扩展路径明确

局限：

- 更像数据整理平台，不是完整的训练平台
- 官方当前主要强调 Ray 等分布式数据处理，不是 Flink
- 不以科学/材料多源数据编译为中心

### Databricks Mosaic AI Model Training

强项：

- continued training / fine-tuning 支持明确
- 数据、训练、MLflow、catalog、部署串得很紧
- 工程完整度高

局限：

- 云平台路线很强，本地优先不强
- 不是开源
- 不是从多源科学数据编译切入
- 没有你们想要的科学/材料数据基础设施定位

### H2O Enterprise LLM Studio / DataStudio

强项：

- 很接近低代码 / UI 驱动工作流
- 数据上传、数据准备、fine-tuning、部署体验较完整
- 适合企业文档和应用型场景

局限：

- 重点是 fine-tuning，不是统一的大模型全生命周期平台
- 不是科学/材料数据平台
- 没有 Spark / Flink 这类执行引擎叙事

### Sparkflows

强项：

- 强调 no-code / low-code
- 强调快速做 LLM fine-tuning
- 更偏应用产品化

局限：

- 不是开源科学数据平台
- 数据层和训练层没有形成深度统一
- 没有明显的多源科学数据编译定位

### Kubeflow

强项：

- 开源
- 训练编排和本地执行能力明确
- LLM fine-tuning 路线逐步增强

局限：

- 它强在 orchestration，不强在多源数据编译
- 不是数据中心平台
- 不是科学/材料垂域数据基础设施

## Lattice 的差异化：我们有什么，他们通常没有

下面这些点，很多平台会各自覆盖其中一部分，但**没有一个对比对象明显把它们完整放在一起**：

| 差异点 | Lattice 当前 | Lattice 目标 | 为什么重要 |
|---|---:|---:|---|
| 科学/材料垂域作为第一目标场景 | ✅ | ✅ | 垂域数据更难、更分散，壁垒更高 |
| 把多源 scientific sources 当成平台输入层 | ✅ | ✅ | 不只是接训练集，而是接原始知识来源 |
| 把 provenance / license / dedup 当成第一层能力 | ✅ | ✅ | 这决定平台是否可信、可扩展、可开源 |
| 把数据编译成多种训练视图 | ✅ | ✅ | 数据不是只存起来，而是直接服务训练 |
| 本地开发可跑 | ✅ | ✅ | 降低迭代门槛，便于研究和工程调试 |
| Spark 批处理可跑 | ✅ | ✅ | 让 pipeline 具备现实扩展性 |
| Flink 流处理纳入平台设计 | ◐ | 🎯 | 让平台不仅能做 batch，也能做持续更新 |
| 把数据平台与训练平台统一叙事 | ❌ | 🎯 | 这是区别于单点工具的关键 |
| 对话式 / 拖拽式工作流 | ❌ | 🎯 | 这是后续产品体验层，而不是当前核心壁垒 |

## 现在最准确的判断

如果你问：

> “目前有这样的平台吗？”

我的判断是：

- **有相似平台**
- **但没有一个完全等同于你们要做的东西**
- **你们的价值不在单个功能，而在能力组合**

更具体地说：

- NeMo Curator 更像数据整理基础设施
- Databricks 更像云上的训练与部署平台
- H2O / Sparkflows 更像低代码微调产品
- Kubeflow 更像训练编排底座

而你们的方向是：

> **一个面向科学/材料领域的大模型数据与训练平台，从多源数据编译出发，逐步走向全生命周期训练工作流平台。**

## 影响力判断

如果 Lattice 最后真的做到下面三件事，影响力会很强：

1. 多源科学数据能被稳定编译成高质量训练数据  
2. 这条链能在本地和分布式引擎上执行  
3. 这些数据能真实支撑 continued pretraining / fine-tuning / post-training

影响力来源会是三方面：

- 研究影响力：可复现的数据构建与训练基础设施
- 工程影响力：本地到分布式的一致执行层
- 产品影响力：把复杂训练流程变成低门槛平台体验

## 官方参考

- NVIDIA NeMo Curator overview: https://docs.nvidia.com/nemo/curator/latest/about/index.html
- NeMo Curator text curation: https://docs.nvidia.com/nemo-framework/user-guide/latest/datacuration/text-curation.html
- Databricks Mosaic AI Model Training / Foundation Model Fine-tuning: https://docs.databricks.com/aws/en/large-language-models/foundation-model-training
- Databricks data preparation for training: https://docs.databricks.com/aws/en/large-language-models/foundation-model-training/data-preparation
- H2O Enterprise LLM Studio overview: https://docs.h2o.ai/h2o-enterprise-llm-studio/get-started/what-is-h2o-enterprise-llm-studio
- H2O datasets workflow: https://docs.h2o.ai/h2o-enterprise-llm-studio/datasets
- Sparkflows fine-tune page: https://www.sparkflows.ai/fine-tune-llm
- Kubeflow 1.11 release: https://blog.kubeflow.org/kubeflow-1.11-release/
- Kubeflow local execution mode: https://www.kubeflow.org/docs/components/trainer/user-guides/local-execution-mode/
- Kubeflow builtin trainer guide: https://www.kubeflow.org/docs/components/trainer/user-guides/builtin-trainer/

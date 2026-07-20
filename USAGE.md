# 仓库目录使用手册

## 工作与目录

| 工作 | 目录/文件 | 主要负责人 |
|---|---|---|
| VLA 加载、动作推理、适配器 | `models/` | 组员 1 |
| patch、EOT、攻击样本 | `attacks/` | 组员 2 |
| 输入预处理、patch 增强、视觉编码器鲁棒微调 | `defense/` | 组员 3 |
| 任务成功率、动作/轨迹指标、图表 | `eval/` | 组员 1/2/5 |
| 可复现实验参数 | `configs/` | 共用，组员 1 把关 |
| 本地观测、权重与大文件 | `data/` | 组员 5，不提交 Git |
| 阅读记录、实验日志与结果 | `experiments/` | 全员 |

## 核心约定

1. VLA 模型接口为 `predict_action(image, instruction)`，输出一维动作向量；修改动作维度或归一化方式时必须同步配置与文档。
2. 防御接口仍接受并返回 `(H, W, 3)` 的 `uint8` 图像，使其能插在视觉观测与 VLA 之间。
3. 一次有效 VLA 实验至少记录：commit、模型/权重、任务、初始状态、seed、语言指令、每步动作、最终 success 和失败原因。
4. clean / attacked / defended 必须复用同一批任务与初始化。主要比较任务成功率，分类准确率只能作为辅助诊断。
5. 权重、数据集、仿真资产和生成图片不得直接提交。只提交配置、代码、小型示例和汇总结果。

## experiments 记录模板

```markdown
# 实验名称
- 日期 / 执行人 / commit：
- 环境 / GPU / 依赖：
- 模型、权重、unnorm_key：
- LIBERO suite、task、episodes、seed：
- 攻击预算与 patch 设置：
- 防御设置：

| condition | successes / total | task success rate | mean action L2 |
|---|---:|---:|---:|
| clean | | | 0 |
| attacked | | | |
| defended | | | |

失败案例、复现障碍与下一步：
```

## 常用命令

```bash
# 无权重接口测试
python models/test_vla_interface.py

# 检查改动
git status --short
git diff --check

# 只提交本人负责的文件
git add <files>
git commit -m "type: concise description"
```

旧 CLIP 文件只为历史兼容。新实验使用 `configs/vla_baseline.yaml`，不要继续把 `configs/baseline.yaml` 的分类标签当作 VLA 评测基准。

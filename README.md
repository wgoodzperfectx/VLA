# VLA Patch Robustness Lab

视觉语言动作模型的对抗补丁与动作鲁棒性研究原型。项目关注图像中的局部扰动是否改变机器人动作，以及如何在相同任务和初始状态下评价防御效果。

> **当前阶段：研究原型。** 本仓库公开动作接口、数字补丁基线、评估函数与实验设计。离线接口测试不加载模型权重，不能证明攻击成功、动作安全或机器人任务成功率。研究进度与证据边界见[公开状态](docs/research-status.md)。

## 已公开的内容

| 模块 | 当前可验证内容 | 状态 |
| --- | --- | --- |
| `models/vla_baseline.py` | OpenVLA 图像加指令到 7 维动作的延迟加载适配器；提示词、图像输入和动作形状检查 | 接口已实现；真实推理未在本仓库验证 |
| `models/test_vla_interface.py` | 无权重离线 smoke test | 可本地运行 |
| `attacks/digital_patch.py` | 随机 RGB 补丁生成及图像贴片示例 | 数字域基线；不是优化攻击 |
| `eval/metrics.py` | 任务成功率与配对动作轨迹 L2 偏差计算函数 | 函数已实现；没有正式 rollout 结果 |
| `configs/vla_baseline.yaml`、`experiments/` | 候选配置、威胁模型与阅读记录 | 研究设计，不等于已完成实验 |

## 本地快速检查

建议在隔离的 Python 环境中安装 [`requirements.txt`](requirements.txt) 所列依赖，然后运行：

```bash
python models/test_vla_interface.py
```

该命令只检查图像转换、OpenVLA 提示词与 7 维有限动作向量，不下载模型或数据集。真实 OpenVLA 推理需要单独准备模型、处理器、CUDA 环境，并核对数据集动作语义与 `unnorm_key`；仓库默认值不是已验证的数据适配结论。

## 研究流程

```text
图像观测 + 任务指令
        │
        ├── clean ────────────────┐
        ├── attacked：局部 RGB 补丁 ├── VLA 动作 / 轨迹 ── 配对评估
        └── defended：防御后观测 ───┘
```

计划中的主指标是闭环任务成功率，辅助指标是对齐动作轨迹的偏差。三种条件必须使用相同任务、初始状态与随机种子。当前仓库**没有**经验证的闭环机器人或仿真 rollout，也没有可报告的攻击成功率和防御增益。图像分类结果不能替代 VLA 动作结果。

## 目录

| 路径 | 用途 |
| --- | --- |
| [`models/`](models/) | OpenVLA 动作接口与历史 CLIP/VLM 基线 |
| [`attacks/`](attacks/) | 数字补丁示例 |
| [`defense/`](defense/) | 防御模块接口预留 |
| [`eval/`](eval/) | 指标函数 |
| [`configs/`](configs/) | 候选配置 |
| [`experiments/`](experiments/) | 实验设计与阅读记录 |
| [`USAGE.md`](USAGE.md) | 目录约定和实验记录要求 |

## 项目边界

本仓库不包含 BridgeData2 或其他受限数据、模型权重、原始生成记录和私有研究记忆。后续正式科学结论需要独立标注、有效输出判定、预先确定的指标与配对实验。

## 参考实现

- [OpenVLA](https://github.com/openvla/openvla)
- [OpenVLA-OFT](https://github.com/moojink/openvla-oft)
- [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
- [LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus)

这些项目是研究参考，不代表本仓库已经复现其结果。仓库尚未附独立许可证；复用代码或素材前请联系仓库维护者确认授权。

# 组员 1：VLA 基线说明与第一阶段实验方案

## 1. 基线结论

第一阶段采用 **OpenVLA-OFT + LIBERO** 作为可执行任务基线，并用 **LIBERO-Plus** 进行视觉前端鲁棒性压力测试。原版 OpenVLA 7B 用作统一推理接口和架构参照；算力允许后再接入 OFT 的 LIBERO 专用权重跑完整 rollout。当前仓库已提供 OpenVLA 单步动作接口和无需下载权重的离线接口测试，但本文不把接口测试当作真实模型实验结果。

最小技术流程：

```text
视觉观测 + 语言指令
        -> VLA 模型（OpenVLA / OpenVLA-OFT）
        -> 机器人动作或动作块
        -> LIBERO 仿真 rollout
        -> 任务成功率 + 动作轨迹偏差
```

## 2. VLA 是什么，与 VL/VLM 有何区别

| 类型 | 输入 | 输出 | 本项目关注的失败 |
|---|---|---|---|
| VL | 图像与文本 | 相似度、检索或分类结果 | 图文匹配错误 |
| VLM | 图像与语言指令 | 文本回答或语义表示 | 描述、问答或推理错误 |
| VLA | 视觉观测、语言指令，可选机器人状态 | 可执行动作或动作序列 | 轨迹偏移、抓错物体、碰撞、任务失败 |

OpenVLA 把视觉与语言表征映射为机器人动作。官方 `openvla-7b` 使用融合的 DINOv2/SigLIP 视觉骨干和 Llama-2 系列语言模型，并在 Open X-Embodiment 的约 97 万条机器人轨迹上训练。OpenVLA-OFT 在此基础上使用连续动作、动作分块和多图像输入等优化，更适合 LIBERO 闭环评测。

## 3. 为什么适合本课题

本课题研究的是视觉前端受到物理域 patch 干扰后，错误如何传导到动作执行。VLA 把“看错”直接连接到“做错”，因而不能只看分类准确率，必须观察完整 rollout。原项目的 patch、输入增强和视觉编码器对抗微调仍可迁移，但安全属性改为任务可靠性与动作稳定性。

前端鲁棒增强的目标不是让每帧表征看起来更干净，而是在尽量保持 clean 任务成功率的同时，提高 attacked 条件下的成功率并减小动作偏差。

## 4. 第一阶段基准选择

### OpenVLA / OpenVLA-OFT

- 原版 OpenVLA 提供清晰的 `image + instruction -> 7-DoF action` 参考接口，便于统一攻击、防御与评估模块。
- OpenVLA-OFT 官方提供 LIBERO 微调权重，连续动作与动作块推理更适合第一轮闭环复现。
- 不从头训练 7B 模型；先复现推理和评测，后续只考虑 LoRA、视觉前端微调或 mix-SFT。

### LIBERO

LIBERO 含 Spatial、Object、Goal 与 LIBERO-100 等机器人操作任务套件，环境通过稀疏成功信号判断任务是否完成。它适合建立 clean baseline，并记录每步动作、奖励和最终成功状态。

### LIBERO-Plus

LIBERO-Plus 在物体布局、相机视角、机器人初始状态、语言指令、光照、背景纹理和传感器噪声七个维度上扩展鲁棒性评测。第一阶段先用它定位视觉前端最脆弱的扰动，再加入物理 patch 和防御；不能把自然分布偏移与对抗攻击混为一谈。

## 5. 威胁模型与最小实验

- 安全对象：VLA 的视觉前端及其下游动作策略。
- 攻击者：可在相机可见场景中放置固定 patch；第一版不修改语言、机器人状态或模型权重。
- 攻击知识：先做白盒/灰盒数字合成以验证机制，再测试跨视角、光照和模型迁移。
- 成功条件：相对 clean 条件造成任务失败或显著动作偏差；单帧分类变化不算最终攻击成功。
- 防御目标：提高 attacked + defended 的任务成功率，同时控制 clean 性能损失。

假设：视觉前端 patch 会降低 LIBERO 任务成功率；包含 patch 数据增强或视觉编码器鲁棒微调的防御能恢复部分成功率，且不应明显损害 clean rollout。

最小对照实验：

| 条件 | 输入 | 防御 | 目的 |
|---|---|---|---|
| clean | 原始观测 | 无 | 原始任务能力 |
| attacked | patch 观测 | 无 | 攻击影响 |
| defended | 同一 patch 观测 | 视觉前端防御 | 防御收益与代价 |

固定模型权重、任务、初始状态、seed、episode 数和 patch 预算；自变量只有实验条件。主指标为任务成功率，辅指标为相对 clean 轨迹的平均/最大动作 L2 偏差。后续再加入碰撞率、动作突变次数和推理延迟。

建议先用 1 个 LIBERO suite、每任务 20 个 episode、3 个随机种子。所有条件复用同一组初始状态；报告均值与离散程度，不以单条成功轨迹代替统计结果。

## 6. 环境、复现障碍与交付路径

- OpenVLA 7B 权重和 LIBERO/MuJoCo 环境较重，正式 rollout 建议在 Linux + CUDA 环境完成。
- 原版 OpenVLA 的动作反归一化键必须与训练数据/机器人 embodiment 匹配；错误的 `unnorm_key` 会产生无意义动作。
- Windows 当前只验证接口、配置与指标代码，不声称已完成真实模型精度复现。
- 接口：`models/vla_baseline.py`
- 离线测试：`python models/test_vla_interface.py`
- 实验配置：`configs/vla_baseline.yaml`
- 后续日志：`experiments/`，至少记录 commit、模型、任务、seed、条件、动作序列和成功状态。

## 7. 本轮结论与下一步

本轮完成了从 CLIP 分类基线到 VLA 动作基线的接口迁移。下一步是在可用 GPU/Linux 环境接入 OpenVLA-OFT 的 LIBERO 权重，先得到 clean task success rate，再加入固定数字 patch，最后比较 clean / attacked / defended 三组结果。失败实验也要记录依赖、显存、权重、动作归一化和仿真初始化等具体障碍。

## 参考资料

1. OpenVLA: <https://github.com/openvla/openvla>；论文：<https://arxiv.org/abs/2406.09246>
2. OpenVLA-OFT: <https://github.com/moojink/openvla-oft>；论文：<https://arxiv.org/abs/2502.19645>
3. LIBERO: <https://github.com/Lifelong-Robot-Learning/LIBERO>；论文：<https://arxiv.org/abs/2306.03310>
4. LIBERO-Plus: <https://github.com/sylvestf/LIBERO-plus>；论文：<https://arxiv.org/abs/2510.13626>
5. VLA 对抗补丁研究：<https://arxiv.org/abs/2411.13587>

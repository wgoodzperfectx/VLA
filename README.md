# 面向 VLA 的物理域对抗补丁鲁棒性增强

大创项目 · 成都信息工程大学网安学院

本项目研究视觉-语言-动作（VLA）模型在物理域对抗补丁下的任务可靠性。主线已经从“CLIP/VLM 分类是否出错”迁移为“视觉观测 + 语言指令是否产生安全、有效的机器人动作”。旧 CLIP 基线保留在 `models/vlm_baseline.py`，仅用于历史实验兼容。

## 当前 baseline

```text
视觉观测 + 语言指令
        -> OpenVLA / OpenVLA-OFT
        -> 动作或动作块
        -> LIBERO rollout
        -> 任务成功率与动作轨迹偏差
```

- 主功能基准：OpenVLA-OFT + LIBERO
- 架构参照：OpenVLA 7B
- 鲁棒性基准：LIBERO-Plus 七类扰动
- 实验条件：clean / attacked / defended
- 主指标：任务成功率；辅指标：动作 L2 偏差

完整选择依据、威胁模型和最小实验设计见 [组员 1 VLA baseline](experiments/week1_组员1_vla_baseline.md)。

## 快速验证

以下命令只验证统一动作接口，不下载 7B 权重：

```bash
pip install -r requirements.txt
python models/test_vla_interface.py
```

真实 OpenVLA 推理需要合适的 CUDA 环境、模型权重以及与机器人数据匹配的动作反归一化键：

```python
from models import OpenVLABaseline

policy = OpenVLABaseline()
action = policy.predict_action("observation.png", "pick up the red cup")
print(action)  # 7-DoF action
```

正式 LIBERO rollout 建议依照 OpenVLA-OFT 官方 Linux 环境配置执行。本仓库的 Windows smoke test 不是实际任务成功率实验。

## 项目结构

```text
VLA/
├── models/
│   ├── vla_baseline.py          # 当前 OpenVLA 动作推理接口
│   ├── test_vla_interface.py    # 无权重离线接口测试
│   └── vlm_baseline.py          # 旧 CLIP 分类基线（兼容）
├── attacks/                     # patch / EOT / 攻击流程
├── defense/                     # 视觉前端鲁棒增强
├── eval/metrics.py              # 任务成功率与动作偏差等指标
├── configs/vla_baseline.yaml    # VLA 第一阶段实验配置
├── data/                        # 本地观测数据，不提交大文件
├── experiments/                 # 研究说明与实验记录
├── TEAM.md
└── USAGE.md
```

## 统一接口

模型侧只暴露动作预测：

```python
action = policy.predict_action(image, instruction)
```

防御侧保持图像接口，便于插入 VLA 前端：

```python
def defend(image):
    """(H, W, 3) uint8 -> (H, W, 3) uint8"""
```

评估必须运行配对 rollout。相同任务、初始状态和 seed 下，比较原图、同一 patch 图和防御后的 patch 图；不能再用图像分类准确率代替 VLA 任务表现。

## 团队分工

- 组员 1：VLA baseline、主线整合、接口与最终 review
- 组员 2：VLA patch 攻击、威胁模型与攻击复现
- 组员 3：视觉前端防御、对抗微调与鲁棒增强
- 组员 4：项目统筹、文档、报告与答辩
- 组员 5：环境、rollout 日志、批量实验与结果统计

详细协作边界见 [TEAM.md](TEAM.md)，目录规则见 [USAGE.md](USAGE.md)。

## 参考项目

- [OpenVLA](https://github.com/openvla/openvla)
- [OpenVLA-OFT](https://github.com/moojink/openvla-oft)
- [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
- [LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus)

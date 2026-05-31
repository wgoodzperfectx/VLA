# 仓库目录使用手册 —— 我做了什么工作，上传到哪个目录

## 总览：一句话版

| 你做了什么 | 上传到 |
|-----------|--------|
| 加载/调用 VLM 模型、写推理函数 | models/ |
| 生成对抗补丁、写攻击算法、EOT 变换 | attacks/ |
| 写检测器、修复器、防御流程 | defense/ |
| 写准确率/ASR/延迟等评估函数 | eval/ |
| 调实验参数（模型名、补丁大小等） | configs/ |
| 测试用的干净图片、补丁图片 | data/（不入 Git） |
| 每次实验的参数、结果、备注 | experiments/ |
| 装了新依赖包 | requirements.txt |
| 项目介绍、跑法、分工说明 | README.md |

---

## 一、models/ —— VLM 模型相关，组员A 维护

**放什么：** 所有和 VLM 模型加载、推理、接口封装有关的代码。

**具体例子：**
- 加载 CLIP / LLaVA 模型的代码 → models/vlm_baseline.py
- 封装 classify(image) 统一推理接口 → models/vlm_baseline.py
- 切换模型（CLIP → BLIP → 其他）的适配代码 → models/ 里新建文件
- 验证模型能跑通的测试脚本 → models/test_clip.py
- 导出给外部用的 __init__.py → models/__init__.py

**规则：** 组员A 维护，别人只 import，不直接改。

---

## 二、attacks/ —— 对抗攻击相关，A+B 都可写

**放什么：** 所有生成对抗样本/补丁的代码。攻击方法、变换策略、补丁合成。

**具体例子：**
- 随机补丁 Baseline → attacks/digital_patch.py（组员A 写）
- AdvPatch 复现代码 → attacks/advpatch.py（组员B 写，新建文件！）
- EOT 旋转/亮度/缩放变换 → attacks/eot_transform.py（谁写谁建）
- PGD / FGSM 等白盒攻击 → attacks/whitebox_attack.py
- 补丁粘贴函数（apply_patch_to_image） → attacks/digital_patch.py
- 批量生成攻击样本的脚本 → attacks/generate_samples.py

**规则：** 各人建各人的文件，互不改对方代码。写完在 attacks/__init__.py 加 import。

---

## 三、defense/ —— 防御相关，组员B 维护

**放什么：** 所有防御/检测/修复/净化的代码。从检测补丁到修复图像到端到端防御。

**具体例子：**
- YOLO 目标检测（检测补丁区域） → defense/detector.py
- LaMa 图像修复（抹掉补丁） → defense/repair.py
- 快速平滑修复（轻量替代） → defense/fast_repair.py
- 异常注意力检测 → defense/attention_detector.py
- 统一防御入口 defend(image) → defense/ 里实现，__init__.py 导出
- Jetson 部署脚本 → defense/deploy_jetson.py

**接口约定（A 和 B 的边界）：**
- B 的输入：一张被攻击的图片 (H, W, 3) uint8 numpy array
- B 的输出：防御处理后的图片 (H, W, 3) uint8 numpy array
- A 调 B：from defense import defend; clean = defend(adv_image)

**规则：** 组员B 维护，接口定了之后 A 只调 defend()。

---

## 四、eval/ —— 评估指标，共用

**放什么：** 所有计算攻击效果/防御效果/推理速度的函数。

**具体例子：**
- 攻击成功率 ASR → eval/metrics.py
- 干净样本准确率 → eval/metrics.py
- 防御成功率 → eval/metrics.py
- 推理延迟测试 → eval/metrics.py
- 画对比图的脚本 → eval/visualize.py

**规则：** 共用的，改了要通知所有人。加新指标可以，别删旧指标。

---
## 五、configs/ —— 实验配置，共用

**放什么：** YAML 配置文件，记录每次实验用的参数。

**具体例子：**
- 模型名、候选标签、补丁尺寸 → configs/baseline.yaml
- EOT 实验的旋转范围、亮度范围 → configs/eot_exp.yaml
- 防御实验的方法选择、阈值 → configs/defense_exp.yaml

**规则：** 每次新实验，复制 baseline.yaml 改参数另存。不要覆盖别人的配置。

---
## 六、data/ —— 图片数据，不入 Git

**放什么：** 测试用的图片。.gitignore 已忽略这个目录的内容。

**子目录：**
- data/clean/ → 原始干净图片（stop sign 等）
- data/patched/ → 加了补丁后的图片（跑 attacks/ 生成）
- data/defended/ → 防御处理后的图片（跑 defense/ 生成）

**规则：** 图片不传 Git。组员C 负责采集和整理。

---
## 七、experiments/ —— 实验日志

**放什么：** 每次实验的记录文件。每次跑完实验新建一个。

**命名规则：** YYYY-MM-DD_简短描述.md

**文件内容模板：**
- 日期、执行人、用的哪个 commit
- 实验参数（模型、补丁、图片数量）
- 结果表格（ASR、准确率、延迟）
- 备注（发现的问题、下一步计划）

**规则：** 把实验结果写在这里，不要堆到 README 里。

---
## 八、根目录文件

| 文件 | 作用 | 什么时候改 |
|------|------|-----------|
| README.md | 项目说明书：怎么跑、谁干什么 | 加了新功能/变了流程时更新 |
| USAGE.md | 本文件：目录使用规则 | 规则变了时更新 |
| requirements.txt | Python 依赖列表 | 装了新包时加一行 |
| setup.bat | 环境启动脚本 | 环境配置变了时更新 |
| .gitignore | 不上传的文件列表 | 几乎不改 |

---
## 九、常见场景速查

**场景1：我加载了一个新模型**
→ 在 models/ 里写加载代码 → 更新 models/__init__.py → git add models/ → commit → push

**场景2：我复现了一个新攻击方法**
→ 在 attacks/ 里新建文件（如 attacks/pgd_attack.py） → 更新 attacks/__init__.py → git add attacks/ → commit → push

**场景3：我跑了一次实验**
→ 在 experiments/ 新建 2026-06-01_xxx.md 记录结果 → git add experiments/ → commit → push

**场景4：我装了一个新包**
→ pip install xxx → 把包名加到 requirements.txt → git add requirements.txt → commit → push

**场景5：我改了接口（会影响别人）**
→ 改代码 → 更新 README.md 说明 → 群里通知 → commit → push

**场景6：组员B 写了防御代码**
→ 在 defense/ 里写 detector.py / repair.py → 更新 defense/__init__.py → git add defense/ → commit → push

**场景7：我想加测试图片**
→ 放到 data/clean/ → 不进 Git，本地用 → 如果需要别人也用，用网盘/群文件传

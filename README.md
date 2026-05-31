# 面向视觉语言模型的物理域对抗补丁鲁棒性增强方法研究

大创项目 · 成都信息工程大学 网安学院


## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/wgoodzperfectx/VLM.git
cd VLM

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境（模型缓存到 D 盘）
setup.bat

# 4. 验证基线
python models/test_clip.py
```

## 项目结构

```
VLM/
├── models/           # 组员A：VLM 基线 + 推理接口
│   ├── vlm_baseline.py   ← 核心接口，组员B只调这个
│   ├── test_clip.py      ← 验证脚本
│   └── __init__.py
├── attacks/          # 对抗补丁生成
│   ├── digital_patch.py
│   └── __init__.py
├── defense/          # 组员B：防御代码
│   └── __init__.py        ← 待填充
├── eval/             # 共用：评估指标
│   ├── metrics.py
│   └── __init__.py
├── configs/          # 实验配置
│   └── baseline.yaml
├── data/             # 测试图片（不传 Git）
├── experiments/      # 实验记录
├── requirements.txt
├── setup.bat
├── .gitignore
└── README.md
```

## 接口约定（组员A ↔ 组员B）

组员 B 只需要知道一个函数：

```python
from models.vlm_baseline import classify

result = classify("image.jpg", candidate_labels=["a stop sign", ...])
# result = {"top1_label": ..., "top1_score": ..., "top5": ..., "embedding": ...}
```

B 在 `defense/` 里写防御函数，签名约定：

```python
def defend(image: np.ndarray) -> np.ndarray:
    """输入：(H,W,3) uint8 → 输出：(H,W,3) uint8"""
    ...
```

评估时串联：

```python
from models.vlm_baseline import classify
from defense.xxx import defend
from eval.metrics import compute_defense_metrics

clean_pred = classify(clean_img)["top1_label"]
adv_pred = classify(adv_img)["top1_label"]
defended_img = defend(adv_img)
defended_pred = classify(defended_img)["top1_label"]

metrics = compute_defense_metrics(
    [clean_pred], [adv_pred], [defended_pred], ["stop sign"]
)
```

## 基线数据（2026-05-31）

| 项目 | 数值 |
|------|------|
| 模型 | CLIP ViT-B/32 (151M) |
| 推理速度 | 53ms (18.8 FPS) CPU |
| 缓存位置 | D:\40_Coursework\hf_cache |

## 组员分工

- **组员A（王紫璇）**：VLM 基线、对抗攻击、实验主线
- **组员B**：防御算法、边缘部署
- **组员C**：物理实验、数据采集
- **组员D**：文档、答辩、展示

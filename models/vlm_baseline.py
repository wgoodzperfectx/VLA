# models/vlm_baseline.py
# 组员A（王紫璇）维护 —— VLM 基线模型统一接口
# 组员B 只调这个文件里的函数，不碰模型内部

import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from pathlib import Path
from typing import Union, List, Optional

_MODEL_ID = "openai/clip-vit-base-patch32"
_device = "cuda" if torch.cuda.is_available() else "cpu"

# 懒加载：第一次调用时才加载模型
_model = None
_processor = None

def _get_model():
    global _model, _processor
    if _model is None:
        _model = CLIPModel.from_pretrained(_MODEL_ID).to(_device).eval()
        _processor = CLIPProcessor.from_pretrained(_MODEL_ID)
    return _model, _processor

def classify(
    image: Union[str, Path, Image.Image, np.ndarray],
    candidate_labels: Optional[List[str]] = None,
) -> dict:
    """
    VLM 基线推理接口 —— 组员B唯一需要调用的函数。

    参数:
        image: 图片路径 / PIL.Image / numpy array
        candidate_labels: 候选类别列表，默认使用 ImageNet-1k 标签

    返回:
        {
            "top1_label": str,       # 最匹配的类别
            "top1_score": float,     # 置信度 (0~1)
            "top5": [(label, score), ...],
            "embedding": List[float], # 图像特征向量 (512维)
        }
    """
    model, processor = _get_model()

    # 统一转 PIL.Image
    if isinstance(image, (str, Path)):
        img = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        img = Image.fromarray(image.astype("uint8")).convert("RGB")
    else:
        img = image.convert("RGB")

    if candidate_labels is None:
        candidate_labels = [
            "a stop sign", "a speed limit sign", "a yield sign",
            "a traffic light", "a person", "a car", "a bicycle",
            "a dog", "a cat", "a blank sign",
        ]

    inputs = processor(
        text=candidate_labels, images=img,
        return_tensors="pt", padding=True
    )
    inputs = {k: v.to(_device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits_per_image[0]  # (N_labels,)
        probs = logits.softmax(dim=0)
        embedding = outputs.image_embeds[0].tolist()  # (512,)

    sorted_indices = probs.argsort(descending=True)
    top1_idx = sorted_indices[0].item()
    top5 = [(candidate_labels[i], probs[i].item()) for i in sorted_indices[:5].tolist()]

    return {
        "top1_label": candidate_labels[top1_idx],
        "top1_score": probs[top1_idx].item(),
        "top5": top5,
        "embedding": embedding,
    }

def get_device() -> str:
    """返回当前运行设备"""
    return _device

def get_model_info() -> dict:
    """返回模型基本信息"""
    model, _ = _get_model()
    params = sum(p.numel() for p in model.parameters())
    return {
        "model_id": _MODEL_ID,
        "device": _device,
        "parameters": f"{params/1e6:.1f}M",
    }

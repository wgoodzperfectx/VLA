# attacks/digital_patch.py
# 组员A（王紫璇）维护 —— 数字域对抗补丁生成

import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional

def generate_random_patch(
    size: Tuple[int, int] = (64, 64),
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    生成随机对抗补丁（Baseline 版本）。
    后续可替换为 AdvPatch / PGD 等方法。

    参数:
        size: 补丁尺寸 (H, W)
        seed: 随机种子（可复现）

    返回:
        numpy array (H, W, 3), dtype=uint8, 值域 [0, 255]
    """
    if seed is not None:
        np.random.seed(seed)
    patch = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
    return patch

def apply_patch_to_image(
    image: np.ndarray,
    patch: np.ndarray,
    position: Tuple[int, int] = (0, 0),
) -> np.ndarray:
    """
    将对抗补丁粘贴到图片上。

    参数:
        image: 原图 (H, W, 3), uint8
        patch: 补丁 (pH, pW, 3), uint8
        position: 粘贴左上角坐标 (x, y)

    返回:
        粘贴后的图片 (H, W, 3), uint8
    """
    result = image.copy()
    x, y = position
    pH, pW = patch.shape[:2]
    H, W = image.shape[:2]

    # 裁剪超出边界的部分
    paste_h = min(pH, H - y)
    paste_w = min(pW, W - x)
    if paste_h <= 0 or paste_w <= 0:
        return result

    result[y:y + paste_h, x:x + paste_w] = patch[:paste_h, :paste_w]
    return result

def generate_patched_samples(
    image_paths: list,
    patch_size: Tuple[int, int] = (64, 64),
    num_patches: int = 5,
    output_dir: str = "data/patched",
) -> list:
    """
    批量生成对抗样本图片。

    参数:
        image_paths: 原始图片路径列表
        patch_size: 补丁尺寸
        num_patches: 每张图生成几个补丁变体
        output_dir: 输出目录

    返回:
        生成的图片路径列表
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    generated = []

    for img_path in image_paths:
        img_path = Path(img_path)
        image = np.array(Image.open(img_path).convert("RGB"))
        H, W = image.shape[:2]

        for i in range(num_patches):
            patch = generate_random_patch(patch_size, seed=i)
            # 随机位置
            x = np.random.randint(0, max(1, W - patch_size[1]))
            y = np.random.randint(0, max(1, H - patch_size[0]))
            patched = apply_patch_to_image(image, patch, (x, y))

            out_name = f"{img_path.stem}_patch{i}_{patch_size[0]}x{patch_size[1]}.png"
            out_path = output / out_name
            Image.fromarray(patched).save(out_path)
            generated.append(str(out_path))

    return generated

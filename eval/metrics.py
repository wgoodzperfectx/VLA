# eval/metrics.py
# 组员A+B 共用 —— 统一的评估指标计算

import numpy as np
from typing import List

def compute_asr(
    clean_preds: List[str],
    adv_preds: List[str],
    ground_truth: List[str],
) -> dict:
    """
    计算攻击成功率 (Attack Success Rate)。

    攻击成功 = 干净样本分类正确 且 对抗样本分类错误/误导向目标类。

    返回:
        {"asr": float, "total": int, "success": int}
    """
    success = 0
    for clean, adv, gt in zip(clean_preds, adv_preds, ground_truth):
        if clean == gt and adv != gt:
            success += 1
    return {
        "asr": success / len(ground_truth) if ground_truth else 0.0,
        "total": len(ground_truth),
        "success": success,
    }

def compute_defense_metrics(
    clean_preds: List[str],
    adv_preds: List[str],
    defended_preds: List[str],
    ground_truth: List[str],
) -> dict:
    """
    计算防御效果三指标。

    返回:
        {
            "clean_accuracy": float,     # 干净样本准确率（越高越好）
            "robust_accuracy": float,    # 防御后准确率（越高越好）
            "defense_success_rate": float,  # 防御成功率（越高越好）
        }
    """
    n = len(ground_truth)
    if n == 0:
        return {"clean_accuracy": 0.0, "robust_accuracy": 0.0, "defense_success_rate": 0.0}

    clean_acc = sum(1 for p, g in zip(clean_preds, ground_truth) if p == g) / n
    robust_acc = sum(1 for p, g in zip(defended_preds, ground_truth) if p == g) / n

    # 防御成功 = 对抗样本被攻击成功 且 防御后恢复正确
    defended_success = sum(
        1 for c, a, d, g in zip(clean_preds, adv_preds, defended_preds, ground_truth)
        if c == g and a != g and d == g
    )
    dsr = defended_success / max(1, sum(1 for c, a, g in zip(clean_preds, adv_preds, ground_truth) if c == g and a != g))

    return {
        "clean_accuracy": round(clean_acc, 4),
        "robust_accuracy": round(robust_acc, 4),
        "defense_success_rate": round(dsr, 4),
    }

def benchmark_latency(
    inference_fn,
    inputs: list,
    warmup: int = 5,
    repeats: int = 50,
) -> dict:
    """
    测量推理延迟。

    返回:
        {"mean_ms": float, "std_ms": float, "fps": float}
    """
    import time
    # warmup
    for _ in range(warmup):
        inference_fn(inputs[0])
    times = []
    for inp in inputs * ((repeats // len(inputs)) + 1):
        if len(times) >= repeats:
            break
        start = time.perf_counter()
        inference_fn(inp)
        times.append((time.perf_counter() - start) * 1000)
    mean_ms = np.mean(times)
    return {
        "mean_ms": round(mean_ms, 1),
        "std_ms": round(np.std(times), 1),
        "fps": round(1000 / mean_ms, 1),
    }

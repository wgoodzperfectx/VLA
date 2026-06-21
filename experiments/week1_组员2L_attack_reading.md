# 攻击代码阅读笔记

## 一、三个主要函数

### 1. `generate_random_patch` - 生成随机补丁

| 参数 | 说明 |
|------|------|
| `size` | 决定补丁的长宽（默认 64×64 像素） |
| `seed` | 随机种子，保证每次生成的随机方块一致（方便实验复现） |

---

### 2. `apply_patch_to_image` - 贴补丁

**参数：**
- `image` - 原图
- `patch` - 补丁
- `position` - 贴片左上角的坐标 $(x, y)$

**核心逻辑：**

1. **复制原图**：使用 `.copy()` 复制一份原图，避免直接修改原文件

2. **边界防御**：
   ```python
   paste_h = min(pH, H - y)
   ```
   防止坐标太靠右或靠下导致补丁超出原图边界。如果超出，会自动裁剪补丁，只贴能放下的部分

3. **矩阵切片覆盖**：利用 NumPy 的切片语法直接替换像素值
   ```python
   result[y:..., x:...] = patch[...]
   ```

---

### 3. `generate_patched_samples` - 批量处理并保存

主控制函数，串联前两个函数进行批量生产。

**工作流程（双重循环）：**

- **外层循环**：遍历每一张输入图片，用 `PIL.Image` 打开并转换成 RGB 矩阵

- **内层循环**：针对当前图片，循环执行 `num_patches` 次（默认 5 次）：
  1. 随机生成一个补丁
  2. 随机计算坐标：
     ```python
     np.random.randint(0, max(1, W - patch_size[1]))
     ```
     保证生成的坐标 $(x, y)$ 无论怎么随机，补丁都能完整落在图片内部
  3. 调用 `apply_patch_to_image` 把补丁贴上去
  4. 自动生成新文件名（例如 `原图名_patch0_64x64.png`），保存到 `data/patched` 文件夹

---

## 二、关键词

- `size`
- `seed`
- `position`

---

## 三、问题与改进建议

### 问题 1：随机种子全局生效

在 Python 中，`np.random.seed()` 是全局生效的。这意味着每次生成的补丁**内容**一样，但**位置**也变成一样的了。

**建议修改**：让每次实验的补丁内容一样，但位置不同

**修改后的代码：**

```python
def generate_random_patch(
    size: Tuple[int, int] = (64, 64),
    seed: Optional[int] = None,
) -> np.ndarray:
    # 创建一个独立的随机生成器，不影响外部其他的 np.random 函数
    rng = np.random.default_rng(seed)
    patch = rng.integers(0, 256, (*size, 3), dtype=np.uint8)
    return patch
```

---

### 问题 2：性能考虑

如果后面改成 AdvPatch，第三个函数里的 `for` 循环会不会太慢？

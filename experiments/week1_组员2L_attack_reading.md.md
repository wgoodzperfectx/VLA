一、3个主要函数
    1、generate_random_patch 负责生成随机补丁：
        `size` 决定补丁的长宽（默认 64x64 像素）；`seed` 是随机种子，用来保证每次生成的随机方块是一模一样的（方便实验复现）
    2、apply_patch_to_image 负责贴补丁：
        a、参数：`image`（原图）、`patch`（补丁）、`position`（贴片左上角的坐标 $x, y$）
        b、核心逻辑：
            1、它先用 `.copy()` 复制一份原图，避免直接修改原文件。
            2、边界防御：计算 `paste_h = min(pH, H - y)`。这是为了防止你指定的坐标太靠右或靠下，导致补丁超出了原图的边界。如果超出了，它会自动把补丁裁剪变小，只贴能放下的部分
            3、 矩阵切片覆盖：利用 NumPy 的切片语法 `result[y:..., x:...] = patch[...]`，直接把原图对应区域的像素值替换为补丁的像素值
    3、generate_patched_samples 负责批量处理并保存：
        这是一个主控制函数，负责把前两个函数串联起来，进行批量生产
        **工作流程**（双重循环）：
            外层循环：遍历每一张输入的图片，用 `PIL.Image` 打开并转换成 RGB 矩阵。
            内层循环：针对当前图片，循环执行 `num_patches` 次（默认 5 次）：
                a、随机生成一个补丁
                b、随机计算坐标：`np.random.randint(0, max(1, W - patch_size[1]))` 这行代码保证了生成的坐标 $(x, y)$ 无论怎么随机，补丁都刚好能完整落在图片内部，不会飞到外面去
                c、调用 `apply_patch_to_image` 把补丁贴上去。
                d、自动生成一个新的文件名（例如 `原图名_patch0_64x64.png`），并保存到 `data/patched` 文件夹里

二、关键词
    size、seed、position

三、问题
    1、在Python中np.random.seed()是全局生效的。就是说 每次生成的补丁内容是一样，但补丁      位置也变成一样的了。那要不要把这个改一下，让每次实验的补丁内容一样，位置不一样
        把第一个函数改成:
```
def generate_random_patch(
    size: Tuple[int, int] = (64, 64),
    seed: Optional[int] = None,
) -> np.ndarray:
    # 创建一个独立的随机生成器，它不会影响外面其他的 np.random 函数
    rng = np.random.default_rng(seed)
    patch = rng.integers(0, 256, (*size, 3), dtype=np.uint8)
    return patch
```
2、如果后面改成AdvPatch，那第3个函数里的for循环会太慢？
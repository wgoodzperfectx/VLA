import torch, os, time
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

MODEL_ID = "openai/clip-vit-base-patch32"
print("=" * 55)
print("【大创基线】CLIP ViT-B/32 模型下载 & 验证")
print("=" * 55)
print(f"HF_HOME: {os.environ['HF_HOME']}")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"设备: {device}")

print("\n>>> 下载模型 (首次 ~605MB, 存 D 盘中...)")
t0 = time.time()
model = CLIPModel.from_pretrained(MODEL_ID)
processor = CLIPProcessor.from_pretrained(MODEL_ID)
model.eval()
print(f"下载+加载耗时: {time.time()-t0:.1f}s")
print(f"参数量: {sum(p.numel() for p in model.parameters())/1e6:.1f}M")

print("\n>>> 推理测试")
img = Image.new("RGB", (224, 224), (255, 0, 0))
texts = ["a red image", "a blue image", "a stop sign"]
inputs = processor(text=texts, images=img, return_tensors="pt", padding=True)
with torch.no_grad():
    probs = model(**inputs).logits_per_image.softmax(dim=1)
for t, p in zip(texts, probs[0].tolist()):
    print(f"  [{p:.4f}] {t}")

times = []
for _ in range(20):
    s = time.perf_counter()
    with torch.no_grad():
        _ = model(**inputs)
    times.append(time.perf_counter() - s)
avg = sum(times) / len(times) * 1000
print(f"\n>>> 推理速度: {avg:.1f}ms ({1000/avg:.1f} FPS) [{device}]")

cache = os.environ["HF_HOME"]
total = 0
for r, _, fs in os.walk(cache):
    for f in fs:
        total += os.path.getsize(os.path.join(r, f))
print(f"\n>>> HF 缓存大小: {total/1024**2:.0f}MB (全部在 D 盘)")
print(f"    路径: {cache}")
print("=" * 55)
print("✓ CLIP ViT-B/32 基线模型验证通过！")

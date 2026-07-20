"""OpenVLA baseline adapter for image + instruction -> robot action inference.

The heavyweight checkpoint is loaded lazily. Importing this module and running
the interface smoke test therefore do not download model weights.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np
import torch
from PIL import Image

ImageInput = Union[str, Path, Image.Image, np.ndarray]


def build_openvla_prompt(instruction: str) -> str:
    """Build the prompt format used by the official OpenVLA example."""
    instruction = instruction.strip()
    if not instruction:
        raise ValueError("instruction must not be empty")
    return f"In: What action should the robot take to {instruction}?\nOut:"


def to_pil_image(image: ImageInput) -> Image.Image:
    """Normalize supported observation formats to an RGB PIL image."""
    if isinstance(image, (str, Path)):
        return Image.open(image).convert("RGB")
    if isinstance(image, np.ndarray):
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("numpy image must have shape (H, W, 3)")
        return Image.fromarray(image.astype(np.uint8)).convert("RGB")
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    raise TypeError(f"unsupported image type: {type(image)!r}")


def validate_action(action: Sequence[float], expected_dim: Optional[int] = 7) -> np.ndarray:
    """Return a finite 1-D action vector and fail early on malformed output."""
    result = np.asarray(action, dtype=np.float32)
    if result.ndim != 1:
        raise ValueError("action must be a one-dimensional vector")
    if expected_dim is not None and result.size != expected_dim:
        raise ValueError(f"expected {expected_dim} action values, got {result.size}")
    if not np.isfinite(result).all():
        raise ValueError("action contains NaN or infinity")
    return result


@dataclass(frozen=True)
class OpenVLAConfig:
    model_id: str = "openvla/openvla-7b"
    device: str = "cuda:0"
    dtype: str = "bfloat16"
    unnorm_key: str = "bridge_orig"
    action_dim: int = 7


class OpenVLABaseline:
    """Lazy Hugging Face adapter around ``predict_action`` from OpenVLA."""

    def __init__(self, config: Optional[OpenVLAConfig] = None) -> None:
        self.config = config or OpenVLAConfig()
        self._model = None
        self._processor = None

    @property
    def torch_dtype(self) -> torch.dtype:
        try:
            return getattr(torch, self.config.dtype)
        except AttributeError as exc:
            raise ValueError(f"unsupported torch dtype: {self.config.dtype}") from exc

    def load(self) -> None:
        """Load the processor and checkpoint on first real inference."""
        if self._model is not None:
            return
        if self.config.device.startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError(
                "OpenVLA inference is configured for CUDA, but CUDA is unavailable. "
                "Use a suitable GPU environment or change the configuration deliberately."
            )

        from transformers import AutoModelForVision2Seq, AutoProcessor

        self._processor = AutoProcessor.from_pretrained(
            self.config.model_id, trust_remote_code=True
        )
        self._model = AutoModelForVision2Seq.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        ).to(self.config.device).eval()

    def predict_action(self, image: ImageInput, instruction: str) -> np.ndarray:
        """Predict one normalized 7-DoF action from an observation and instruction."""
        self.load()
        prompt = build_openvla_prompt(instruction)
        inputs = self._processor(prompt, to_pil_image(image))
        inputs = inputs.to(self.config.device, dtype=self.torch_dtype)

        with torch.inference_mode():
            action = self._model.predict_action(
                **inputs,
                unnorm_key=self.config.unnorm_key,
                do_sample=False,
            )
        return validate_action(action, self.config.action_dim)

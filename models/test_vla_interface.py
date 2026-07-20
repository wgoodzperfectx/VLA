"""Offline smoke test for the VLA baseline contract (no checkpoint download)."""

import numpy as np
from PIL import Image

try:
    from models.vla_baseline import build_openvla_prompt, to_pil_image, validate_action
except ModuleNotFoundError:  # Allow: python models/test_vla_interface.py
    from vla_baseline import build_openvla_prompt, to_pil_image, validate_action


def main() -> None:
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    assert isinstance(to_pil_image(image), Image.Image)
    assert build_openvla_prompt("pick up the red cup").endswith("\nOut:")
    action = validate_action([0.0, 0.1, 0.0, -0.1, 0.0, 0.0, 1.0])
    assert action.shape == (7,)
    print("VLA interface smoke test passed (no model weights loaded).")


if __name__ == "__main__":
    main()

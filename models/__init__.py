# Current VLA interface. Legacy CLIP helpers remain available explicitly from
# models.vlm_baseline without being imported (and initialized) here.
from .vla_baseline import OpenVLABaseline, OpenVLAConfig

__all__ = ["OpenVLABaseline", "OpenVLAConfig"]

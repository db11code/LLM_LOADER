"""
Sub-package: discovery helpers.
"""
from .cache_path import get_hf_cache_path
from .index_builder import scan_cache, build_index   # ← add build_index

__all__: list[str] = ["get_hf_cache_path", "scan_cache", "build_index"] 
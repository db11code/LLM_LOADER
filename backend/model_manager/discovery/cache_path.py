"""
Return or create the folder that stores downloaded / converted models.
Implementation will be added in Milestone 2.
"""
from pathlib import Path
import os

def get_hf_cache_path() -> Path:
    """
    Determine the local Hugging Face cache directory.

    Order of precedence:
      1. $HUGGINGFACE_HUB_CACHE (use as-is)
      2. $HF_HOME/huggingface/hub
      3. <user-home>/.cache/huggingface/hub

    Returns
    -------
    Path
        Absolute, expanded path to the cache directory.
    """
    # 1️⃣ env var override
    env_cache = os.environ.get("HUGGINGFACE_HUB_CACHE")
    if env_cache:
        return Path(env_cache).expanduser().resolve()

    # 2️⃣ HF_HOME root
    env_home = os.environ.get("HF_HOME")
    if env_home:
        return Path(env_home).expanduser().resolve() / "huggingface" / "hub"

    # 3️⃣ default fallback
    return Path.home() / ".cache" / "huggingface" / "hub"


def get_cache_dir() -> Path:
    """Placeholder – returns ~/.cache/llm_loader for now."""
    return Path.home() / ".cache" / "llm_loader" 
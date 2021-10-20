from pathlib import Path


def get_path(path: str) -> Path:
    p = Path(__file__).parents[1]
    return p / path
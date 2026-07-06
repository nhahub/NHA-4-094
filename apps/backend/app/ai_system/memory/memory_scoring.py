import numpy as np
from datetime import datetime
from app.ai_system.memory import memory_config

def cosine_similarity(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    arr_a = np.array(a, dtype=np.float32)
    arr_b = np.array(b, dtype=np.float32)
    norm_a = np.linalg.norm(arr_a)
    norm_b = np.linalg.norm(arr_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(arr_a, arr_b) / (norm_a * norm_b))

def recency_score(created_at: datetime) -> float:
    """Exponential decay: score=1.0 now, ~0.59 at 7 days, ~0.25 at 30 days."""
    days = (datetime.utcnow() - created_at).total_seconds() / 86400.0
    return 1.0 / (1.0 + memory_config.RECENCY_DECAY_RATE * days)

def ranking_score(similarity: float, created_at: datetime, importance: float) -> float:
    return (
        memory_config.WEIGHT_SIMILARITY * similarity +
        memory_config.WEIGHT_RECENCY * recency_score(created_at) +
        memory_config.WEIGHT_IMPORTANCE * importance
    )

from dataclasses import dataclass
from typing import Optional


@dataclass
class Signal:
    timestamp: str
    signal: str
    confidence: float
    reasoning: str
    model: Optional[str] = None
    interval: Optional[str] = None


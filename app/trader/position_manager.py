from __future__ import annotations
from typing import Optional
from app.models import Position

class PositionManager:
    def __init__(self):
        self.active: Optional[Position] = None

    def open(self, position: Position) -> None:
        self.active = position

    def close(self) -> None:
        self.active = None

    def is_open(self) -> bool:
        return self.active is not None

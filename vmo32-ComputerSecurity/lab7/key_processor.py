from __future__ import annotations

import hashlib
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List


@dataclass
class KeyProcessor:
    grid_size: int = 3
    min_points: int = 4

    @property
    def total_nodes(self) -> int:
        return self.grid_size * self.grid_size

    def node_to_rc(self, node: int) -> tuple[int, int]:
        return divmod(node, self.grid_size)

    def rc_to_node(self, row: int, col: int) -> int:
        return row * self.grid_size + col

    def intermediate_node(self, from_node: int, to_node: int) -> int | None:
        """Return middle node when jump crosses exactly one untouched node."""
        r1, c1 = self.node_to_rc(from_node)
        r2, c2 = self.node_to_rc(to_node)

        dr = r2 - r1
        dc = c2 - c1

        if dr == 0 and abs(dc) == 2:
            return self.rc_to_node(r1, (c1 + c2) // 2)
        if dc == 0 and abs(dr) == 2:
            return self.rc_to_node((r1 + r2) // 2, c1)
        if abs(dr) == 2 and abs(dc) == 2:
            return self.rc_to_node((r1 + r2) // 2, (c1 + c2) // 2)
        return None

    def expanded_transition(self, from_node: int, to_node: int, visited: set[int]) -> list[int]:
        """Transition with Android-like midpoint insertion."""
        if to_node in visited:
            return []

        result: list[int] = []
        mid = self.intermediate_node(from_node, to_node)
        if mid is not None and mid not in visited:
            result.append(mid)

        result.append(to_node)
        return result

    def enough_points(self, pattern: Iterable[int]) -> bool:
        return len(list(pattern)) >= self.min_points

    def serialize_pattern(self, pattern: Iterable[int]) -> str:
        return "-".join(str(i) for i in pattern)

    def fingerprint(self, pattern: Iterable[int]) -> str:
        serialized = self.serialize_pattern(pattern)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def similarity(self, pattern_a: List[int], pattern_b: List[int]) -> float:
        """Order-sensitive similarity for two node sequences."""
        if not pattern_a and not pattern_b:
            return 1.0
        if not pattern_a or not pattern_b:
            return 0.0
        return SequenceMatcher(a=pattern_a, b=pattern_b).ratio()

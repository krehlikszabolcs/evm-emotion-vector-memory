from dataclasses import dataclass
from typing import List, Tuple

Vector5 = List[float]

@dataclass
class FEV:
    L: Vector5
    U: Vector5

    @property
    def center(self) -> Vector5:
        return [(l + u) / 2.0 for l, u in zip(self.L, self.U)]

def clamp(v: Vector5, L: Vector5, U: Vector5) -> Vector5:
    return [max(l, min(x, u)) for x, l, u in zip(v, L, U)]

def update_identity(prev: Vector5, endpoint: Vector5, beta: float) -> Vector5:
    return [beta * x + (1.0 - beta) * p for x, p in zip(endpoint, prev)]

def boundary_recovery(eev: Vector5, fev: FEV, alpha: float = 0.5, N_persist: int = 6,
                      persist_counter: List[int] = None) -> Tuple[Vector5, List[int]]:
    if persist_counter is None:
        persist_counter = [0,0,0,0,0]

    center = fev.center
    # Default threshold: T_A = 0.8 * (U-L)/2
    thresholds = [0.8 * (u - l) / 2.0 for l, u in zip(fev.L, fev.U)]

    for i in range(5):
        if abs(eev[i] - center[i]) >= thresholds[i]:
            persist_counter[i] += 1
        else:
            persist_counter[i] = 0

        if persist_counter[i] >= N_persist:
            eev[i] = alpha * eev[i] + (1.0 - alpha) * center[i]
            persist_counter[i] = 0

    return eev, persist_counter

"""Small portable PRNG (mulberry32) and normal draws (Box-Muller).

Chosen so the website's JavaScript port reproduces the Python results exactly for
the same seed: both use 32-bit unsigned integer arithmetic and the same order of
draws. numpy's generators are not used inside the simulator for that reason.
"""
from __future__ import annotations

import math

import numpy as np

M32 = 0xFFFFFFFF


class Mulberry32:
    def __init__(self, seed: int):
        self.state = seed & M32

    def next_u32(self) -> int:
        self.state = (self.state + 0x6D2B79F5) & M32
        t = self.state
        t = ((t ^ (t >> 15)) * (t | 1)) & M32
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & M32)) & M32
        return (t ^ (t >> 14)) & M32

    def uniform(self) -> float:
        """In (0, 1): never exactly 0, so log() is safe."""
        return (self.next_u32() + 0.5) / 4294967296.0

    def normal(self) -> float:
        u1, u2 = self.uniform(), self.uniform()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    def normals(self, n: int) -> np.ndarray:
        return np.array([self.normal() for _ in range(n)])

    def uniforms(self, n: int) -> np.ndarray:
        return np.array([self.uniform() for _ in range(n)])

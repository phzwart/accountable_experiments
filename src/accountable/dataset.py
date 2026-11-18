"""
A dataset is a design on which a campaign runs, plus an oracle.

Retrospective experiments hold the truth at every design site, so the
oracle returns stored spectra and remainder labels can be scored. A live
campaign supplies an oracle that measures; remainder labels are then
unavailable and only the guarantee speaks for the skips.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .sibson import ImageMap


class Oracle:
    retrospective = False

    def measure(self, idx: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def truth(self, idx: np.ndarray) -> Optional[np.ndarray]:
        """Truth at unmeasured sites, retrospective only."""
        return None


class StoredOracle(Oracle):
    retrospective = True

    def __init__(self, spectra: np.ndarray):
        self.spectra = np.asarray(spectra, float)

    def measure(self, idx):
        return self.spectra[np.asarray(idx, int)]

    def truth(self, idx):
        return self.spectra[np.asarray(idx, int)]


@dataclass
class Dataset:
    """
    ``points`` are design positions in the unit square (geometry for the
    interpolant). ``levels`` are the hierarchical levels. ``candidate``
    optionally restricts which sites take part (e.g. a composition
    triangle). ``images`` adds mirror images to the interpolation cloud.
    """

    name: str
    points: np.ndarray
    levels: np.ndarray
    oracle: Oracle
    axis: np.ndarray
    axis_unit: str = ""
    candidate: Optional[np.ndarray] = None
    images: Optional[ImageMap] = None
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.points = np.asarray(self.points, float)
        self.levels = np.asarray(self.levels, int)
        if self.candidate is None:
            self.candidate = np.ones(len(self.points), bool)

    @property
    def n(self) -> int:
        return len(self.points)

    def level_counts(self) -> dict:
        lv = self.levels[self.candidate]
        return {int(L): int((lv == L).sum()) for L in range(int(lv.max()) + 1)}

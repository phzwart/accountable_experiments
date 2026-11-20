"""
Natural-neighbour (Sibson) weights on a measured point set.

The weights depend only on site positions. One weight set serves both
prediction routes: interpolating spectra (then extracting a target) and
interpolating a scalar target directly.

Numerics follow the original ``saxs_phase_space`` implementation line for
line, so decisions reproduce. The Delaunay triangulation and the Voronoi
cells of the measured set are built once per measured set instead of once
per query; both are deterministic functions of the measured set, so the
weights are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from collections import OrderedDict

import numpy as np
from scipy.spatial import Delaunay, Voronoi, cKDTree

# An image map takes measured points (n, 2) and returns the stacked mirror
# images (n_img * n, 2), in preimage order within each block.
ImageMap = Callable[[np.ndarray], np.ndarray]


def _poly_area(poly: np.ndarray) -> float:
    if poly is None or len(poly) < 3:
        return 0.0
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def _sutherland_hodgman(subject: np.ndarray, clip: np.ndarray) -> np.ndarray:
    """Clip a polygon by a convex polygon."""
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-14

    def intersect(p, q, a, b):
        dp = q - p
        dc = b - a
        denom = dp[0] * dc[1] - dp[1] * dc[0]
        if abs(denom) < 1e-18:
            return p
        t = ((a[0] - p[0]) * dc[1] - (a[1] - p[1]) * dc[0]) / denom
        return p + t * dp

    output = np.asarray(subject, float)
    if len(output) == 0:
        return output
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp = output
        output = []
        if len(inp) == 0:
            break
        s = inp[-1]
        for e in inp:
            if inside(e, a, b):
                if not inside(s, a, b):
                    output.append(intersect(s, e, a, b))
                output.append(e)
            elif inside(s, a, b):
                output.append(intersect(s, e, a, b))
            s = e
        output = np.asarray(output, float) if len(output) else np.zeros((0, 2))
    return output


def _voronoi_region_polygons(points: np.ndarray, radius: float = 10.0):
    """Finite polygons for each Voronoi cell, indexed like ``points``."""
    vor = Voronoi(points)
    center = points.mean(axis=0)
    regions = []
    for i, reg_i in enumerate(vor.point_region):
        region_idx = vor.regions[reg_i]
        if not region_idx:
            regions.append(np.zeros((0, 2)))
            continue
        if -1 not in region_idx:
            regions.append(vor.vertices[region_idx])
            continue
        ridges = []
        for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
            if p1 != i and p2 != i:
                continue
            ridges.append((p1, p2, v1, v2))
        pts = []
        for p1, p2, v1, v2 in ridges:
            other = p2 if p1 == i else p1
            if v1 >= 0 and v2 >= 0:
                pts.extend([vor.vertices[v1], vor.vertices[v2]])
                continue
            v_finite = vor.vertices[v1 if v1 >= 0 else v2]
            t = points[other] - points[i]
            t /= np.linalg.norm(t) + 1e-15
            n = np.array([-t[1], t[0]])
            midpoint = 0.5 * (points[i] + points[other])
            if np.dot(midpoint - center, n) < 0:
                n = -n
            pts.append(v_finite)
            pts.append(v_finite + n * radius)
        if len(pts) < 3:
            regions.append(np.zeros((0, 2)))
        else:
            poly = np.asarray(pts, float)
            ang = np.arctan2(poly[:, 1] - points[i, 1], poly[:, 0] - points[i, 0])
            regions.append(poly[np.argsort(ang)])
    return regions


class _SibsonCloud:
    """Cached Delaunay and Voronoi cells of one point cloud."""

    def __init__(self, P: np.ndarray, radius: float):
        self.P = np.asarray(P, float)
        self.radius = float(radius)
        self.n = len(self.P)
        self._tri = None
        self._regions = None
        self._regions_failed = False

    @property
    def tri(self):
        if self._tri is None:
            self._tri = Delaunay(self.P)
        return self._tri

    def regions(self):
        if self._regions is None and not self._regions_failed:
            try:
                self._regions = _voronoi_region_polygons(self.P, radius=self.radius)
            except Exception:
                self._regions_failed = True
        return self._regions

    def weights(self, q: np.ndarray):
        """Sibson weights at ``q``: (idx, w). Empty outside the hull."""
        P = self.P
        q = np.asarray(q, float).ravel()
        n = self.n
        if n == 0:
            return np.array([], dtype=int), np.array([])
        if n == 1:
            return np.array([0]), np.array([1.0])
        tri = self.tri
        s = int(tri.find_simplex(q))
        if s < 0:
            return np.array([], dtype=int), np.array([])
        d = np.linalg.norm(P - q, axis=1)
        j = int(np.argmin(d))
        if d[j] < 1e-14:
            return np.array([j]), np.array([1.0])

        def _barycentric_fallback():
            simp = tri.simplices[s]
            b = tri.transform[s, :2].dot(q - tri.transform[s, 2])
            w = np.r_[b, 1 - b.sum()]
            w = np.clip(w, 0, None)
            if w.sum() <= 0:
                w = np.ones(3) / 3.0
            else:
                w = w / w.sum()
            return np.asarray(simp, dtype=int), w

        vor0_regions = self.regions()
        if vor0_regions is None:
            return _barycentric_fallback()
        P_aug = np.vstack([P, q])
        try:
            vor1 = Voronoi(P_aug)
        except Exception:
            return _barycentric_fallback()

        q_id = n
        nbrs = []
        for (p1, p2) in vor1.ridge_points:
            if p1 == q_id and p2 < n:
                nbrs.append(p2)
            elif p2 == q_id and p1 < n:
                nbrs.append(p1)
        nbrs = sorted(set(nbrs))
        if not nbrs:
            return _barycentric_fallback()

        q_reg = vor1.regions[vor1.point_region[q_id]]
        if not q_reg or -1 in q_reg:
            verts = []
            for (p1, p2), (v1, v2) in zip(vor1.ridge_points, vor1.ridge_vertices):
                if q_id not in (p1, p2):
                    continue
                if v1 >= 0:
                    verts.append(vor1.vertices[v1])
                if v2 >= 0:
                    verts.append(vor1.vertices[v2])
            if len(verts) < 3:
                return _barycentric_fallback()
            Vq = np.asarray(verts, float)
            ang = np.arctan2(Vq[:, 1] - q[1], Vq[:, 0] - q[0])
            Vq = Vq[np.argsort(ang)]
        else:
            Vq = vor1.vertices[q_reg]

        areas = []
        keep = []
        for i in nbrs:
            Vi = vor0_regions[i]
            if len(Vi) < 3 or len(Vq) < 3:
                continue
            inter = _sutherland_hodgman(Vi, Vq)
            a = _poly_area(inter)
            if a > 1e-18:
                areas.append(a)
                keep.append(i)
        if not keep:
            return _barycentric_fallback()
        w = np.asarray(areas, float)
        w /= w.sum()
        return np.asarray(keep, dtype=int), w


@dataclass
class NeighbourWeights:
    """
    Weights of each query on the measured set.

    ``keys[i]`` indexes the measured set, ``raw[i]`` holds the summed Sibson
    areas before normalisation, and ``fallback[i]`` marks a query outside
    the (extended) hull, whose weights are inverse-distance kNN.
    """

    keys: list
    raw: list
    fallback: np.ndarray
    n_measured: int

    def apply(self, Y: np.ndarray) -> np.ndarray:
        """Interpolate rows of ``Y`` (spectra or scalars) at every query."""
        Y = np.asarray(Y, float)
        squeeze = Y.ndim == 1
        Y2 = Y[:, None] if squeeze else Y
        out = np.zeros((len(self.keys), Y2.shape[1]), float)
        fb_rows = np.flatnonzero(self.fallback)
        for i, (keys, raw) in enumerate(zip(self.keys, self.raw)):
            if self.fallback[i]:
                continue
            ww = np.array(raw, float)
            ww /= ww.sum()
            out[i] = (ww[:, None] * Y2[keys]).sum(axis=0)
        if len(fb_rows):
            # Same arithmetic as the original kNN fallback: one einsum.
            K = np.stack([self.keys[i] for i in fb_rows])
            W = np.stack([self.raw[i] for i in fb_rows])
            out[fb_rows] = np.einsum("nk,nkq->nq", W, Y2[K])
        return out[:, 0] if squeeze else out


def symmetry_cloud(P_meas: np.ndarray, images: Optional[ImageMap]):
    """Measured points plus de-duplicated images, with the preimage index."""
    P_meas = np.asarray(P_meas, float)
    n = len(P_meas)
    if images is None or n == 0:
        return P_meas, np.arange(n)
    mirrors = images(P_meas)
    n_img = len(mirrors) // n
    P_ext = np.vstack([P_meas, mirrors])
    src = np.concatenate([np.arange(n), np.tile(np.arange(n), n_img)])
    # Drop an image that coincides with an earlier kept point (first wins).
    # Coincident pairs are rare (sites on a mirror line), so a k-d tree
    # finds them; the scan below keeps the original first-wins order.
    keep = np.ones(len(P_ext), dtype=bool)
    earlier = {}
    for a, b in cKDTree(P_ext).query_pairs(1e-10):
        lo, hi = (a, b) if a < b else (b, a)
        if hi >= n and np.linalg.norm(P_ext[lo] - P_ext[hi]) < 1e-10:
            earlier.setdefault(hi, []).append(lo)
    for i in sorted(earlier):
        if any(keep[j] for j in earlier[i]):
            keep[i] = False
    return P_ext[keep], src[keep]


METHODS = ("legacy", "watson", "delaunay")

# A campaign asks for weights on the same measured set several times per
# level (scores, labels, interest score). Weights depend only on the
# positions, so the cloud and the per-query weights are cached for the
# few most recent measured sets. Results are identical to recomputation.
_CLOUD_CACHE: "OrderedDict[tuple, tuple]" = OrderedDict()
_CLOUD_CACHE_SIZE = 4


def _cloud_key(P_meas, images, method):
    P = np.ascontiguousarray(P_meas, dtype=float)
    return (P.shape, hash(P.tobytes()), id(images), method)


def _cloud_cache_get(P_meas, images, method):
    key = _cloud_key(P_meas, images, method)
    hit = _CLOUD_CACHE.get(key)
    if hit is not None:
        _CLOUD_CACHE.move_to_end(key)
        if np.array_equal(hit[0], P_meas):
            return hit[1]
    return None


def _cloud_cache_put(P_meas, images, method, entry):
    key = _cloud_key(P_meas, images, method)
    _CLOUD_CACHE[key] = (np.array(P_meas, float, copy=True), entry)
    _CLOUD_CACHE.move_to_end(key)
    while len(_CLOUD_CACHE) > _CLOUD_CACHE_SIZE:
        _CLOUD_CACHE.popitem(last=False)
    return entry


def neighbour_weights(
    P_meas: np.ndarray,
    P_query: np.ndarray,
    *,
    images: Optional[ImageMap] = None,
    k_fallback: int = 5,
    method: str = "legacy",
) -> NeighbourWeights:
    """
    Sibson weights of every query on the measured set.

    ``method="legacy"`` reproduces the original implementation, including
    its behaviour on near-cocircular sites. ``method="watson"`` computes
    natural-neighbour coordinates by half-plane clipping and is continuous
    in the site positions. ``method="delaunay"`` gives barycentric weights
    on the enclosing simplex of a Delaunay triangulation, in any dimension
    (piecewise-linear interpolation; used for designs with more than two
    coordinates). Queries outside the (extended) hull fall back
    to inverse-distance kNN in both.
    """
    if method not in METHODS:
        raise ValueError(f"unknown natural-neighbour method {method!r}")
    P_meas = np.asarray(P_meas, float)
    P_query = np.atleast_2d(np.asarray(P_query, float))
    if P_query.size == 0:
        return NeighbourWeights([], [], np.zeros(0, bool), len(P_meas))
    entry = _cloud_cache_get(P_meas, images, method)
    if entry is None:
        P_cloud, src = symmetry_cloud(P_meas, images)
        span = float(np.linalg.norm(P_cloud.max(0) - P_cloud.min(0))) + 1.0
        radius = max(5.0 * span, 5.0)
        if method == "legacy":
            cloud = _SibsonCloud(P_cloud, radius)
        elif method == "watson":
            cloud = _WatsonCloud(P_cloud)
        else:
            cloud = _DelaunayCloud(P_cloud)
        entry = _cloud_cache_put(P_meas, images, method, (cloud, src, {}))
    cloud, src, memo = entry
    keys_all, raw_all = [], []
    fallback = np.zeros(len(P_query), bool)
    for i, qpt in enumerate(P_query):
        qk = qpt.tobytes()
        if qk not in memo:
            memo[qk] = cloud.weights(qpt)
        idx, w = memo[qk]
        if len(idx) == 0:
            fallback[i] = True
            keys_all.append(None)
            raw_all.append(None)
            continue
        src_i = src[idx]
        acc = {}
        for j, s in enumerate(src_i):
            acc[int(s)] = acc.get(int(s), 0.0) + float(w[j])
        keys = np.array(sorted(acc.keys()), dtype=int)
        keys_all.append(keys)
        raw_all.append(np.array([acc[k] for k in keys], float))
    fb = np.flatnonzero(fallback)
    if len(fb):
        tree = cKDTree(P_meas)
        k_use = min(k_fallback, len(P_meas))
        d, idx = tree.query(P_query[fb], k=k_use)
        if np.ndim(d) == 1:
            d, idx = d[:, None], idx[:, None]
        w = 1.0 / np.maximum(d, 1e-12)
        w /= w.sum(axis=1, keepdims=True)
        for row, qi in enumerate(fb):
            keys_all[qi] = np.asarray(idx[row], dtype=int)
            raw_all[qi] = np.asarray(w[row], float)
    return NeighbourWeights(keys_all, raw_all, fallback, len(P_meas))


def interpolate(P_meas, Y_meas, P_query, *, images=None, k_fallback=5,
                method: str = "legacy") -> np.ndarray:
    """Convenience: weights then apply."""
    W = neighbour_weights(P_meas, P_query, images=images, k_fallback=k_fallback, method=method)
    return W.apply(Y_meas)


# ---------------------------------------------------------------------------
# Robust natural-neighbour (Sibson) coordinates.
#
# Natural neighbours of q are the vertices of Delaunay triangles whose
# circumcircle contains q. The Voronoi cell of q after insertion is the
# intersection of the half-planes {|x - q| <= |x - p_j|} over those
# neighbours, and the area it steals from neighbour i is that cell clipped
# by {|x - p_i| <= |x - p_j|} for the other neighbours. Every step is the
# clipping of a bounded convex polygon by a half-plane, so near-cocircular
# configurations (a raster) only add or drop slivers of vanishing area and
# the weights stay continuous in the site positions. A query on a hull
# edge gets the limiting weights: linear along that edge.
# ---------------------------------------------------------------------------
def _clip_halfplane(poly: np.ndarray, n: np.ndarray, c: float) -> np.ndarray:
    """Keep the part of a convex polygon with n·x <= c."""
    if len(poly) == 0:
        return poly
    out = []
    m = len(poly)
    vals = poly @ n - c
    for i in range(m):
        a, b = poly[i], poly[(i + 1) % m]
        va, vb = vals[i], vals[(i + 1) % m]
        if va <= 0:
            out.append(a)
        if (va < 0 < vb) or (vb < 0 < va):
            t = va / (va - vb)
            out.append(a + t * (b - a))
    return np.asarray(out, float) if out else np.zeros((0, 2))


def _bisector(p: np.ndarray, r: np.ndarray):
    """Half-plane {|x - p| <= |x - r|} as n·x <= c."""
    n = r - p
    c = 0.5 * (r @ r - p @ p)
    return n, c


class _WatsonCloud:
    def __init__(self, P: np.ndarray, rel_tol: float = 1e-10, edge_tol: float = 1e-7):
        self.P = np.asarray(P, float)
        self.n = len(self.P)
        self.rel_tol = float(rel_tol)
        self.edge_tol = float(edge_tol)
        self.span = float(np.linalg.norm(self.P.max(0) - self.P.min(0))) if self.n else 1.0
        self._tri = None

    @property
    def tri(self):
        if self._tri is None:
            self._tri = Delaunay(self.P)
            S = self.P[self._tri.simplices]
            a, b, c = S[:, 0], S[:, 1], S[:, 2]
            d = 2.0 * (a[:, 0] * (b[:, 1] - c[:, 1]) + b[:, 0] * (c[:, 1] - a[:, 1])
                       + c[:, 0] * (a[:, 1] - b[:, 1]))
            a2, b2, c2 = (a ** 2).sum(1), (b ** 2).sum(1), (c ** 2).sum(1)
            with np.errstate(divide="ignore", invalid="ignore"):
                ux = (a2 * (b[:, 1] - c[:, 1]) + b2 * (c[:, 1] - a[:, 1]) + c2 * (a[:, 1] - b[:, 1])) / d
                uy = (a2 * (c[:, 0] - b[:, 0]) + b2 * (a[:, 0] - c[:, 0]) + c2 * (b[:, 0] - a[:, 0])) / d
                self._cc = np.column_stack([ux, uy])
                self._r2 = ((a - self._cc) ** 2).sum(1)
            # Flat simplices (collinear vertices) have no circumcircle; they
            # never enter the conflict region.
            self._flat = ~np.isfinite(self._r2)
            hull = self._tri.convex_hull
            self._hull = hull
        return self._tri

    def _on_hull_edge(self, q):
        """
        Limiting weights for a query on (or within ``edge_tol`` of) a hull
        edge: linear between the two boundary sites that bracket it along
        that edge's line. Collinear boundary sites all count, whichever of
        them Qhull reports as hull vertices.
        """
        P = self.P
        tol = self.edge_tol * max(self.span, 1e-30)
        for a, b in self._hull:
            pa, pb = P[a], P[b]
            e = pb - pa
            L = float(np.sqrt(e @ e))
            if L <= 0:
                continue
            u = e / L
            nrm = np.array([-u[1], u[0]])
            if abs(float((q - pa) @ nrm)) > tol:
                continue
            tq = float((q - pa) @ u)
            if tq < -tol or tq > L + tol:
                continue
            on = np.abs((P - pa) @ nrm) <= tol
            idx = np.flatnonzero(on)
            t = (P[idx] - pa) @ u
            lo = idx[t <= tq]
            hi = idx[t >= tq]
            if len(lo) == 0 and len(hi) == 0:
                continue
            if len(lo) == 0 or len(hi) == 0:
                side = hi if len(lo) == 0 else lo
                ts = (P[side] - pa) @ u
                k = int(side[np.argmin(np.abs(ts - tq))])
                return np.array([k]), np.array([1.0])
            tl = (P[lo] - pa) @ u
            th = (P[hi] - pa) @ u
            i_lo = int(lo[np.argmax(tl)])
            i_hi = int(hi[np.argmin(th)])
            t_lo, t_hi = float(tl.max()), float(th.min())
            if i_lo == i_hi or t_hi - t_lo <= 0:
                return np.array([i_lo]), np.array([1.0])
            w = (tq - t_lo) / (t_hi - t_lo)
            return np.array([i_lo, i_hi], int), np.array([1.0 - w, w])
        return None

    def weights(self, q: np.ndarray):
        P = self.P
        q = np.asarray(q, float).ravel()
        n = self.n
        if n == 0:
            return np.array([], dtype=int), np.array([])
        if n == 1:
            return np.array([0]), np.array([1.0])
        tri = self.tri
        d = np.linalg.norm(P - q, axis=1)
        j = int(np.argmin(d))
        if d[j] < 1e-14:
            return np.array([j]), np.array([1.0])
        edge = self._on_hull_edge(q)
        if edge is not None:
            return edge
        s = int(tri.find_simplex(q))
        if s < 0:
            return np.array([], dtype=int), np.array([])
        # Conflict triangles: circumcircle contains q (flood fill from s).
        r2 = self._r2
        with np.errstate(invalid="ignore"):
            dq = ((self._cc - q) ** 2).sum(1)
            inside = (dq <= r2 * (1.0 + self.rel_tol)) & ~self._flat
        seen = {s}
        stack = [s]
        conflict = [s]
        while stack:
            t = stack.pop()
            for nb in tri.neighbors[t]:
                if nb < 0 or nb in seen:
                    continue
                seen.add(int(nb))
                if inside[nb]:
                    conflict.append(int(nb))
                    stack.append(int(nb))
        nbrs = np.unique(tri.simplices[conflict].ravel())
        # q's new Voronoi cell, clipped from a box that contains it.
        R = 1e6 * max(self.span, 1.0)
        box = np.array([[q[0] - R, q[1] - R], [q[0] + R, q[1] - R],
                        [q[0] + R, q[1] + R], [q[0] - R, q[1] + R]])
        cell = box
        for k in nbrs:
            nvec, c = _bisector(q, P[k])
            cell = _clip_halfplane(cell, nvec, c)
        areas = np.zeros(len(nbrs))
        for ii, i in enumerate(nbrs):
            part = cell
            for k in nbrs:
                if k == i:
                    continue
                nvec, c = _bisector(P[i], P[k])
                part = _clip_halfplane(part, nvec, c)
                if len(part) < 3:
                    break
            areas[ii] = _poly_area(part) if len(part) >= 3 else 0.0
        tot = areas.sum()
        if not np.isfinite(tot) or tot <= 0:
            return np.array([], dtype=int), np.array([])
        keep = areas > 0
        return nbrs[keep].astype(int), areas[keep] / tot


class _DelaunayCloud:
    """
    Barycentric weights on the enclosing Delaunay simplex, in any dimension.

    The interpolant is piecewise linear and continuous; like natural
    neighbours it depends on positions only. Outside the convex hull the
    weights are empty and the caller falls back to inverse-distance kNN.
    """

    def __init__(self, P: np.ndarray):
        self.P = np.asarray(P, float)
        self.n, self.d = self.P.shape if self.P.ndim == 2 else (0, 0)
        self._tri = None

    @property
    def tri(self):
        if self._tri is None:
            self._tri = Delaunay(self.P, qhull_options="QJ" if self.d > 2 else "Qbb Qc Qz Q12")
        return self._tri

    def weights(self, q: np.ndarray):
        q = np.asarray(q, float).ravel()
        if self.n == 0:
            return np.array([], dtype=int), np.array([])
        d = np.linalg.norm(self.P - q, axis=1)
        j = int(np.argmin(d))
        if d[j] < 1e-14:
            return np.array([j]), np.array([1.0])
        if self.n <= self.d:
            return np.array([], dtype=int), np.array([])
        tri = self.tri
        s = int(tri.find_simplex(q))
        if s < 0:
            return np.array([], dtype=int), np.array([])
        T = tri.transform[s]
        b = T[:self.d] @ (q - T[self.d])
        w = np.append(b, 1.0 - b.sum())
        w = np.clip(w, 0.0, None)
        if w.sum() <= 0:
            return np.array([], dtype=int), np.array([])
        idx = tri.simplices[s]
        keep = w > 0
        return np.asarray(idx[keep], int), w[keep] / w.sum()

"""Deterministic two-layer grid router used by the carrier generator.

Not an external autorouter: it is part of the generator source, runs the
same way every time, and its output is checked by KiCad DRC, schematic parity
and the copper-collision audit like hand-written copper.

Model: 0.25 mm grid, layers 0 = F.Cu, 1 = B.Cu, 8-direction moves on a layer,
vias between layers. A cell is usable by net N when no copper of another net
(pads, tracks, vias), board edge or hole is closer than the required clearance.
"""
import heapq
import math

import numpy as np
import pcbnew

STEP = 0.25
CLR = 0.2          # copper clearance (mm)
EDGE_CLR = 0.5     # copper to board edge
HOLE_CLR = 0.3     # copper to NPTH hole edge
VIA_D = 0.6
VIA_DRILL = 0.3
FREE = 0
BLOCK = -1


def mm(v):
    return pcbnew.ToMM(v)


class Grid:
    def __init__(self, board, width, height):
        self.b = board
        self.nx = int(round(width / STEP)) + 1
        self.ny = int(round(height / STEP)) + 1
        # owner[layer][half-width class] -> int grid: 0 free, -1 blocked, >0 net code
        self.radii = {}
        self.items = []   # (layer_mask, kind, geom, netcode)
        self.netcodes = {}
        self.W, self.H = width, height

    # ------------------------------------------------------------ copper inventory
    def code(self, name):
        if name not in self.netcodes:
            self.netcodes[name] = len(self.netcodes) + 1
        return self.netcodes[name]

    def add_pad(self, pad):
        pos = pad.GetPosition()
        x, y = mm(pos.x), mm(pos.y)
        sx, sy = mm(pad.GetSize().x), mm(pad.GetSize().y)
        ang = round(pad.GetOrientation().AsDegrees()) % 180
        if ang == 90:
            sx, sy = sy, sx
        layers = []
        if pad.IsOnLayer(pcbnew.F_Cu):
            layers.append(0)
        if pad.IsOnLayer(pcbnew.B_Cu):
            layers.append(1)
        net = pad.GetNetname()
        code = self.code(net) if net and not net.startswith("unconnected") else BLOCK
        if pad.GetDrillSize().x > 0:
            # vias keep 0.5 mm hole-to-hole from every drilled pad, whatever its net
            d = mm(pad.GetDrillSize().x)
            self.items.append(((0, 1), "via_only", (x, y, d / 2 + 0.5 + VIA_DRILL / 2 - CLR - VIA_D / 2), BLOCK))
        if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
            d = mm(pad.GetDrillSize().x)
            self.items.append(((0, 1), "circle", (x, y, d / 2 + HOLE_CLR - CLR), BLOCK))
            return
        if pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
            self.items.append((tuple(layers), "circle", (x, y, sx / 2), code))
        else:
            self.items.append((tuple(layers), "rect", (x, y, sx / 2, sy / 2), code))

    def add_segment(self, layer, a, b, width, net):
        self.items.append(((layer,), "seg", (a[0], a[1], b[0], b[1], width / 2), self.code(net)))

    def add_via(self, x, y, net):
        self.items.append(((0, 1), "circle", (x, y, VIA_D / 2), self.code(net)))

    # ------------------------------------------------------------ rasterising
    def _mark(self, grid, item, inflate):
        _layers, kind, g, code = item
        if kind == "circle":
            x, y, r = g
            R = r + inflate
            x0, x1, y0, y1 = x - R, x + R, y - R, y + R
        elif kind == "rect":
            x, y, hx, hy = g
            x0, x1, y0, y1 = x - hx - inflate, x + hx + inflate, y - hy - inflate, y + hy + inflate
        else:
            ax, ay, bx, by, hw = g
            R = hw + inflate
            x0, x1 = min(ax, bx) - R, max(ax, bx) + R
            y0, y1 = min(ay, by) - R, max(ay, by) + R
        i0, i1 = max(0, int(math.floor(x0 / STEP))), min(self.nx - 1, int(math.ceil(x1 / STEP)))
        j0, j1 = max(0, int(math.floor(y0 / STEP))), min(self.ny - 1, int(math.ceil(y1 / STEP)))
        if i0 > i1 or j0 > j1:
            return
        xs = np.arange(i0, i1 + 1) * STEP
        ys = np.arange(j0, j1 + 1) * STEP
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        if kind == "circle":
            d = np.hypot(X - x, Y - y) - r
        elif kind == "rect":
            dx = np.maximum(np.abs(X - x) - hx, 0)
            dy = np.maximum(np.abs(Y - y) - hy, 0)
            d = np.hypot(dx, dy)
        else:
            vx, vy = bx - ax, by - ay
            L2 = vx * vx + vy * vy
            t = np.clip(((X - ax) * vx + (Y - ay) * vy) / L2, 0, 1) if L2 > 0 else 0
            d = np.hypot(X - (ax + t * vx), Y - (ay + t * vy)) - hw
        mask = d < inflate - 1e-6
        sub = grid[i0:i1 + 1, j0:j1 + 1]
        cur = sub[mask]
        new = np.where((cur == FREE) | (cur == code), code, BLOCK)
        sub[mask] = new

    def build(self, half_width):
        """Usability grids for a centreline of the given half-width (trace) and for vias."""
        out = []
        for gi, inflate in enumerate((CLR + half_width, CLR + VIA_D / 2)):
            layers = [np.zeros((self.nx, self.ny), dtype=np.int32) for _ in range(2)]
            for g in layers:
                e = int(math.ceil((EDGE_CLR + inflate - CLR) / STEP))
                g[:e, :] = BLOCK
                g[-e:, :] = BLOCK
                g[:, :e] = BLOCK
                g[:, -e:] = BLOCK
            for item in self.items:
                if item[1] == "via_only":
                    if gi == 0:
                        continue
                    item = (item[0], "circle", item[2], item[3])
                for L in item[0]:
                    self._mark(layers[L], item, inflate)
            out.append(layers)
        return out

    # ------------------------------------------------------------ search
    def route(self, net, starts, targets, half_width, via_cost=12.0, layers_allowed=(0, 1),
              grids=None, extra_block=None):
        """A* from any start cell to any target cell. starts/targets: sets of (L, i, j)."""
        code = self.code(net)
        tr, vi = grids if grids is not None else self.build(half_width)

        def ok(L, i, j):
            if not (0 <= i < self.nx and 0 <= j < self.ny) or L not in layers_allowed:
                return False
            v = tr[L][i, j]
            return v == FREE or v == code

        def ok_via(i, j):
            return all((vi[L][i, j] == FREE or vi[L][i, j] == code) for L in (0, 1))

        tgt = set(targets)
        tx = [(i, j) for (_L, i, j) in tgt]
        ti0, ti1 = min(a for a, _ in tx), max(a for a, _ in tx)
        tj0, tj1 = min(b for _, b in tx), max(b for _, b in tx)

        def h(i, j):
            if len(tx) < 40:
                return min(math.hypot(i - a, j - b) for a, b in tx)
            # admissible: distance to the targets' bounding box
            di = ti0 - i if i < ti0 else (i - ti1 if i > ti1 else 0)
            dj = tj0 - j if j < tj0 else (j - tj1 if j > tj1 else 0)
            return math.hypot(di, dj)

        dirs = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        # State = cell only; the arrival direction is kept for a turn penalty
        # (slightly suboptimal, much faster than direction-expanded states).
        openh = []
        g = {}
        prev = {}
        arr = {}
        for st in starts:
            if ok(*st):
                g[st] = 0.0
                arr[st] = -1
                heapq.heappush(openh, (h(st[1], st[2]), 0.0, st))
        best_end = None
        done = set()
        while openh:
            f, cost, s = heapq.heappop(openh)
            if s in done:
                continue
            done.add(s)
            if s in tgt:
                best_end = s
                break
            L, i, j = s
            d = arr[s]
            for k, (di, dj, c) in enumerate(dirs):
                n = (L, i + di, j + dj)
                if n in done or not ok(*n):
                    continue
                if di and dj and not (ok(L, i + di, j) and ok(L, i, j + dj)):
                    continue
                nc = cost + c + (0.0 if d == -1 or d == k else 0.6)
                if nc < g.get(n, 1e18):
                    g[n] = nc
                    prev[n] = s
                    arr[n] = k
                    heapq.heappush(openh, (nc + h(n[1], n[2]), nc, n))
            if ok_via(i, j):
                n = (1 - L, i, j)
                if n not in done and ok(*n):
                    nc = cost + via_cost
                    if nc < g.get(n, 1e18):
                        g[n] = nc
                        prev[n] = s
                        arr[n] = -1
                        heapq.heappush(openh, (nc + h(i, j), nc, n))
        if best_end is None:
            return None
        path = [best_end]
        key = best_end
        while key in prev:
            key = prev[key]
            path.append(key)
        path.reverse()
        return path


def path_to_copper(path):
    """Collapse a cell path into [(layer, [(x, y), ...])] polylines and via points."""
    polys = []
    vias = []
    cur = [path[0]]
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]:
            polys.append(cur)
            vias.append((a[1] * STEP, a[2] * STEP))
            cur = [b]
        else:
            cur.append(b)
    polys.append(cur)
    out = []
    for poly in polys:
        if len(poly) < 2:
            continue
        pts = [poly[0]]
        for k in range(1, len(poly) - 1):
            p0, p1, p2 = pts[-1], poly[k], poly[k + 1]
            d1 = (p1[1] - p0[1], p1[2] - p0[2])
            d2 = (p2[1] - p1[1], p2[2] - p1[2])
            n1 = (int(math.copysign(1, d1[0])) if d1[0] else 0, int(math.copysign(1, d1[1])) if d1[1] else 0)
            n2 = (int(math.copysign(1, d2[0])) if d2[0] else 0, int(math.copysign(1, d2[1])) if d2[1] else 0)
            if n1 != n2:
                pts.append(p1)
        pts.append(poly[-1])
        out.append((poly[0][0], [(p[1] * STEP, p[2] * STEP) for p in pts]))
    return out, vias

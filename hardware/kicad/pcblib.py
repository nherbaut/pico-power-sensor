"""Shared helpers for the board generators (run under KiCad's /usr/bin/python3)."""
import re
import uuid
from pathlib import Path

import pcbnew

MM = pcbnew.FromMM
LIB = Path(__file__).resolve().parent / "lib" / "picopower-proto.pretty"


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def parse_netlist(path):
    """Return ({(ref, pad): net}, {ref: (footprint, [symbol uuids])}) from a KiCad netlist."""
    text = Path(path).read_text()
    comps = {}
    for block in text.split("(comp (ref ")[1:]:
        ref = re.match(r'"([^"]+)"', block).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', block).group(1)
        val = re.search(r'\(value "([^"]*)"\)', block).group(1)
        ts = re.findall(r'\(tstamps ((?:"[^"]+"\s*)+)\)', block)
        uuids = re.findall(r'"([^"]+)"', ts[-1]) if ts else []
        comps[ref] = (fp, uuids, val)
    pads = {}
    nets_part = text[text.index("(nets"):]
    for block in nets_part.split("(net (code ")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', block).group(1)
        for node in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', block):
            pads[(node.group(1), node.group(2))] = name
    if not comps or not pads:
        raise SystemExit(f"netlist {path} parsed empty")
    return pads, comps


class Board:
    def __init__(self, netlist):
        self.b = pcbnew.BOARD()
        self.pads, self.comps = parse_netlist(netlist)
        self.io = pcbnew.PCB_IO_KICAD_SEXPR()
        self.nets = {}
        self.fps = {}
        self.ns = uuid.uuid5(uuid.NAMESPACE_URL, str(netlist))

    def net(self, name):
        if name not in self.nets:
            n = pcbnew.NETINFO_ITEM(self.b, name)
            self.b.Add(n)
            self.nets[name] = n
        return self.nets[name]

    def outline(self, pts, width=0.1):
        for a, b in zip(pts, pts[1:] + pts[:1]):
            s = pcbnew.PCB_SHAPE(self.b, pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(V(*a))
            s.SetEnd(V(*b))
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(MM(width))
            self.b.Add(s)

    def place(self, ref, x, y, rot=0, back=False, fpname=None, board_only=False):
        if fpname is None:
            fpname = self.comps[ref][0].split(":", 1)[1]
        else:
            lib_fp = "picopower-proto:" + fpname
        fp = self.io.FootprintLoad(str(LIB), fpname)
        if fp is None:
            raise SystemExit(f"footprint {fpname} not found")
        fp.SetFPID(pcbnew.LIB_ID("picopower-proto", fpname))
        fp.SetReference(ref)
        self.b.Add(fp)
        if back:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(V(x, y))
        if board_only:
            fp.SetBoardOnly(True)
            fp.SetExcludedFromBOM(True)
        elif ref in self.comps:
            fp.SetPath(pcbnew.KIID_PATH("/" + self.comps[ref][1][0]))
            fp.SetValue(self.comps[ref][2])
        for p in fp.Pads():
            key = (ref, p.GetNumber())
            if p.GetNumber() and key in self.pads:
                p.SetNet(self.net(self.pads[key]))
            elif p.GetNumber() and not board_only:
                raise SystemExit(f"pad {key} missing from netlist")
        self.fps[ref] = fp
        return fp

    def ref_at(self, ref, x=None, y=None, rot=None, hide=False, size=0.8):
        """Reference text: hidden, or moved (default: footprint centre)."""
        fp = self.fps[ref]
        r = fp.Reference()
        if hide:
            r.SetVisible(False)
            return
        if x is None:
            c = fp.GetBoundingBox(False).GetCenter()
            x, y = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
        r.SetPosition(V(x, y))
        r.SetTextSize(V(size, size))
        r.SetTextThickness(MM(0.12))
        if rot is not None:
            r.SetTextAngleDegrees(rot)

    def solid_pads(self, ref, nums):
        """Solid zone connection for pads whose 2.54 mm neighbours leave no room for spokes."""
        for p in self.fps[ref].Pads():
            if p.GetNumber() in nums:
                p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)

    def pad_xy(self, ref, num):
        for p in self.fps[ref].Pads():
            if p.GetNumber() == num:
                pos = p.GetPosition()
                return (round(pcbnew.ToMM(pos.x), 4), round(pcbnew.ToMM(pos.y), 4))
        raise KeyError((ref, num))

    def track(self, net, pts, width, layer=pcbnew.F_Cu):
        n = self.net(net)
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.b)
            t.SetStart(V(*a))
            t.SetEnd(V(*b))
            t.SetWidth(MM(width))
            t.SetLayer(layer)
            t.SetNet(n)
            self.b.Add(t)

    def via(self, net, x, y, size=0.8, drill=0.4):
        v = pcbnew.PCB_VIA(self.b)
        v.SetPosition(V(x, y))
        v.SetWidth(MM(size))
        v.SetDrill(MM(drill))
        v.SetNet(self.net(net))
        self.b.Add(v)

    def zone(self, net, layer, pts, clearance=0.3, spoke=0.8, min_width=0.25, priority=0):
        z = pcbnew.ZONE(self.b)
        z.SetLayer(layer)
        z.SetNet(self.net(net))
        # Append to the zone's own outline: SetOutline(poly) keeps a pointer to a
        # Python-owned SHAPE_POLY_SET and Save() segfaults after it is collected.
        ol = z.Outline()
        ol.NewOutline()
        for x, y in pts:
            ol.Append(MM(x), MM(y))
        z.SetLocalClearance(MM(clearance))
        z.SetThermalReliefSpokeWidth(MM(spoke))
        z.SetThermalReliefGap(MM(0.5))
        z.SetMinThickness(MM(min_width))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetAssignedPriority(priority)
        self.b.Add(z)
        return z

    def text(self, s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetPosition(V(x, y))
        t.SetLayer(layer)
        t.SetTextSize(V(size, size))
        t.SetTextThickness(MM(0.15 if size >= 1 else 0.12))
        t.SetTextAngleDegrees(rot)
        if layer in (pcbnew.B_SilkS,):
            t.SetMirrored(True)
        self.b.Add(t)

    def rules(self):
        ds = self.b.GetDesignSettings()
        ds.m_MinClearance = MM(0.2)
        ds.m_TrackMinWidth = MM(0.25)
        ds.m_ViasMinSize = MM(0.6)
        ds.m_MinThroughDrill = MM(0.3)
        ds.m_CopperEdgeClearance = MM(0.5)
        ds.m_HoleClearance = MM(0.25)
        ds.m_HoleToHoleMin = MM(0.5)
        ds.m_SilkClearance = MM(0.0)

    def fill_and_save(self, path):
        # A bare in-memory BOARD() crashes ZONE_FILLER; save, reload, fill, save.
        self.b.Save(str(path))
        b = pcbnew.LoadBoard(str(path))
        b.BuildConnectivity()
        filler = pcbnew.ZONE_FILLER(b)
        filler.Fill(b.Zones())
        b.Save(str(path))
        self.harden_severities(Path(path).with_suffix(".kicad_pro"))

    @staticmethod
    def harden_severities(pro):
        """Promote stock 'ignore' DRC checks that matter here (courtyards, footprint type)."""
        import json
        d = json.loads(pro.read_text())
        rs = d.setdefault("board", {}).setdefault("design_settings", {}).setdefault("rule_severities", {})
        for k in ("missing_courtyard", "npth_inside_courtyard", "pth_inside_courtyard"):
            rs[k] = "error"
        for k in ("footprint_type_mismatch", "footprint_filters_mismatch"):
            rs[k] = "warning"
        pro.write_text(json.dumps(d, indent=2) + "\n")

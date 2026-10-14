"""Manufacturer-based footprint geometry shared by CAD generation and review tools."""
import math
import pcbnew


def point(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def part_fields(fp, part):
    """Persist procurement metadata in native boards after footprint replacement."""
    for key, value in {'MPN': part['mpn'], 'Datasheet': part['documentation_url']}.items():
        field = fp.GetFieldByName(key)
        if field is None:
            fp.AddField(pcbnew.PCB_FIELD(fp, fp.GetNextFieldId(), key))
            field = fp.GetFieldByName(key)
        field.SetText(value)
        field.SetVisible(False)


def selected_passive(fp, name):
    """Copper lands for selected Vishay, Murata and KEMET parts."""
    dimensions = {'R_0805_TNPW': (.95, .9, 1.45),
                  'C_0805_Murata': (.9, .6, 1.25),
                  'C_0805_KEMET': (.9, 1.15, 1.45)}
    if name not in dimensions:
        return
    offset, width, height = dimensions[name]
    for pad in fp.Pads():
        pad.SetFPRelativePosition(point(-offset if pad.GetNumber() == '1' else offset, 0))
        pad.SetSize(point(width, height))
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    if name == 'C_0805_KEMET':
        # KEM_C1003_C0G_SMD, 2025-02-20, p12, table 3, 0805 density B.
        for graphic in list(fp.GraphicalItems()):
            if graphic.GetLayer() in (pcbnew.F_CrtYd, pcbnew.F_SilkS):
                fp.Remove(graphic)
        rectangle(fp, pcbnew.F_CrtYd, -1.75, -1.0, 1.75, 1.0, .05)
        for y in (-.95, .95):
            shape = pcbnew.PCB_SHAPE(fp)
            shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
            shape.SetLayer(pcbnew.F_SilkS)
            shape.SetStart(global_point(fp, -.6, y))
            shape.SetEnd(global_point(fp, .6, y))
            shape.SetWidth(pcbnew.FromMM(.12))
            fp.Add(shape)


def global_point(fp, x, y):
    angle = math.radians(fp.GetOrientationDegrees())
    origin = fp.GetPosition()
    return origin + point(x*math.cos(angle)+y*math.sin(angle), -x*math.sin(angle)+y*math.cos(angle))


def rectangle(fp, layer, left, top, right, bottom, width):
    shape = pcbnew.PCB_SHAPE(fp)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetLayer(layer)
    shape.SetStart(global_point(fp, left, top))
    shape.SetEnd(global_point(fp, right, bottom))
    shape.SetWidth(pcbnew.FromMM(width))
    fp.Add(shape)


def led(fp):
    for pad in fp.Pads():
        if pad.GetNumber() in ('1', '2'):
            pad.SetFPRelativePosition(point(-1.175 if pad.GetNumber() == '1' else 1.175, 0))
            pad.SetSize(point(1.25, 1.1))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    for graphic in list(fp.GraphicalItems()):
        if graphic.GetLayer() in (pcbnew.F_CrtYd, pcbnew.F_SilkS):
            fp.Remove(graphic)
    rectangle(fp, pcbnew.F_CrtYd, -2.05, -.9, 2.05, .9, .05)
    # Horizontal silk strokes stay outside mask openings; short cathode marker.
    for x1, y1, x2, y2 in [(-1,-.75,1,-.75),(-1,.75,1,.75),(-1.95,-.6,-1.95,.6)]:
        shape=pcbnew.PCB_SHAPE(fp)
        shape.SetShape(pcbnew.SHAPE_T_SEGMENT);shape.SetLayer(pcbnew.F_SilkS)
        shape.SetStart(global_point(fp,x1,y1));shape.SetEnd(global_point(fp,x2,y2))
        shape.SetWidth(pcbnew.FromMM(.12));fp.Add(shape)


def shunt(fp):
    # Vishay 30108 page 2, 5..200 mOhm row: e=1.70, c=.76.
    # Retain outer edge at +/-4.13 mm and the existing .51 mm vertical gap.
    for pad in fp.Pads():
        if pad.GetNumber() in ('2', '3'):
            left = pad.GetNumber() == '2'
            pad.SetSize(point(1.7, .76))
            pad.SetFPRelativePosition(point(-3.28 if left else 3.28, 1.27 if left else -1.27))
    for graphic in list(fp.GraphicalItems()):
        if graphic.GetLayer()==pcbnew.F_SilkS:
            fp.Remove(graphic)
    for y in (-1.85,1.85):
        shape=pcbnew.PCB_SHAPE(fp);shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
        shape.SetLayer(pcbnew.F_SilkS);shape.SetWidth(pcbnew.FromMM(.12))
        shape.SetStart(global_point(fp,-2,y));shape.SetEnd(global_point(fp,2,y));fp.Add(shape)


def socket(fp):
    # 10461-H: 4.85 mm projected depth, 7.20 mm height. Keep provisional body offset.
    for graphic in fp.GraphicalItems():
        if isinstance(graphic, pcbnew.PCB_SHAPE) and graphic.GetLayer() in (pcbnew.F_Fab, pcbnew.F_SilkS):
            graphic.SetStart(global_point(fp,-8.30,-1.25))
            graphic.SetEnd(global_point(fp,-3.45,11.25))
    # Retain the old larger courtyard until the offset/mating direction is physically verified.



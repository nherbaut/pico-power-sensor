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


def mosfet(fp):
    """Infineon BSC010N04LS6 PG-TDSON-8-FL boardpads (datasheet rev 2.3, page 11, figure 2).

    Applied to the KiCad TDSON-8-1 stock footprint. Copper follows Infineon: drain
    4.455 x 4.41 mm, lead pads 1.055 mm long, and one 3.19 mm source pad under the three
    source leads (pads 1-3 stay as separate numbers on the same net; pads 2 and 3 lie inside
    pad 1). Solder paste keeps the earlier 0.85 x 0.5 mm aperture per lead until the
    Infineon stencil apertures are agreed with the assembler. Safe to apply twice.
    """
    lead_x = -(2.27 + 3.325) / 2
    copper_mask = pcbnew.LSET()
    copper_mask.AddLayer(pcbnew.F_Cu)
    copper_mask.AddLayer(pcbnew.F_Mask)
    for pad in list(fp.Pads()):
        number = pad.GetNumber()
        position = pad.GetFPRelativePosition()
        # Remove paste helpers from an earlier application.
        if not number and abs(pcbnew.ToMM(position.x) + 2.9) < .05 and pad.GetLayerSet().Contains(pcbnew.F_Paste) \
                and not pad.GetLayerSet().Contains(pcbnew.F_Cu):
            fp.Remove(pad)
    for pad in list(fp.Pads()):
        number = pad.GetNumber()
        if number == '5':
            pad.SetSize(point(4.455, 4.41))
            pad.SetFPRelativePosition(point((-1.13 + 3.325) / 2, 0))
        elif number in ('1', '2', '3', '4'):
            y = {'1': -1.905, '2': -.635, '3': .635, '4': 1.905}[number]
            if number == '1':
                pad.SetSize(point(1.055, 3.19))
                pad.SetFPRelativePosition(point(lead_x, -.635))
            else:
                pad.SetSize(point(1.055, .5))
                pad.SetFPRelativePosition(point(lead_x, y))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetLayerSet(copper_mask)
    for y in (-1.905, -.635, .635, 1.905):
        paste = pcbnew.PAD(fp)
        paste.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        paste.SetShape(pcbnew.PAD_SHAPE_ROUNDRECT)
        paste.SetRoundRectRadiusRatio(.25)
        paste.SetSize(point(.85, .5))
        layers = pcbnew.LSET()
        layers.AddLayer(pcbnew.F_Paste)
        paste.SetLayerSet(layers)
        fp.Add(paste)
        paste.SetOrientation(fp.GetOrientation())  # pad angles follow the footprint
        paste.SetFPRelativePosition(point(-2.9, y))


def socket(fp):
    # 10461-H: 4.85 mm projected depth, 7.20 mm height. Keep provisional body offset.
    for graphic in fp.GraphicalItems():
        if isinstance(graphic, pcbnew.PCB_SHAPE) and graphic.GetLayer() in (pcbnew.F_Fab, pcbnew.F_SilkS):
            graphic.SetStart(global_point(fp,-8.30,-1.25))
            graphic.SetEnd(global_point(fp,-3.45,11.25))
    # Retain the old larger courtyard until the offset/mating direction is physically verified.



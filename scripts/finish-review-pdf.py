#!/usr/bin/env python3
"""Centre an unscaled KiCad paper plot and add a separate 50 mm print ruler."""
import io
from pathlib import Path
import sys
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def finish(path, name, board_width_mm):
    reader = PdfReader(path)
    page = reader.pages[0]
    width, height = float(page.mediabox.width), float(page.mediabox.height)
    # Native boards start at (0,0); KiCad plots mm at 1:1 from the page's top-left.
    page.add_transformation(Transformation().translate((width-board_width_mm*mm)/2, -70*mm))
    overlay = io.BytesIO()
    drawing = canvas.Canvas(overlay, pagesize=(width, height), invariant=1)
    drawing.setFont('Helvetica-Bold', 13)
    drawing.drawString(20*mm, height-20*mm, f'PicoPower {name} - unpowered paper mock-up')
    drawing.setFont('Helvetica', 9)
    drawing.drawString(20*mm, height-27*mm, 'Print at 100% / actual size. Do not fit to page or mirror. Not fabrication data.')
    drawing.drawString(20*mm, height-33*mm, 'Verify this ruler is exactly 50 mm before cutting. CAD geometry is not physical fit evidence.')
    y = height-43*mm
    drawing.line(20*mm, y, 70*mm, y)
    for x in range(20, 71, 10):
        drawing.line(x*mm, y-2*mm, x*mm, y+2*mm)
    drawing.drawString(74*mm, y-1*mm, '50 mm')
    drawing.save()
    page.merge_page(PdfReader(overlay).pages[0])
    writer = PdfWriter()
    writer.add_page(page)
    target = Path(path)
    temporary = target.with_suffix('.tmp.pdf')
    with temporary.open('wb') as handle:
        writer.write(handle)
    temporary.replace(target)


if __name__ == '__main__':
    finish(sys.argv[1], sys.argv[2], float(sys.argv[3]))

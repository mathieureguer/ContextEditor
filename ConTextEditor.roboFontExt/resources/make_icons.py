from fontParts.world import OpenFont

f = OpenFont("icons.ufo")
icons = [
    ("toggle", "toggleButton.pdf"),
    ("edit", "editButton.pdf"),
    ]

for glyph, path in icons:

    newDrawing()
    newPage(20, 20)
    g = f[glyph]
    ratio = width() / g.width
    scale(ratio, ratio)
    bez = BezierPath()
    g.draw(bez)
    drawPath(bez)
    saveImage(path)

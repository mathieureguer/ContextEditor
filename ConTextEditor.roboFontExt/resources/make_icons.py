from fontParts.world import OpenFont

f = OpenFont("icons.ufo")

# UI

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


# ICON

MARGIN = 40
BACKGROUND = (0, .5, .5)
FOREGROUND = (1, 1, 1)
GLYPH = "edit"
PATH = "icon.png"

def round_rect(x, y, w, h, radius, curvature=.55):
    bez = BezierPath()

    x1 = x+radius
    x2 = x1 + w-radius*2
    x3 = x + w

    y1 = y + radius
    y2 = y1 + h-radius*2
    y3 = y + h

    bez.moveTo((x1, y))
    bez.lineTo((x2, y))
    bez.curveTo((x2+radius*curvature, y), (x3, y1-radius*curvature), (x3, y1))
    bez.lineTo((x3, y2))
    bez.curveTo((x3, y2+radius*curvature), (x2+radius*curvature, y3), (x2, y3))
    bez.lineTo((x1, y3))
    bez.curveTo((x1-radius*curvature, y3), (x, y2+radius*curvature), (x, y2))
    bez.lineTo((x, y1))
    bez.curveTo((x, y1-radius*curvature), (x1-radius*curvature, y), (x1, y))
    bez.closePath()

    drawPath(bez)


newDrawing()
newPage(512, 512)

fill(0, 1, .8)
round_rect(0, 0, width(), height(), 80)

fill(1, 1, 1)

g = f["toggle"]
ratio = (width() - MARGIN*2) / g.width
with savedState():
    translate(MARGIN, MARGIN)
    scale(ratio, ratio)
    bez = BezierPath()
    g.draw(bez)
    drawPath(bez)

fill(1, 0, 0)
g = f[GLYPH]
ratio = (width() - MARGIN*2) / g.width
with savedState():
    translate(MARGIN, MARGIN)
    scale(ratio, ratio)
    bez = BezierPath()
    g.draw(bez)
    drawPath(bez)


saveImage(PATH)

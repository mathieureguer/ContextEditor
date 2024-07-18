# ConTextEditor (working title)

ConTextEditor is a Robofont extention that display neighbor glyphs in your glyph editor, much like the great RamsayStreet — with aditional flexibility. 

Neighbors are not fetched from a preexisting database, instead the focus is set on setting them on the fly.


Multiple neighbors can be displayed at once.

A background / mask neighbors is available, for overlay under the current glyph.

Any open ufo can be used a neighbor provider.

## tokens

A few special token are available when setting up neighbors:

- `<self>` will be replaced by the current glyph name. 
- `<root>` will be replaced by the current glyph name, without suffix.
- `@layerName` will fetch said layer from the requested glyph.


`<self>.onum` will display `eight.onum` when current glyph is `eight`

`<root>` will display `A` when current glyph is `À.smcp`

`<root>.alt@background` will display the `background` layer from `È.alt` when current glyph is `È.ss02`


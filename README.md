# ConTextEditor (working title)

ConTextEditor is a Robofont extention that display neighbor glyphs in your glyph editor, much like the great RamsayStreet — with aditional flexibility. 

Neighbors are not fetched from a preexisting database, instead the focus is set on setting them on the fly.
![UI](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/UI-annotated.png)


Multiple neighbors can be displayed at once.
![background](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/multiple-neighbors.png)


A background / mask neighbors is available, for overlay under the current glyph.
![background](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/mask-1.png)

Any open ufo can be used as neighbor provider.
![preview](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/preview.png)

Instances from DesignSpaces open via the great DesignSpaceEditor can used as neighbor provider as well. Interpolation is live and will update with your edits. 

![designspace](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/designspace.gif)


## tokens

A few dynamic tokens are available when setting up neighbors:

- `<self>` will be replaced by the current glyph name. 

  ![<self>](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/self.gif)

- `<root>` will be replaced by the current glyph name, without suffix.

  ![<root>](https://github.com/mathieureguer/ContextEditor/blob/main/resources/screens/root.png)

- `@layerName` will fetch said layer from the requested glyph.


`<self>.onum` will display `eight.onum` when current glyph is `eight`

`<root>` will display `A` when current glyph is `À.smcp`

`<root>.alt@background` will display the `background` layer from `E.alt` when current glyph is `E.ss02`


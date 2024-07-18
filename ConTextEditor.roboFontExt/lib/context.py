from mojo.subscriber import *
from mojo.UI import CurrentGlyphWindow, inDarkMode, getDefault
from mojo.roboFont import CurrentGlyph, CurrentFont, AllFonts, RGlyph

import merz
import vanilla

import pathlib

from EzuiExtentionSettingsManager import ExtentionSettingsManager

# ----------------------------------------

CURRENT_FONT_MENU_NAME = "CurrentFont"
CURRENT_GLYPH_TAG = "<self>"
ROOT_GLYPH_TAG = "<root>"
LAYER_NAME_TOKEN = "@"

DEFAULT_CONTEXT_DICT = {"querry": "n", "font": None}

DEFAULTS = {
    "neighbor_color_light" : (.24, .75, .9, 1),
    "neighbor_color_dark"  : (.6, .3, .5, 1),
    "mask_color_light"     : (.5, .7, .7, .7),
    "mask_color_dark"      : (.4, .15, .4, .7),
    "edit_color_light"     : (0, 1, 1, 1),
    "edit_color_dark"      : (0.9, 0, .6, 1),
}

DEFAULT_KEY = "com.mathieureguer.ConTextEditor."

# ----------------------------------------

def _get_font_string(font):
    if font == None:
        return CURRENT_FONT_MENU_NAME
    else:
        return f"{font.info.familyName} {font.info.styleName}"

# ----------------------------------------
# subcriber toogling 
# ----------------------------------------

register_function_map = {
        registerRoboFontSubscriber: unregisterRoboFontSubscriber,
        registerFontOverviewSubscriber: unregisterFontOverviewSubscriber,
        registerGlyphEditorSubscriber: unregisterGlyphEditorSubscriber,
        registerSpaceCenterSubscriber: unregisterSpaceCenterSubscriber,
        registerCurrentFontSubscriber: unregisterCurrentFontSubscriber,
        registerCurrentGlyphSubscriber: unregisterCurrentGlyphSubscriber,
    }

def toggleSubscriberClass(SubscriberClass, register_function):
    assert register_function in register_function_map, f"{register_function} appears not to be a supported Subscriber registration method"
    registered_subscribers = listRegisteredSubscribers(subscriberClassName=SubscriberClass.__name__)
    if len(registered_subscribers) > 0:
        unregister_function = register_function_map.get(register_function)
        for target_subscriber in registered_subscribers:
            unregister_function(target_subscriber)
        print(f"Toggle {SubscriberClass.__name__} off")
    else:
        register_function(SubscriberClass)
        print(f"Toggle {SubscriberClass.__name__} on")

def toggleSubscriberClassOn(SubscriberClass, register_function):
    assert register_function in register_function_map.keys(), f"{register_function} appears not to be a supported Subscriber registration method"
    registered_subscribers = listRegisteredSubscribers(subscriberClassName=SubscriberClass.__name__)
    if len(registered_subscribers) == 0:
        register_function(SubscriberClass)
    print(f"Toggle {SubscriberClass.__name__} on")
    # return listRegisteredSubscribers(subscriberClassName=SubscriberClass.__name__)[-1]

def toggleSubscriberClassOff(SubscriberClass, unregister_function):
    assert unregister_function in register_function_map.values(), f"{unregister_function} appears not to be a supported Subscriber unregistration method"
    registered_subscribers = listRegisteredSubscribers(subscriberClassName=SubscriberClass.__name__)
    if len(registered_subscribers) > 0:
        for target_subscriber in registered_subscribers:
            unregister_function(target_subscriber)
    print(f"Toggle {SubscriberClass.__name__} off")

def getActiveSubscriberByClass(SubscriberClass):
    registered_subscribers = listRegisteredSubscribers(subscriberClassName=SubscriberClass.__name__)
    return (registered_subscribers)

# ----------------------------------------
# Merz helper
# ----------------------------------------

## this is very hacky. I am sorry.

def merz_counter_offset_pt(layer, point):
    if layer != None:
        super_layer = layer.getSuperlayer()
        if super_layer != None:    
            pt_x, pt_y = point
            l_x, l_y = super_layer.getPosition()
            point = (pt_x - l_x, pt_y - l_y)
            return merz_counter_offset_pt(super_layer, point)
        else:
            return point

def merz_get_absolute_position(layer):
    layer_stack = _get_super_layer_recursive(layer, [])
    pt_x = 0
    pt_y = 0
    for l in layer_stack:
        l_x, l_y = l.getPosition()
        pt_x += l_x
        pt_y += l_y
    return pt_x, pt_y

def _get_super_layer_recursive(layer, layer_list):
    layer_list.append(layer)
    if layer.getSuperlayer() != None:
        _get_super_layer_recursive(layer.getSuperlayer(), layer_list)
    return layer_list


# ----------------------------------------
# UI objects
# ----------------------------------------

class BaseContextEditorBox():
    allow_delete = False

    def __init__(self, parent=None, **kwarg):
        self.parent = parent 

        self._x = 0
        self._y = 0
        self._width = 100
        self._height = 100

        self.hit_testing_layer = None
        self._overlayed = False
        self._selected = False

        self._edit_mode = False

    # ----------------------------------------
    # geometry 

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        for c in self.containers:
            x, y = c.getPosition()
            c.setPosition((value, y))

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def bounds(self):
        return self.x, self.y, self.width, self.height
        # return self.x + self.offset, self.y, self.width, self.height

    @property
    def containers(self):
        return []

    # ----------------------------------------
    # hit testing

    def is_point_inside(self, point):
        if self.hit_testing_layer:
            offset_point = merz_counter_offset_pt(self.hit_testing_layer, point)
            return self.hit_testing_layer.containsPoint(offset_point)
        
        # I guess this could be dealt with by merz directly
        #return self.x + self.offset < point[0] < self.x + self.offset + self.width and self.y < point[1] < self.y + self.height

    # ----------------------------------------
    # mouse events

    @property
    def overlayed(self):
        return self._overlayed
    
    @overlayed.setter
    def overlayed(self, value):
        self._overlayed = value
        if value == True:
            self.overlayed_callback()
        else:
            self.unoverlayed_callback()

    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, value):
        self._selected = value
        if value == True:
            self.selected_callback()
        else:
            self.unselected_callback()

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value
        if value == True:
            self.edit_mode_on_callback()
        else:
            self.edit_mode_off_callback()

    def selected_callback(self):
        pass

    def unselected_callback(self):
        pass

    def overlayed_callback(self):
        pass

    def unoverlayed_callback(self):
        pass

    def edit_mode_on_callback(self):
        pass

    def edit_mode_off_callback(self):
        pass


   
class ContextGlyph(BaseContextEditorBox):
    inactive_color = (1, 1, 1, 0)
    
    overlay_color_light = (.8, .8, .8, 1)
    overlay_color_dark  = (.8, .8, .8, 1)
    
    selected_color_light = (.7, .7, .7, 1)
    selected_color_dark  = (.7, .7, .7, 1)
    
    glyph_color_light = DEFAULTS["neighbor_color_light"]
    glyph_color_dark  = DEFAULTS["neighbor_color_dark"]

    glyph_color_edit_mode_light = DEFAULTS["edit_color_light"]
    glyph_color_edit_mode_dark  = DEFAULTS["edit_color_dark"]

    allow_delete = True

    def __init__(self, querry="n", font=None, parent=None, offset=0):
        super().__init__(parent=parent)
        self._set_font(font)
        self._set_querry(querry)

        self._x = 0
        self._y = self.current_font.info.descender
        self._height = self.current_font.info.ascender - self._y
        
        self.build_merz_layers()
        self.panel = ContextGlyphPopover(self)
        # self.offset = offset

    # ----------------------------------------
    # serializing helpers
    
    def as_dict(self):
        return {"querry": self._querry, "font": _get_font_string(self._font)}

    def _relative_font_path(self):
        if self.font:
            font_path = pathlib.Path(self.font.path)
            root_font_path = pathlib.Path(self.parent.font.path)
            return font_path.relative_to(root_font_path)
        else:
            return None

    # ----------------------------------------

    @property
    def current_font(self):
        return self.parent.font.asFontParts()

    @property
    def current_glyph(self):
        return self.parent.glyph

    # ----------------------------------------
    # geometry

    @property
    def width(self):
        return self.glyph.width


    # ----------------------------------------
    # querry

    @property
    def querry(self):
        return self._querry

    @querry.setter
    def querry(self, value):
        self._set_querry(value)
        self._glyph_changed()

    def _set_querry(self, value):
        querry = value.strip()
        name_querry, target_layer = self._split_name_and_layer(querry)
        name = self._resolve_name_querry(name_querry)
        self._querry = querry
        self._name = name
        self._target_layer = target_layer

    def _resolve_name_querry(self, name_querry):
        name = name_querry
        if CURRENT_GLYPH_TAG in name:
            name = self._resolve_current_glyph(name)
        if ROOT_GLYPH_TAG in name:
            name = self._resolve_root_glyph(name)
        return name

    def _split_name_and_layer(self, querry):
        if LAYER_NAME_TOKEN in querry:
            name, layer = querry.split(LAYER_NAME_TOKEN, 1)
        else:
            font = self.font or self.current_font
            name, layer = querry, font.defaultLayer.name
        return name, layer

    #------------------------------
    # querry key words:

    def _resolve_current_glyph(self, querry):
        return querry.replace(CURRENT_GLYPH_TAG, self.current_glyph.name)

    def _resolve_root_glyph(self, querry):
        root = self.current_glyph.name.split(".")[0]
        return querry.replace(ROOT_GLYPH_TAG, root)

    #------------------------------
    
    @property
    def name(self):
        return self._name

    @property
    def target_layer(self):
        return self._target_layer
            
    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._set_font(value)
        self._glyph_changed()
        # self.parent.save_data_to_global()

    def _set_font(self, value):
        if isinstance(value, str):
            self._font = None
            for f in AllFonts():
                if _get_font_string(f) == value:
                    self._font = f
                    break
        else:
            self._font = value

    @property
    def glyph(self):
        font = self.font or self.current_font
        
        name = self.name
        target_layer = self.target_layer
        if len(name) > 0 and name in font:
            glyph = font[name]
            if target_layer in font.layerOrder:
                glyph = glyph.getLayer(target_layer)
        else:
            glyph = RGlyph()
            glyph.width = 200
        return glyph
    
    # ----------------------------------------
    # merz

    @property
    def containers(self):
        return (self.background_layer, self.preview_layer)

    def build_merz_layers(self):
        self.background_layer = merz.Base(position=(self.x, self.y))
        self.glyph_layer = self.build_glyph_layer()
        self.box_layer = self.build_box_layer()
        self.background_layer.appendSublayer(self.box_layer)
        self.background_layer.appendSublayer(self.glyph_layer)
        self.hit_testing_layer = self.box_layer

        self.delete_button = self.background_layer.appendSymbolSublayer(
            name="delete",
            position=(10, self.height -10),
            imageSettings=dict(
                name="com.mathieureguer.ConTextEditor.deleteSymbol",
                size=(20, 20),
                acceptsHit=True,
                # alignment="topLeft"
            ),  
        )
        self.delete_button.setVisible(False)

        self.preview_layer = merz.Base(position=(self.x, self.y))
        self.glyph_layer_preview = self.build_glyph_layer()
        self.preview_layer.appendSublayer(self.glyph_layer_preview)

        self.update_colors()

    def build_box_layer(self):
        return merz.Rectangle(position=(0, 0),
                              size=(self.width, self.height),
                              fillColor=self.inactive_color)

    def build_glyph_layer(self):
        path = merz.Path(position=(0, -self.y))
        path.setPath(self.glyph.getRepresentation("merz.CGPath"))
        return path

    # ----------------------------------------
    # additional hit testing

    def is_delete_pressed(self, point):
        # thanks for the work around Tal.
        # print("delete testing")
        # offset_point = merz_counter_offset_pt(self.delete_button, point)
        # x, y = offset_point
        # rect = (x-50, y-50, 100, 100)
        # print("delete pos", self.delete_button.getPosition())
        # print("point", point)
        # print("offset point", offset_point)
        # print("rect", rect)
        # container = self.background_layer.getContainer()
        # hits = container.findSublayersIntersectedByRect(
        #             rect,
        #             onlyAcceptsHit=False,
        #             recurse=True
        #         )
        # print("hits", hits)
        # for h in hits:
        #     print(h)
        # print("done")
        # print("offset_point")
        x, y = point
        radius = 30
        absolute_x, absolute_y = merz_get_absolute_position(self.delete_button)
        if x-radius < absolute_x < x+radius and y-radius < absolute_y < y+radius:
            return True
        # print("testing del")
        # for x in range(-2000, 2000, 20):
        #     for y in range(-2000, 2000, 20):
        #         rect = (x-20, y-20, 40, 40)
        #         if self.delete_button.isContainedByRect(rect):
        #             print("intersect", x, y, "pos", self.delete_button.getPosition())

        # print(self.delete_button.isIntersectedByRect((*point, 50, 50)))
        # print(self.delete_button.isIntersectedByRect(rect))
        # other_rect = (0, 400, 400, 400)
        # print(self.delete_button.isIntersectedByRect(rect))

    # ----------------------------------------
    # mouse events

    def selected_callback(self):
        if inDarkMode():
            self.box_layer.setFillColor(self.selected_color_dark)
        else:
            self.box_layer.setFillColor(self.selected_color_light)
        if hasattr(self, "delete_button"):
            self.delete_button.setVisible(True)
        self.panel.open()

    def unselected_callback(self):
        self.box_layer.setFillColor(self.inactive_color)
        if hasattr(self, "delete_button"):
            self.delete_button.setVisible(False)
        self.panel.close()

    def overlayed_callback(self):
        if inDarkMode():
            self.box_layer.setFillColor(self.overlay_color_dark)
        else:
            self.box_layer.setFillColor(self.overlay_color_light)
        if hasattr(self, "delete_button"):
            self.delete_button.setVisible(True)

    def unoverlayed_callback(self):
        self.box_layer.setFillColor(self.inactive_color)
        if hasattr(self, "delete_button"):
            self.delete_button.setVisible(False)

    def edit_mode_on_callback(self):
        if inDarkMode():
            self.glyph_layer.setFillColor(self.glyph_color_edit_mode_dark)
        else:
            self.glyph_layer.setFillColor(self.glyph_color_edit_mode_light)

    def edit_mode_off_callback(self):
        if inDarkMode():
            self.glyph_layer.setFillColor(self.glyph_color_dark)
        else:
            self.glyph_layer.setFillColor(self.glyph_color_light)

    # ----------------------------------------
    # query events

    def _glyph_changed(self):
        self._update_glyph_path()
        self.parent.position_context()

    def _current_glyph_changed(self):
        # maybe this should always update everything?
        # layer can change...
        # self._update_glyph_path()
        if self.name == self.current_glyph.name:
            if self.target_layer == self.current_glyph.layer.name:
            # Glyph will get redrawn even if they are not on the same layer
                self._update_glyph_path()

    def _font_glyph_changed(self):
        if not self.font:
            self._update_glyph_path()

    def _glyph_editor_will_set_glyph(self):
        # reset the querry to get up to date dynamic name
        self._set_querry(self.querry)
        self._glyph_changed()

    def _update_glyph_path(self):
        p = self.glyph.getRepresentation("merz.CGPath")
        self.glyph_layer.setPath(p)
        self.glyph_layer_preview.setPath(p)
        self.box_layer.setSize((self.width, self.height))


    def update_colors(self):
        if inDarkMode():
            if self.edit_mode:
                self.glyph_layer.setFillColor(self.glyph_color_edit_mode_dark)
            else:
                self.glyph_layer.setFillColor(self.glyph_color_dark)
            self.glyph_layer_preview.setFillColor(getDefault("glyphViewPreviewFillColor.dark"))
        else:
            if self.edit_mode:
                self.glyph_layer.setFillColor(self.glyph_color_edit_mode_light)
            else:
                self.glyph_layer.setFillColor(self.glyph_color_light)            
            self.glyph_layer_preview.setFillColor(getDefault("glyphViewPreviewFillColor"))

class MaskContextGlyph(ContextGlyph):
    # overlay_color_light = (.8, .8, .8, 1)
    # overlay_color_dark  = (.8, .8, .8, 1)
    
    # selected_color_light = (.7, .7, .7, 1)
    # selected_color_dark  = (.7, .7, .7, 1)
    
    glyph_color_light =  DEFAULTS["mask_color_light"]
    glyph_color_dark  =  DEFAULTS["mask_color_dark"]
    # glyph_color_edit_mode_light =  (0, .6, .8, .5)
    # glyph_color_edit_mode_dark  =  (0, .6, .8, .5)
 
    @property
    def width(self):
        return self.current_glyph.width

    def _current_glyph_changed(self):
        self._update_glyph_path()

class ContextGlyphPopover():

    def __init__(self, parent):
        self.parent = parent
        self._update_font_dict()
        self.build()

    def build(self):
        self.panel = vanilla.Popover((120, 80))
        self.panel.name = vanilla.EditText(
            "auto", 
            self.parent.querry, 
            callback=self.name_callback
        )
        self.panel.font = vanilla.PopUpButton(
            "auto", 
            self.font_map.keys(), 
            callback=self.font_callback
        )

        rules = [
            "H:|-margin-[name(200)]-margin-|",
            "H:|-margin-[font]-margin-|",
            "V:|-margin-[name]-(8)-[font]-margin-|",
        ]
        metrics = {"margin":15}
        self.panel.addAutoPosSizeRules(rules, metrics)

    # ----------------------------------------

    def name_callback(self, sender):
        self.parent.querry = sender.get()

    def font_callback(self, sender):
        key = sender.getItem()
        self.parent.font = self.font_map[key]

    # ----------------------------------------
    
    def open(self):
        # update the font list
        self._udpate_font_popup()

        # position the popover
        glyph_view = CurrentGlyphWindow().getGlyphView()
        relative_bounds = self._get_glyph_view_relative_rect(self.parent.bounds, glyph_view)
        self.panel.open(parentView=glyph_view, preferredEdge='top', relativeRect=relative_bounds)

    def close(self):
        self.panel.close()

    # ----------------------------------------
    
    def _update_font_dict(self):
        self.font_map = {CURRENT_FONT_MENU_NAME: None} 
        for f in AllFonts():
            self.font_map[_get_font_string(f)] = f

    def _udpate_font_popup(self):
        # update the font list
        self._update_font_dict()
        self.panel.font.setItems(self.font_map.keys())
        item = _get_font_string(self.parent.font)
        if item in self.panel.font.getItems():
            self.panel.font.setItem(item)

    def _get_glyph_view_relative_rect(self, rect, glyph_view):
        x, y, w, h = rect
        x_view_offset, y_view_offset = glyph_view.offset()
        view_scale = glyph_view.scale()
        return (x + x_view_offset)*view_scale, (y + y_view_offset)*view_scale, w*view_scale, h*view_scale


class ContextAddButton(BaseContextEditorBox):
    inactive_color = (.8, .8, .8, 1)
    overlay_color = (.7, .7, .7, 1)

    stroke = 30
    margin = 50

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._x = 0
        self._y = 0
        self._height = self.parent.font.info.xHeight
        self._width = 350

        self.build_merz_layers()



    # ----------------------------------------
    # merz
    
    @property
    def containers(self):
        return [self.background_layer]    
    
    def get_plus_layer(self):
        
        size = min(self.width, self.height)
        size -= self.margin * 2
  
        x_0 = self.margin
        x_1 = (size-self.stroke)/2
        x_2 = x_1 + self.stroke
        x_3 = size - self.margin

        y_0 = self.margin
        y_1 = (size-self.stroke)/2
        y_2 = y_1 + self.stroke
        y_3 = size - self.margin

        plus = merz.Path()
        pen = plus.getPen()
        pen.oval((0, 0, size, size))
        pen.moveTo((x_1, y_0))
        pen.lineTo((x_1, y_1))
        pen.lineTo((x_0, y_1))
        pen.lineTo((x_0, y_2))
        pen.lineTo((x_1, y_2))
        pen.lineTo((x_1, y_3))
        pen.lineTo((x_2, y_3))
        pen.lineTo((x_2, y_2))
        pen.lineTo((x_3, y_2))
        pen.lineTo((x_3, y_1))
        pen.lineTo((x_2, y_1))
        pen.lineTo((x_2, y_0))
        pen.closePath()
        plus.setFillColor(self.inactive_color)
        plus.setPosition(((self.width-size)/2, (self.height-size)/2))
        return plus

    def build_merz_layers(self):
        self.background_layer = merz.Base(
            position=(self.x, self.y),
            size=(0, 0),
        )
        self.box_layer = self.background_layer.appendRectangleSublayer(
            position=(0, 0),
            size=(self.width, self.height),
            fillColor=(0, 0, 0, 0),
        )                                          
        self.plus_layer = self.get_plus_layer()
        self.background_layer.appendSublayer(self.plus_layer)
        self.set_visible(False)
      
        ## I could not get the hit box to work. 
        ## somehow the hit testing area seemed to drift 
        ## about 30 units toward the bottom left
        # size = min(self.width, self.height)
        # size -= self.margin * 2
        # hit_box = self.background_layer.appendRectangleSublayer(
        #     position=((self.width-size)/2, (self.height-size)/2),
        #     position=(50, 50),
        #     size=(size, size),
        #     fillColor =(1, 0, 0, .3)
        # )
 
        self.hit_testing_layer = self.box_layer

    def set_visible(self, value):
        self.background_layer.setVisible(value)

    # ----------------------------------------
    # mouse events

    def overlayed_callback(self):
        self.plus_layer.setFillColor(self.overlay_color)

    def unoverlayed_callback(self):
        self.plus_layer.setFillColor(self.inactive_color)

    def selected_callback(self):
        self.plus_layer.setFillColor(self.inactive_color)


class RightContextAddButton(ContextAddButton):
    def selected_callback(self):
        self.plus_layer.setFillColor(self.inactive_color)
        self.parent.new_glyph_to_right_context()


class LeftContextAddButton(ContextAddButton):
    def selected_callback(self):
        self.plus_layer.setFillColor(self.inactive_color)
        self.parent.new_glyph_to_left_context()


# ----------------------------------------
# symbol factories
# ----------------------------------------

from merz.tools.drawingTools import NSImageDrawingTools

def deleteButtonFactory(
        size,
        margin_ratio=.15,
        stroke_ratio=.15,
        color=(.5, .5, .5, 1),
        **kwargs
    ):

    size = (max(size), max(size))
    width, height = size
    
    bot = NSImageDrawingTools((width, height))
    bot.fill(*color)
    bot.rotate(45, (width/2, height/2))
    
    # draw a circle
    # i think I have to draw it by hand
    # in order for it to be in the same bez path as the crosss
    r = .275
    p = bot.BezierPath()
    p.moveTo((0, height/2))
    p.curveTo((0, height/2+height*r), (width/2-width*r, height), (width/2, height))
    p.curveTo((width/2+width*r, height), (width, height/2+height*r), (width, height/2))
    p.curveTo((width, height/2-height*r), (width/2+width*r, 0), (width/2, 0))
    p.curveTo((width/2-width*r, 0), (0, height/2-height*r), (0, height/2))
    p.closePath()
    
    # now the cross
    stroke = width * stroke_ratio
    margin = width*margin_ratio
        
    x_0 = margin
    x_1 = (width-stroke)/2
    x_2 = x_1 + stroke
    x_3 = width - margin
    y_0 = margin
    y_1 = (height-stroke)/2
    y_2 = y_1 + stroke
    y_3 = height - margin
    
    p.moveTo((x_2, y_0))
    p.lineTo((x_2, y_1))
    p.lineTo((x_3, y_1))
    p.lineTo((x_3, y_2))
    p.lineTo((x_2, y_2))
    p.lineTo((x_2, y_3))
    p.lineTo((x_1, y_3))
    p.lineTo((x_1, y_2))
    p.lineTo((x_0, y_2))
    p.lineTo((x_0, y_1))
    p.lineTo((x_1, y_1))
    p.lineTo((x_1, y_0))
    p.closePath()
    bot.drawPath(p)

    return bot.getImage()

merz.SymbolImageVendor.registerImageFactory("com.mathieureguer.ConTextEditor.deleteSymbol", deleteButtonFactory)

# ----------------------------------------
# controller
# ----------------------------------------

RIGHT_CONTEXT_LIB_KEY = DEFAULT_KEY + ".right_context"
MASK_CONTEXT_LIB_KEY = DEFAULT_KEY + ".mask_context"
LEFT_CONTEXT_LIB_KEY = DEFAULT_KEY + ".left_context"

class ContextDisplaySubscriber(Subscriber):
    debug = True
    # global_left_context = [DEFAULT_CONTEXT_DICT]
    # global_mask_context = [DEFAULT_CONTEXT_DICT]
    # global_right_context = [DEFAULT_CONTEXT_DICT]

    def build(self):
        self.settings_manager = ExtentionSettingsManager(self, DEFAULT_KEY)
        self.settings_manager.register_extention_defaults(DEFAULTS)
        self.settings_manager.load_extention_settings()

        self._edit_mode = False
        self.left_add_button = LeftContextAddButton(self)
        self.right_add_button = RightContextAddButton(self)
        
        glyphEditor = self.getGlyphEditor()
        self.container_background = glyphEditor.extensionContainer(
            identifier="com.mathieureguer.contextEditor.background",
            location="background",
            clear=True
        )

        self.container_preview = glyphEditor.extensionContainer(
            identifier="com.mathieureguer.contextEditor.background",
            location="preview",
            clear=True
        )

        self.build_context()
        self.position_context()
        self.colorize_context()

    def destroy(self):
        self.save_context_to_font_lib()
        self.clear_context()

    # ----------------------------------------
    ## this is used for persistent context shared accross all subscribers
    
    # def populate_right_context_from_global(self):
    #     self.right_context = []
    #     for glyph_data in ContextDisplaySubscriber.global_right_context:
    #         self._add_glyph_box_to_right_context(glyph_data)

    # def populate_left_context_from_global(self):
    #     self.left_context = []
    #     for glyph_data in ContextDisplaySubscriber.global_left_context:
    #         self._add_glyph_box_to_left_context(glyph_data)

    # def populate_mask_context_from_global(self):
    #     self.mask_context = []
    #     for glyph_data in ContextDisplaySubscriber.global_mask_context:
    #         self._add_glyph_box_to_mask_context(glyph_data)

    # def save_data_to_global(self):
    #     """
    #     This is probably overly complex, should be an event
    #     """
    #     ContextDisplaySubscriber.global_left_context = [c.as_dict() for c in self.left_context]
    #     ContextDisplaySubscriber.global_mask_context = [c.as_dict() for c in self.mask_context]
    #     ContextDisplaySubscriber.global_right_context = [c.as_dict() for c in self.right_context]

    #     for s in getActiveSubscriberByClass(ContextDisplaySubscriber):
    #         s.build_context()
    #         s.position_context()

    # ----------------------------------------
    
    def save_context_to_font_lib(self):
        self.font.lib[RIGHT_CONTEXT_LIB_KEY] = [context.as_dict() for context in self.right_context]
        self.font.lib[MASK_CONTEXT_LIB_KEY] = [context.as_dict() for context in self.mask_context]
        self.font.lib[LEFT_CONTEXT_LIB_KEY] = [context.as_dict() for context in self.left_context]


    def _validate_data_with_default(self, data):
        validated_data = DEFAULT_CONTEXT_DICT.copy()
        mutual_keys = data.keys() & DEFAULT_CONTEXT_DICT.keys()
        for k in mutual_keys:
            validated_data[k] = data[k]
        return validated_data

    def populate_context_from_lib(self):

        self.right_context = []
        if RIGHT_CONTEXT_LIB_KEY in self.font.lib:
            for glyph_data in self.font.lib[RIGHT_CONTEXT_LIB_KEY]:
                glyph_data = self._validate_data_with_default(glyph_data)
                self._add_glyph_box_to_right_context(glyph_data)
        else:
            self._add_glyph_box_to_right_context(DEFAULT_CONTEXT_DICT)

        self.mask_context = []
        if MASK_CONTEXT_LIB_KEY in self.font.lib:
            for glyph_data in self.font.lib[MASK_CONTEXT_LIB_KEY]:
                glyph_data = self._validate_data_with_default(glyph_data)
                self._add_glyph_box_to_mask_context(glyph_data)
        else:
            self._add_glyph_box_to_mask_context(DEFAULT_CONTEXT_DICT)

        self.left_context = []
        if MASK_CONTEXT_LIB_KEY in self.font.lib:
            for glyph_data in self.font.lib[LEFT_CONTEXT_LIB_KEY]:
                glyph_data = self._validate_data_with_default(glyph_data)
                self._add_glyph_box_to_left_context(glyph_data)
        else:
            self._add_glyph_box_to_left_context(DEFAULT_CONTEXT_DICT)

    # ----------------------------------------
    
    def delete_selected_box(self):
        for context in [self.left_context, self.right_context]:
            for i, box in enumerate(context):
                if box.selected:
                    del context[i]
        self.save_context_to_font_lib()
        self.build_context()
        self.position_context()


    # ----------------------------------------
    
    @property
    def edit_mode(self):
        return self._edit_mode


    @edit_mode.setter
    def edit_mode(self, value):
        self._edit_mode = value
        if value == False:
            for box in [*self.left_context, *self.mask_context, *self.right_context]:
                box.selected = False
                box.overlayed = False
                box.edit_mode = False
        else:
            for box in [*self.left_context, *self.mask_context, *self.right_context]:
                box.edit_mode = True
        self.left_add_button.set_visible(value)
        self.right_add_button.set_visible(value)

    # ----------------------------------------
    
    @property
    def font(self):
        return self.glyph.font

    @property
    def glyph(self):
        return self.getGlyphEditor().getGlyph()
    

    # ----------------------------------------
    
    def glyphEditorWillSetGlyph(self, info):
        for box in [
            *self.left_context, 
            *self.mask_context, 
            *self.right_context
            ]:
                # box._font_glyph_changed()
                box._glyph_editor_will_set_glyph()
                # box._current_glyph_changed()
        self.position_context()

    def glyphEditorDidMouseMove(self, info):
        if self.edit_mode:
            point = info["locationInGlyph"]
            for box in [
                self.left_add_button, 
                *self.left_context, 
                *self.mask_context, 
                *self.right_context, 
                self.right_add_button
                ]:
                if box.selected == False:
                    if box.is_point_inside(point):
                        box.overlayed = True
                    else:
                        box.overlayed = False

    def glyphEditorDidMouseDown(self, info):
        if self.edit_mode:
            point = info["locationInGlyph"]
            for box in [
                self.left_add_button, 
                *self.left_context, 
                *self.mask_context, 
                *self.right_context, 
                self.right_add_button
                ]:
                if box.is_point_inside(point):
                    if box.allow_delete and box.is_delete_pressed(point):
                        box._selected = True
                        self.delete_selected_box()
                        box.selected = False
                    else:                     
                        box.selected = True
                else:
                    box.selected = False

    def glyphEditorDidKeyDown(self, info):
        if self.edit_mode:
            DELETE_KEY = '\x7f'
            if info["deviceState"]["keyDown"]== DELETE_KEY:
                self.delete_selected_box()

    glyphEditorGlyphDidChangeDelay = 0
    def glyphEditorGlyphDidChange(self, info):
        for box in [*self.left_context, *self.mask_context, *self.right_context]:
            box._current_glyph_changed()
            # box._glyph_editor_will_set_glyph()

    glyphEditorGlyphDidChangeMetricsDelay = 0
    def glyphEditorGlyphDidChangeMetrics(self, info):
        self.position_context()

    def roboFontAppearanceChanged(self, info):
        for context in self.left_context + self.right_context:
            context.update_colors()

    def roboFontDidChangePreferences(self, info):
        for context in self.left_context + self.right_context:
            context.update_colors()

    # ----------------------------------------
    
    def contexteditorDidChangeSettings(self, info):
        self.settings_manager.load_extention_settings()
        self.colorize_context()

    def colorize_context(self):
        ContextGlyph.glyph_color_light = self.settings_manager["neighbor_color_light"]
        ContextGlyph.glyph_color_dark  = self.settings_manager["neighbor_color_dark"]
        ContextGlyph.glyph_color_edit_mode_light = self.settings_manager["edit_color_light"]
        ContextGlyph.glyph_color_edit_mode_dark  = self.settings_manager["edit_color_dark"]
        MaskContextGlyph.glyph_color_light = self.settings_manager["mask_color_light"]
        MaskContextGlyph.glyph_color_dark  = self.settings_manager["mask_color_dark"]
        MaskContextGlyph.glyph_color_edit_mode_light = self.settings_manager["edit_color_light"]
        MaskContextGlyph.glyph_color_edit_mode_dark  = self.settings_manager["edit_color_dark"]

        for box in self.left_context + self.mask_context + self.right_context:
            box.update_colors()

    # ----------------------------------------

    def build_context(self):
        self.clear_context()
        self.populate_context_from_lib()

        for box in self.left_context:
            self.container_background.appendSublayer(box.background_layer)
            self.container_preview.appendSublayer(box.preview_layer)

        for box in self.mask_context:
            self.container_background.appendSublayer(box.background_layer)

        for box in self.right_context:
            self.container_background.appendSublayer(box.background_layer)
            self.container_preview.appendSublayer(box.preview_layer)

        self.container_background.appendSublayer(self.left_add_button.background_layer) 
        self.container_background.appendSublayer(self.right_add_button.background_layer)

    def position_context(self):
        self.position_left_context()
        self.position_right_context()

    def position_left_context(self):
        current_offset = 0
        for box in [*self.left_context, self.left_add_button]:
            current_offset -= box.width
            box.x = current_offset

    def position_right_context(self):
        current_offset = self.glyph.width
        for box in [*self.right_context, self.right_add_button]:
            box.x = current_offset
            current_offset += box.width

    def clear_context(self):
        self.container_background.clearSublayers()
        self.container_preview.clearSublayers()

    # ----------------------------------------
    # glyph box are stored in parrallel in a set of class variable
    # in order to share them across subscribers 
    # and preserve then when subscribers are unregistered

    def new_glyph_to_right_context(self):
        box = self.add_glyph_to_right_context(DEFAULT_CONTEXT_DICT)
        # box.querry = "n"
        box.selected = True

    def new_glyph_to_left_context(self):
        box = self.add_glyph_to_left_context(DEFAULT_CONTEXT_DICT)
        # box.querry = "n"
        box.selected = True
    
    def add_glyph_to_right_context(self, glyph_data):
        # global_right_context.append(glyph_data)
        box = self._add_glyph_box_to_right_context(glyph_data)
        self.container_background.appendSublayer(box.background_layer)
        self.container_preview.appendSublayer(box.preview_layer)
        self.position_right_context()
        return box

    def add_glyph_to_left_context(self, glyph_data):
        # global_left_context.append(glyph_data)
        box = self._add_glyph_box_to_left_context(glyph_data)
        self.container_background.appendSublayer(box.background_layer)
        self.container_preview.appendSublayer(box.preview_layer)
        self.position_left_context()
        return box

    def add_glyph_to_mask_context(self, glyph_data):
        # global_mask_context.append(glyph_data)
        box = self._add_glyph_box_to_left_context(glyph_data)
        self.container_background.appendSublayer(box.background_layer)
        self.container_preview.appendSublayer(box.preview_layer)
        self.position_left_context()

    def _add_glyph_box_to_right_context(self, glyph_data):
        box = ContextGlyph(parent=self, **glyph_data)
        box.edit_mode = self.edit_mode
        self.right_context.append(box)
        return box
        
    def _add_glyph_box_to_left_context(self, glyph_data):
        box = ContextGlyph(parent=self, **glyph_data)
        box.edit_mode = self.edit_mode
        self.left_context.append(box)
        return box

    def _add_glyph_box_to_mask_context(self, glyph_data):
        box = MaskContextGlyph(parent=self, **glyph_data)
        self.mask_context = [box]
        return box

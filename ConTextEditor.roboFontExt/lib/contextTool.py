from context import ContextDisplaySubscriber, toggleSubscriberClass, toggleSubscriberClassOn, toggleSubscriberClassOff, getActiveSubscriberByClass

from mojo.subscriber import *
from mojo.events import BaseEventTool, installTool
from mojo.UI import CurrentGlyphWindow
from mojo.extensions import ExtensionBundle
from lib.UI.toolbarGlyphTools import ToolbarGlyphTools

# from AppKit import NSImage, NSImageNameAdvanced, NSImageNameFontPanel

# ----------------------------------------

bundle = ExtensionBundle("ConTextEditor")
toggle_icon = bundle.getResourceImage("toggleButton")
edit_icon = bundle.getResourceImage("editButton")

class ContextEditTool(BaseEventTool):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.left_context = []
        self.mask_context = []
        self.right_context = []

    def getToolbarTip(self):
        return "ConText Editor"

    def becomeActive(self):
        self.contextSubscriber = toggleSubscriberClassOn(ContextDisplaySubscriber, registerGlyphEditorSubscriber)
        for c in getActiveSubscriberByClass(ContextDisplaySubscriber):
            c.edit_mode = True

    def becomeInactive(self):
        # changing all subscriber here, not sure I can acess a subscriber specific to 
        for c in getActiveSubscriberByClass(ContextDisplaySubscriber):
            c.edit_mode = False
        # toggleSubscriberClassOff(ContextDisplaySubscriber, unregisterGlyphEditorSubscriber)

    def getToolbarIcon(self):
        return edit_icon
        # icon = NSImage.alloc().initByReferencingFile_(str(EDIT_ICON_PATH))
        # if icon :
        #     return icon 

# ----------------------------------------

class AddToolbarToggleButton(Subscriber):
    debug = True


    def glyphEditorWantsToolbarItems(self, info):

        # create the button
        view = ToolbarGlyphTools((30, 25), [dict(image=toggle_icon, toolTip="Toggle ConText")], trackingMode="one")

        newItem = {'itemIdentifier': 'ToggleConText',
                   'label':          'ConText',
                   'toolTip':        'Toggle ConText',
                   'view':           view,
                   'callback':        self.toggle_callback}


        # add it to the toolbar
        info['itemDescriptions'].insert(1, newItem)
        
    def toggle_callback(self, sender):
        toggleSubscriberClass(ContextDisplaySubscriber, registerGlyphEditorSubscriber)

# ----------------------------------------

installTool(ContextEditTool())
registerRoboFontSubscriber(AddToolbarToggleButton)


from context import ContextDisplaySubscriber, toggleSubscriberClass, toggleSubscriberClassOn, toggleSubscriberClassOff, getActiveSubscriberByClass
from contextEvent import register_custom_event

from mojo.subscriber import *
from mojo.events import BaseEventTool, installTool, setActiveEventTool
from mojo.UI import CurrentGlyphWindow
from mojo.extensions import ExtensionBundle
from lib.UI.toolbarGlyphTools import ToolbarGlyphTools


from contextInstanceCollector import ContextInstanceCollector, contextAllInstances
import builtins

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
        icons = [
            dict(image=toggle_icon, toolTip="Toggle ConText"),
            dict(image=edit_icon, toolTip="Edit ConText")
            ]
        toolbar_view = ToolbarGlyphTools((60, 25), icons, trackingMode="one")
        # edit_view = ToolbarGlyphTools((30, 25), [dict(image=edit_icon, toolTip="Edit ConText")], trackingMode="one")


        toolbar_item = {'itemIdentifier': 'ConText',
                      'label':          'ConText',
                      'toolTip':        'ConText',
                      'view':           toolbar_view,
                      'callback':       self.toolbar_callback}

        # edit_item = {'itemIdentifier': 'EditConText',
        #             'label':          'Edit ConText',
        #             'toolTip':        'Edit ConText',
        #             'view':           edit_view,
        #             'callback':       self.edit_callback}


        # add it to the toolbar
        info['itemDescriptions'].insert(1, toolbar_item)
        # info['itemDescriptions'].insert(1, edit_item)

        
    def toolbar_callback(self, sender):
        """distribute the callabcks based on segment pressed"""
        callbacks = [self.toggle_callback, self.edit_callback]
        selected = sender.selectedSegment()
        callbacks[selected](sender)

    def toggle_callback(self, sender):
        toggleSubscriberClass(ContextDisplaySubscriber, registerGlyphEditorSubscriber)

    def edit_callback(self, sender):
        setActiveEventTool("ContextEditTool")

# ----------------------------------------

installTool(ContextEditTool())
registerRoboFontSubscriber(AddToolbarToggleButton)
registerRoboFontSubscriber(ContextInstanceCollector)    
builtins.ContextAllInstances = contextAllInstances


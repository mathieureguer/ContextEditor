from context import ContextDisplaySubscriber, toggleSubscriberClassOn, toggleSubscriberClassOff, getActiveSubscriberByClass
from mojo.subscriber import *
from mojo.events import BaseEventTool, installTool
from mojo.UI import CurrentGlyphWindow

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
            print(c.getGlyphEditor())
            print(CurrentGlyphWindow())
            print("------")
            c.edit_mode = True

    def becomeInactive(self):
        # changing all subscriber here, not sure I can acess a subscriber specific to 
        for c in getActiveSubscriberByClass(ContextDisplaySubscriber):
            c.edit_mode = False
        # toggleSubscriberClassOff(ContextDisplaySubscriber, unregisterGlyphEditorSubscriber)


installTool(ContextEditTool())



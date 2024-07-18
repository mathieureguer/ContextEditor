from context import ContextDisplaySubscriber, toggleSubscriberClass, DEFAULT_KEY
from mojo.subscriber import *

#------------------------------

if __name__ == '__main__':
    toggleSubscriberClass(ContextDisplaySubscriber, registerGlyphEditorSubscriber)

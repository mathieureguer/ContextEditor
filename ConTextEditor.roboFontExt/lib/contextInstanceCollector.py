from mojo.subscriber import Subscriber
import lib.fontObjects.fontPartsWrappers
import builtins

"""
this is quite dodgy, I am not sure the pattern I use here is the cleanest thing.
"""

_contextInstanceCollector = []

class ContextInstanceCollector(Subscriber):

    debug = True
    def build(self):
        # collect already opened designspace
        try:
            for ds in AllDesignspaces():
                for i in ds.instances:
                    instance = ContextInstance(ds, i)
                    _contextInstanceCollector.append(instance)
        except:
            print("DesignSpaceEditor is not installed")

    def designspaceEditorDidOpenDesignspace(self, info):
        ds = info["designspace"]
        for i in ds.instances:
            instance = ContextInstance(ds, i)
            _contextInstanceCollector.append(instance)

    def designspaceEditorDidCloseDesignspace(self, info):
        ds = info["designspace"]
        delete_this = []
        for index, instance in enumerate(_contextInstanceCollector):
            if instance.designspace == ds:
                delete_this.append(index)
                instance.close()
        for index in reversed(delete_this):
            del _contextInstanceCollector[index]

    def destroy(self):
        # I am not sure why I need the global statement here
        global _contextInstanceCollector
        for f in _contextInstanceCollector:
            f.close()
        _contextInstanceCollector = []

            
class ContextInstance(lib.fontObjects.fontPartsWrappers.RFont):
    
    familyName_preffix = "~ "
    
    def __init__(self, ds, instance_descriptor):
        super().__init__(showInterface=False)
        self.designspace = ds
        self.descriptor = instance_descriptor
        info = ds.makeOneInfo(instance_descriptor.location, roundGeometry=True)
        info.extractInfo(self.info)
        self.info.familyName = self.familyName_preffix + self.descriptor.familyName
        self.info.styleName = self.descriptor.styleName
    
    # def __getitem__(self, name):
    #     if name in self.naked()._glyphSet:
    #         return self.naked()._glyphSet[name]
    #     else:
    #         mutated = self.designspace.makeOneGlyph(name, self.descriptor.location, roundGeometry=True)
    #         glyph = self.newGlyph(name)
    #         mutated.extractGlyph(glyph.naked())
    #         print("glyph", glyph.width)
    #         print("mutated", mutated.width)
    #         glyph.width = mutated.width
    #         return glyph

    def mutate_glyph(self, name):
        mutated = self.designspace.makeOneGlyph(name, self.descriptor.location, roundGeometry=True)
        glyph = self.newGlyph(name)
        mutated.extractGlyph(glyph.naked())
        # glyph.width = mutated.width
        return glyph

    def get_glyph(self, name):
        if name in self.keys():
            return self[name]
        elif name in self.source_keys():
            return self.mutate_glyph(name)
        else:
            return None

    def source_keys(self):
        source = self.designspace.findDefault()
        font = self.designspace.fonts.get(source.name)
        return font.keys()


def contextAllInstances():
    return _contextInstanceCollector
    

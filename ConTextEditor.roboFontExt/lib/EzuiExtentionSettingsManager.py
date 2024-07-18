import plistlib
from collections import UserDict

import ezui
from mojo.extensions import getExtensionDefault, setExtensionDefault

#------------------------------

INDEX_BASED_GETSET = [ezui.PopUpButton]

#------------------------------

class PrefixedDict(UserDict):
    """
    a user dictionary to handle prefixed keys somewhat gracefully  
    """
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix
        
    @property
    def prefixed_data(self):
        return {self.prefix + key : value for key, value in self.data.items()}

    def load_prefixed_data(self, prefixed_data):
        for prefixed_key, value in prefixed_data.items():
            key = self._strip_prefixed_key(prefixed_key)
            self.data[_strip_prefixed_key]

    def _strip_prefixed_key(self, prefixed_key):
        assert prefixed_key.startswith(self.prefix), f"{prefixed_key} key does not start with registerted prefix {self.prefix}"
        return prefixed_key[len(self.prefix):]



class ExtentionSettingsManager(PrefixedDict):
    """
    Deals with an extention defaults.
    Keep track of the registered keys, can return all settings of an extention as dict
    Can import and export dict presets as xml
    """

    def __init__(self, controller, prefix):
        super().__init__(prefix)
        self.controller = controller
        self._input_map = {} 

    # ----------------------------------------
    # extention defaults

    def register_extention_defaults(self, data):

        for key, value in data.items():
            self[key] = value

        # import registerExtensionsDefaults work-around (ripped off from Tal Lemming)
        try:
            from mojo.extensions import registerExtensionsDefaults
        except ImportError:
            def registerExtensionsDefaults(d):
                for k, v in self.prefixed_data.items():
                    e = getExtensionDefault(k, fallback="__fallback__")
                    if e == "__fallback__":
                        setExtensionDefault(k, v)
        registerExtensionsDefaults(self.prefixed_data)

    def save_extention_settings(self):
        for key, value in self.prefixed_data.items():
            setExtensionDefault(key, value)

    def load_extention_settings(self, fallback=None):
        settings = {}
        for prefixed_key in self.prefixed_data.keys():
            settings[self._strip_prefixed_key(prefixed_key)] = getExtensionDefault(prefixed_key, fallback=None)
        self.data.update(settings)

    # ----------------------------------------
    # ezui helpers

    def register_input(self, identifier):
        obj = self.controller.w.getItem(identifier)
        self._input_map[identifier] = obj

    def register_input_default(self, identifier, value):
        obj = self.controller.w.getItem(identifier)
        self._input_map[identifier] = obj
        self._set_input_value(obj, value)

    def udpate_settings_from_input(self):
        for key, input_object in self._input_map.items():
            self[key] = self._get_input_value(input_object)

    def set_input_from_settings(self):
        for key, input_object in self._input_map.items():
            if key in self.keys():
                self._set_input_value(input_object, self[key])

    def _get_input_value(self, input_object):
        # data formating could / should happen here
        if type(input_object) in INDEX_BASED_GETSET:
            return input_object.getitems()[input_object.get()]
        else:
            return input_object.get()

    def _set_input_value(self, input_object, value):
        # data formating could / should happen here
        if type(input_object) in INDEX_BASED_GETSET:
            index = input_object.getItems().index(value)
            input_object.set(index)
        else:
            input_object.set(value)

    # ----------------------------------------
    # Import Export

    def to_plist(self, prefixed=True):
        if prefix_key:
            out_data = self.prefixed_data
        else:
            out_data = self.data
        return plistlib.writePlistToString(out_data)

    def from_plist(self, plist, prefixed=True):
        raw_data = plistlib.readPlistFromString(plist)
        if prefixed:
            self.load_prefixed_data(raw_data)
        else:
            self.data.update(raw_data)

    def write_preset(self, dict, path, prefixed=True):
        with open(path, "w+") as f:
            f.write(self.to_plist(prefixed=prefixed))

    def read_preset(self, path, prefixed=True):
        with open(path, "r") as f:
            plist = f.read()
            self.from_plist(plist, prefixed=prefixed)
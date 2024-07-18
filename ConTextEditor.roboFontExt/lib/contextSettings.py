import ezui

from EzuiExtentionSettingsManager import ExtentionSettingsManager
from mojo.events import postEvent


from context import DEFAULTS, DEFAULT_KEY

#------------------------------

COLOR_WIDTH  = 75
COLOR_HEIGHT = 30

class ContextSettingsPanel(ezui.WindowController):

    def build(self):

        content = """
        * HorizontalStack
        > Light @light_label
        > Dark  @dark_label
        * HorizontalStack
        > * ColorWell @neighbor_color_light 
        > * ColorWell @neighbor_color_dark
        > Neighbor Color
        * HorizontalStack
        > * ColorWell @mask_color_light
        > * ColorWell @mask_color_dark
        > Mask Color
        * HorizontalStack
        > * ColorWell @edit_color_light
        > * ColorWell @edit_color_dark
        > Edit Color
        """
    
        description_data = dict(
            light_label=dict(
                width=COLOR_WIDTH,
            ),
            neighbor_color_light=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(1, 0, 0, 1),
                callback=self.color_settings_callback
            ),
            neighbor_color_dark=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(0, 1, 0, 1),
                callback=self.color_settings_callback
            ),
            mask_color_light=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(1, 0, 0, 1),
                callback=self.color_settings_callback
            ),
            mask_color_dark=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(1, 0, 0, 1),
                callback=self.color_settings_callback
            ),
            edit_color_light=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(1, 0, 0, 1),
                callback=self.color_settings_callback
            ),
            edit_color_dark=dict(
                width=COLOR_WIDTH,
                height=COLOR_HEIGHT,
                color=(1, 0, 0, 1),
                callback=self.color_settings_callback
            ),

        )

        self.w = ezui.EZWindow(
            title="ConTextEditor Settings",
            content=content,
            controller=self,
            descriptionData=description_data,
        )

        self.settings_manager = ExtentionSettingsManager(self, DEFAULT_KEY)
        self.settings_manager.register_extention_defaults(DEFAULTS)

        self.settings_manager.register_input("neighbor_color_light")
        self.settings_manager.register_input("neighbor_color_dark")
        self.settings_manager.register_input("mask_color_light")
        self.settings_manager.register_input("mask_color_dark")
        self.settings_manager.register_input("edit_color_light")
        self.settings_manager.register_input("edit_color_dark")

        self.settings_manager.load_extention_settings()
        self.settings_manager.set_input_from_settings()

    def started(self):
        self.w.open()

    def color_settings_callback(self, sender):
        self.settings_manager.udpate_settings_from_input()
        self.settings_manager.save_extention_settings()
        postEvent(f"{DEFAULT_KEY}.changed")


#------------------------------

if __name__ == '__main__':

    
    OpenWindow(ContextSettingsPanel)
import re
import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.ui.dialog import dialogmode

MsgBoxThemes = {
    'basic':
        Theme([
            Style('underline', 'Base3', 'Base02', underline=True),
            Style('separator', 'LightBlue', 'Base02', nowrap=False),
            Style('button', 'LightBlue', 'Base02', nowrap=True),
            Style('button.shortcut', 'LightBlue', 'Base02', underline=True,
                   nowrap=True),
        ]),
}

class MsgBoxMode(dialogmode.DialogMode):
    autoshrink = True
    SEPARATOR = '/'
    USE_UNDO = False

    def init_themes(self):
        super().init_themes()
        self.themes.append(MsgBoxThemes)

    def init_keybind(self):
        pass

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.CURSOR_TO_MIDDLE_ON_SCROLL = False

    def on_str(self, wnd, s):
        pass

    def on_start(self, wnd):
        wnd.cursor.setpos(self.document.endpos()-1)

    def on_str(self, wnd, s):
        for c in s:
            c = c.lower()
            if c in self.shortcuts:
                self.on_shortcut(wnd, c)
                return
            if self.keys and (c in self.keys):
                self.on_shortcut(wnd, c)
                return

    def on_shortcut(self, wnd, c):
        # return value
        if c:
            c = c.lower()
        try:
            self._runcallback(c)
        finally:
            # Destroy popup window
            if wnd:
                popup = wnd.get_label('popup')
                if popup:
                    popup.destroy()

    def _runcallback(self, c):
        if self.callback:
            self.callback(c)

    def on_esc_pressed(self, wnd, event):
        super().on_esc_pressed(wnd, event)
        self.on_shortcut(wnd, None)

    def _show_window(self):
        kaa.app.show_dialog(self.document)

    @classmethod
    def build_msgbox(cls, caption, options, callback, keys=None):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        mode.callback = callback
        mode.keys  = keys
        doc.setmode(mode)

        f = dialogmode.FormBuilder(doc)

        # caption
        if caption:
            f.append_text('caption', caption)
            f.append_text('default', ' ')

        mode.shortcuts = {}
        for n, option in enumerate(options):
            m = re.search(r'&([^&])', option)
            shortcut = m.group(1)
            mode.shortcuts[shortcut.lower()] = option

            f.append_text('button',
                          option,
                          on_shortcut=
                            lambda wnd, key=shortcut:mode.on_shortcut(wnd, key),
                          shortcut_style='button.shortcut')

            if n < len(options)-1:
                f.append_text('separator', cls.SEPARATOR)

        f.append_text('default', ' ')
        f.append_text('underline', ' ')

        return doc

    @classmethod
    def show_msgbox(cls, caption, options, callback, keys=None):
        doc = cls.build_msgbox(caption, options, callback, keys)
        doc.mode._show_window()
        return doc

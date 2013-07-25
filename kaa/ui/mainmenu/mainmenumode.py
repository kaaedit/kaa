import kaa
from kaa.ui.msgbox import msgboxmode


class MenuMode(msgboxmode.MsgBoxMode):
    SEPARATOR = '/'

    @classmethod
    def build_menu(cls, wnd, items):
        doc = cls.build_msgbox('', [item for (item, commandids) in items], None)
        doc.mode.items = dict(items)
        doc.mode.target = wnd
        return doc

    def close(self):
        super().close()
        self.target = None

    def _runcallback(self, c):
        if not c:
            kaa.app.pop_menu()
        else:
            item = self.shortcuts[c]
            commandids = self.items[item]
            self.target.document.mode.on_commands(self.target, commandids)

class MainMenuMode(MenuMode):
    @classmethod
    def build(cls, wnd):
        return cls.build_menu(wnd,
           (('&File', ('menu.file',)),
            ('&Edit', ('menu.edit',)),
            ('&Macro', ('menu.macro',)),
            ('&Window', ('menu.window',)))
        )

class FileMenuMode(MenuMode):
    @classmethod
    def build(cls, wnd):
        return cls.build_menu(wnd,
           (('&New', ('file.new',)),
            ('&Open', ('file.open',)),
            ('&Save', ('file.save',)),
            ('Save &As', ('file.saveas',)),
            ('&Close', ('file.close',)),
            ('&Quit', ('file.quit',)))
        )

class EditMenuMode(MenuMode):
    @classmethod
    def build(cls, wnd):
        return cls.build_menu(wnd,
           (('&Cut', ('edit.cut',)),
            ('C&opy', ('edit.copy',)),
            ('&Paste', ('edit.paste',)),
            ('&Undo', ('edit.undo',)),
            ('&Redo', ('edit.redo',)))
        )


class MacroMenuMode(MenuMode):
    @classmethod
    def build(cls, wnd):
        return cls.build_menu(wnd,
           (('&Start Record', ('macro.start-record',)),
            ('&End Record', ('macro.end-record',)),
            ('&Run Macro', ('macro.run',)))
        )

class WindowMenuMode(MenuMode):
    @classmethod
    def build(cls, wnd):
        return cls.build_menu(wnd,
           (('&Frame list', ('app.show-framelist',)),
            ('Split &vert', ('editor.splitvert',)),
            ('Split &horz', ('editor.splithorz',)),
            ('&Move separator', ('editor.moveseparator',)),
            ('&Next window', ('editor.nextwindow',)),
            ('&Join window', ('editor.joinwindow',)),
            ('&Switch file', ('editor.switchfile',)),
           )
        )


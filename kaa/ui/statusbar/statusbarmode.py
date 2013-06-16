import kaa
from kaa.filetype.default import modebase
from kaa.theme import Theme, Style

class StatusInfo:
    updated = False
    def __init__(self):
        self.infos = {
            'filename':'',
            'modified_mark':'',
        }

    def set_info(self, **values):
        ret = False
        for name, value in values.items():
            updated = True
            if name in self.infos:
                if value == self.infos[name]:
                    updated = False

            self.infos[name] = value

            self.updated = self.updated or updated
            ret = ret or updated
        return ret

    def get_info(self, name, default=None):
        return self.infos.get(name, default)



StatusBarTheme = Theme('default', [
    Style('default', 'red', 'cyan', False, False),
    Style('filename', 'magenta', 'cyan'),
    Style('msg', 'default', 'default'),
])


class StatusBarMode(modebase.ModeBase):
    STATUSBAR_MESSAGE = '{filename}[{modified_mark}]'

    def __init__(self):
        super().__init__()
        self.statusinfo = StatusInfo()

    def init_theme(self):
        self.theme = StatusBarTheme

    def on_set_document(self, doc):
        super().on_set_document(doc)
        doc.undo = None

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

    def build_status(self, statusbar):
        d = statusbar.infos.copy()
        s = self.STATUSBAR_MESSAGE.format(**d)

        self.document.replace(0, self.document.endpos(), s)
        self.document.styles.setints(0, self.document.endpos(),
                                    self.get_styleid('filename'))

    def set_info(self, **values):
        ret = self.statusinfo.set_info(**values)
        return ret

    def on_idle(self):
        if not self.closed:
            ret = super().on_idle()
            if not ret:
                if self.statusinfo.updated:
                    self.build_status(self.statusinfo)
                    self.statusinfo.updated = False
                    ret = True
            return ret

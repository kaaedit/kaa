from kaa.filetype.default import modebase
from kaa.theme import Style


class StatusInfo:
    updated = False

    def __init__(self):
        self.infos = {
            'filename': '',
            'modified': '',
            'lineno': 1,
            'linecount': 1,
            'col': 1,
            'editmode': '',
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


StatusBarThemes = {
    'basic': [
        Style('default', 'Red', 'Base02'),
        Style('filename', 'LightBlue', 'Base02'),
        Style('msg', 'Red', 'Base02'),
        Style('editmode', 'Green', 'Base02', rjust=True),
    ],
}


class StatusBarMode(modebase.ModeBase):
    USE_UNDO = False

    def __init__(self):
        super().__init__()
        self.statusinfo = StatusInfo()

    def init_themes(self):
        super().init_themes()
        self.themes.append(StatusBarThemes)

    def on_set_document(self, doc):
        super().on_set_document(doc)
        doc.undo = None

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

    def build_status(self, statusbar):
        d = statusbar.infos
        self.document.delete(0, self.document.endpos())
        style_default = self.get_styleid('default')
        style_filename = self.get_styleid('filename')
        style_editmode = self.get_styleid('editmode')

        if d['filename']:
            self.document.append(d['filename'], style_filename)

        if d['modified']:
            self.document.append('*', style_filename)

        self.document.append(' ', style_default)
        self.document.append(
            '[{lineno}:{col}] {linecount}'.format(**d), style_filename)

        self.document.append(d['editmode'], style_editmode)

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

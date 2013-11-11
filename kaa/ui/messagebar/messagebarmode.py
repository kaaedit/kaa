import kaa
from kaa.filetype.default import modebase
from kaa.theme import Theme, Style

MessageBarThemes = {
    'basic':
        Theme([
            Style('default', 'Base3', 'default'),
            Style('rec', 'Base3', 'red'),
        ]),
}

class MessageBarMode(modebase.ModeBase):
    USE_UNDO = False
    message = ''
    def init_themes(self):
        super().init_themes()
        self.themes.append(MessageBarThemes)

    def on_set_document(self, doc):
        super().on_set_document(doc)
        doc.undo = None

    def set_message(self, msg):
        self.message = msg
        self.update()

    def update(self):
        style_default = self.get_styleid('default')
        style_rec = self.get_styleid('rec')

        self.document.delete(0, self.document.endpos())
        if kaa.app.macro.is_recording():
            self.document.append('[REC]', style_rec)
            self.document.append(' ', style_default)

        self.document.append(self.message, style_default)



import kaa
from kaa.filetype.default import modebase
from kaa.theme import Theme, Style

MessageBarTheme = Theme('default', [
    Style('default', 'red', 'default', False, False),
])


class MessageBarMode(modebase.ModeBase):
    def init_theme(self):
        self.theme = MessageBarTheme

    def on_set_document(self, doc):
        super().on_set_document(doc)
        doc.undo = None

    def set_message(self, msg):
        self.document.replace(0, self.document.endpos(), msg)
        self.document.styles.setints(0, self.document.endpos(),
                                    self.get_styleid('default'))


import kaa
from kaa.filetype.default import modebase
from kaa.theme import Style

MessageBarThemes = {
    'basic': [
        Style('default', 'Base3', 'default'),
        Style('rec', 'Base3', 'red'),
    ],
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
        if not msg:
            # Get default message for current document
            if kaa.app.focus and getattr(kaa.app.focus, 'document', None):
                msg = getattr(kaa.app.focus.document.mode,
                              'DEFAULT_STATUS_MSG', None)
            else:
                msg = None

            if msg is None:
                # Show default message of app.
                msg = kaa.app.DEFAULT_MENU_MESSAGE

        if msg != self.message:
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

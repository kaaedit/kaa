from kaa import doc_re
from kaa.command import commandid, norec, norerun
from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span
from kaa.keyboard import ctrl
from kaa.theme import Style

IniThemes = {
    'basic': [
        Style('section', 'Blue', None, bold=True),
        Style('param-name', 'Orange', None, bold=True),
    ]
}


def build_tokenizer():
    return Tokenizer([
        Span('ini-section', 'section', r'^\[(?P<SECTION>.+)\]', '$'),
        Span('ini-comment', 'comment', r';.*', '$'),
        Span('ini-param-name', 'param-name', r'^([a-zA-Z0-9_-])+\s*', r'(\s*|\=)'),
    ])

MDMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

ini_keys = {
    (ctrl, 't'): 'toc.showlist',
}


class IniMode(defaultmode.DefaultMode):
    MODENAME = 'Ini'

    RE_SECTION = doc_re.compile(r'^\[(?P<SECTION>.+)\]$', doc_re.M)

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [ini_keys])

    def init_themes(self):
        super().init_themes()
        self.themes.append(IniThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]

    def get_sections(self):
        pos = 0
        while True:
            m = self.RE_SECTION.search(self.document, pos)
            if not m:
                break

            pos = m.end()
            name = m.group('SECTION')

            yield self.HeaderInfo('namespace', None, name, name,
                                  None, m.start())

    @commandid('toc.showlist')
    @norec
    @norerun
    def show_toclist(self, wnd):
        from kaa.ui.toclist import toclistmode
        sections = list(self.get_sections())
        toclistmode.show_toclist(wnd, sections)

import copy

from kaa import doc_re
from kaa.command import commandid, norec, norerun
from kaa.filetype.default import defaultmode
from kaa.keyboard import ctrl
from kaa.theme import Style
from kaa.syntax_highlight import *

INIThemes = {
    'basic': [
        Style('section', 'Blue', None, bold=True),
        Style('param-name', 'Orange', None, bold=True),
    ]
}


def ini_tokens():
    return [
        ('comment', Span('comment', r';', '$')),
        ('section', Span('section', r'^\[', r'\]')),
        ('param-name', SingleToken('param-name', [r"^([a-zA-Z0-9_-])+"])),
    ]


def make_tokenizer():
    return Tokenizer(tokens=ini_tokens())

INIMENU = [
    ['&Comment', None, 'code.region.linecomment'],
    ['&Uncomment', None, 'code.region.unlinecomment'],
    ['&Table of contents', None, 'toc.showlist'],
]

MDMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

ini_keys = {
    (ctrl, 't'): 'toc.showlist',
}


class INIMode(defaultmode.DefaultMode):
    MODENAME = 'INI'
    LINE_COMMENT = ';'

    RE_SECTION = doc_re.compile(r'^\[(?P<SECTION>.+)\]$', doc_re.M)

    tokenizer = make_tokenizer()

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [ini_keys])

    def init_themes(self):
        super().init_themes()
        self.themes.append(INIThemes)

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(INIMENU)

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

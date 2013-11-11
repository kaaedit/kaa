import keyword, copy
from kaa.filetype.default import defaultmode, theme
from kaa.highlight import Tokenizer, Keywords, Span, SingleToken
from kaa.theme import Theme, Style
from gappedbuf import re as gre
from kaa.command import Commands, command, norec, norerun
from kaa.keyboard import *

PythonThemes = {
    'basic':
        Theme([
            Style('python-bytes', 'blue', 'default'),
        ]),

}

PYTHONMENU = [
    ['&Comment', None, 'code.region.linecomment'],
    ['&Uncomment', None, 'code.region.unlinecomment'],
]

python_code_keys = {
    ((alt, 'm'), ('c')): 'menu.python.code',
}

class PythonMode(defaultmode.DefaultMode):
    MODENAME = 'Python'
    re_begin_block = gre.compile(r"[^#]*:\s*(#.*)?$")
    LINE_COMMENT = '#'
    
    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [python_code_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(PYTHONMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonThemes)

    def init_tokenizers(self):
        self.tokenizers = [Tokenizer([
            Keywords('python-statement', 'keyword', keyword.kwlist),
            SingleToken('python-numeric', 'number',
                         [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b']), 
            Span('python-comment', 'comment', r'\#', '$', escape='\\'),
            Span('python-string31', 'string', 'r?"""', '"""', escape='\\'),
            Span('python-string32', 'string', "r?'''", "'''", escape='\\'),
            Span('python-string11', 'string', 'r?"', '"', escape='\\'),
            Span('python-string12', 'string', "r?'", "'", escape='\\'),

            Span('python-bytes31', 'python-bytes', '(br?|r?b)"""', '"', escape='\\'),
            Span('python-bytes32', 'python-bytes', "(br?|r?b)'''", "'''", escape='\\'),
            Span('python-bytes11', 'python-bytes', '(br?|r?b)"', '"', escape='\\'),
            Span('python-bytes12', 'python-bytes', "(br?|r?b)'", "'", escape='\\'),
        ])]

    RE_BEGIN_NEWBLOCK = gre.compile(r"[^#]*\:\s*(#.*)?$", gre.M)
    def on_auto_indent(self, wnd):
        pos = wnd.cursor.pos
        tol = self.document.gettol(pos)
        m = self.RE_BEGIN_NEWBLOCK.match(self.document.buf, tol, pos)
        if not m:
            super().on_auto_indent(wnd)
        else:
            f, t = self.get_indent_range(pos)
            t = min(t, pos)
            cols = self.calc_cols(f, t)
            indent = self.build_indent_str(cols+self.indent_width)
            indent = '\n'+indent
            self.edit_commands.insert_string(wnd, pos, indent, 
                    update_cursor=False)
            wnd.cursor.setpos(pos+len(indent))
            
            wnd.cursor.savecol()


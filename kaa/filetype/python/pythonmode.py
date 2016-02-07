import io
import copy
from kaa.filetype.default import defaultmode
from kaa.theme import Style
from kaa import doc_re
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.keyboard import *
from kaa.ui.pythondebug import port
from kaa.syntax_highlight import *

PythonThemes = {
    'basic': [
        Style('python-bytes', 'blue', None),
    ],
}

PYTHONMENU = [
    ['&Comment', None, 'code.region.linecomment'],
    ['&Uncomment', None, 'code.region.unlinecomment'],
    ['&Table of contents', None, 'toc.showlist'],
    ['Toggle &Breakpoint', None, 'debugger.toggle.breakpoint'],
]

python_keys = {
    (ctrl, 't'): 'toc.showlist',
    f8: 'debugger.toggle.breakpoint',
}

KEYWORDS = ['and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
            'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield']

CONSTANTS = ['False', 'None', 'True']


def make_tokenizer():
    return Tokenizer(tokens=(
        ("keyword", Keywords('keyword', KEYWORDS)),
        ("constant", Keywords('constant', CONSTANTS)),
        ("decorator", SingleToken('directive', [r'@\w[\w.]*'])),
        ("number", SingleToken('number',
                               [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ("comment", Span('comment', r'\#', '$', escape='\\')),

        ("string31", Span('string', '[rR]?"""', '"""', escape='\\')),
        ("string32", Span('string', "[rR]?'''", "'''", escape='\\')),
        ("string11", Span('string', '[rR]?"', '"', escape='\\')),
        ("string12", Span('string', "[rR]?'", "'", escape='\\')),

        ('bytes31', Span('python-bytes',
                         '([bB][rR]?|[rR]?[bB])"""', '"""', escape='\\')),
        ('bytes32', Span('python-bytes',
                         "([bB][rR]?|[rR]?[bB])'''", "'''", escape='\\')),
        ('bytes11', Span('python-bytes',
                         '([bB][rR]?|[rR]?[bB])"', '"', escape='\\')),
        ('bytes12', Span('python-bytes',
                         "([bB][rR]?|[rR]?[bB])'", "'", escape='\\')),
    ))


class PythonMode(defaultmode.DefaultMode):
    MODENAME = 'Python'
    re_begin_block = doc_re.compile(r"[^#]*:\s*(#.*)?$")
    LINE_COMMENT = '#'

    tokenizer = make_tokenizer()

    @classmethod
    def update_fileinfo(cls, fileinfo, document=None):
        import tokenize
        if not document:
            try:
                with open(fileinfo.fullpathname, 'rb') as buffer:
                    encoding, lines = tokenize.detect_encoding(buffer.readline)
                    fileinfo.encoding = encoding
            except IOError:
                pass
        else:
            s = document.gettext(0, 1024).encode('utf-8', errors='ignore')
            buffer = io.BytesIO(s)
            encoding, lines = tokenize.detect_encoding(buffer.readline)
            fileinfo.encoding = encoding

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [python_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(PYTHONMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonThemes)

    def on_set_document(self, document):
        super().on_set_document(document)
        self.display_breakpoint()

    def on_del_window(self, wnd):
        super().on_del_window(wnd)
        self.update_python_breakpoints()

    def get_line_overlays(self):
        ret = super().get_line_overlays()

        for k, v in self.get_breakpoints():
            ret[v] = 'breakpoint'
        return ret

    def on_file_saved(self, fileinfo):
        if self.document.get_filename() != fileinfo.fullpathname:
            self._clear_breakpoints()

        super().on_file_saved(fileinfo)

    RE_SEARCH_NAME = doc_re.compile(r'(\\.)|(\w+)|(\S)')

    def _py_getname(self, pos):
        while True:
            m = self.RE_SEARCH_NAME.search(self.document, pos)
            if not m:
                return self.document.endpos()
            if m.lastindex == 1:
                pos = m.end()
                continue
            elif m.lastindex == 2:
                return m.start(), m.end(), m.group()
            else:
                return m.start(), m.start(), ''

    def _py_def(self, m, token):
        pos, end, name = self._py_getname(m.end())
        if name:
            f, t = self.get_indent_range(m.start())
            cols = self.calc_cols(f, t)

            yield token, f, (cols, name)
        return end

    def _py_end_comment(self, m):
        close = r'(\\\n)|(\n)'
        reobj = doc_re.compile(close)

        pos = m.end()
        while True:
            m = reobj.search(self.document, pos)
            if not m:
                return self.document.endpos()
            if m.lastindex == 2:
                return m.end()
            else:
                pos = m.end()

    def _py_end_string(self, m):
        close = r'\\.|(?P<CLOSE>%s)' % m.group()
        reobj = doc_re.compile(close)

        pos = m.end()
        while True:
            m = reobj.search(self.document, pos)
            if not m:
                return self.document.endpos()
            if m.lastgroup == 'CLOSE':
                return m.end()
            else:
                pos = m.end()

    TOKENIZE_SEARCH_CLOSE = r'''
            (?P<BACKSLASH>\\.)|(?P<PARENTHESIS>[\{\[\(])|
            (?P<COMMENT>\#)|(?P<STRING>\"|\"\"\"|\'|\'\'\')'''

    def _py_close_parenthesis(self, m):
        close = '|(?P<CLOSE>\\%s)' % self.PARENSIS_PAIR[m.group()]
        reobj = doc_re.compile(self.TOKENIZE_SEARCH_CLOSE + close, doc_re.X)
        pos = m.end()
        while True:
            m = reobj.search(self.document, pos)
            if not m:
                return self.document.endpos()

            g = m.lastgroup
            if g == 'CLOSE':
                return m.end()
            elif g == 'BACKSLASH':
                pos = m.end()
            elif g == 'PARENTHESIS':
                pos = self._py_close_parenthesis(m)
            elif g == 'STRING':
                pos = self._py_end_string(m)
            elif g == 'COMMENT':
                pos = self._py_end_comment(m)
            else:
                assert 0

    RE_TOKENIZE_SEARCH = doc_re.compile(
        r'''(?P<BACKSLASH>\\.)|(?P<CLASS>\bclass\b)|
            (?P<DEF>\bdef\b)|(?P<PARENTHESIS>[\{\[\(])|
            (?P<COMMENT>\#)|(?P<STRING>\"\"\"|\"|\'\'\'|\')''', doc_re.X)

    def _parse_names(self, pos):
        while True:
            m = self.RE_TOKENIZE_SEARCH.search(self.document, pos)
            if not m:
                break
            g = m.lastgroup
            if g == 'BACKSLASH':
                pos = m.end()
            elif g == 'CLASS':
                pos = yield from self._py_def(m, 'class')
            elif g == 'DEF':
                pos = yield from self._py_def(m, 'def')
            elif g == 'PARENTHESIS':
                pos = self._py_close_parenthesis(m)
            elif g == 'STRING':
                pos = self._py_end_string(m)
            elif g == 'COMMENT':
                pos = self._py_end_comment(m)
            else:
                assert 0

    def _py_getfuncs(self):
        for token, pos, (indent, name) in self._parse_names(0):
            if token in {'class', 'def'}:
                yield token, pos, indent, name

    def get_headers(self):
        stack = []
        for token, pos, indent, name in self._py_getfuncs():
            dispname = name if token is 'class' else name + '()'
            headertype = 'namespace' if token == 'class' else 'function'
            if not stack:
                header = self.HeaderInfo(
                    headertype, None, name, dispname, None, pos)
                yield header
                stack.append((indent, header))
                continue

            for i, (parent_indent, info) in enumerate(stack):
                if indent <= parent_indent:
                    del stack[i:]
                    break

            if stack:
                parents = tuple(header for (_, header) in stack
                                if header.token == 'namespace')
                parent = parents[-1] if parents else None
                fullname = '.'.join([stack[-1][1].name, name])
                header = self.HeaderInfo(
                    headertype, parent, fullname,
                    dispname, None, pos)
            else:
                header = self.HeaderInfo(
                    headertype, None, name, dispname, None, pos)

            yield header
            stack.append((indent, header))

    @commandid('toc.showlist')
    @norec
    @norerun
    def show_toclist(self, wnd):
        from kaa.ui.toclist import toclistmode
        toclistmode.show_toclist(wnd, list(self.get_headers()))

    RE_SPLIT_LINE = doc_re.compile(
        r'''(?P<BACKSLASH>\\.)|(?P<OPEN_PARENTHESIS>[\{\[\(])|
            (?P<CLOSE_PARENTHESIS>[\}\]\)])|(?P<COMMENT>\#)|
            (?P<STRING>\"\"\"|\"|\'\'\'|\')|(?P<COLON>:)''',
        doc_re.X)

    def _get_indent_reasons(self, pos, posto):
        while pos < posto:
            m = self.RE_SPLIT_LINE.search(self.document, pos, posto)
            if not m:
                break

            g = m.lastgroup
            if g == 'BACKSLASH':
                pos = m.end()
            elif g == 'OPEN_PARENTHESIS':
                yield 'open_parenthesis', m.span(), m.group()
                pos = m.end()
            elif g == 'CLOSE_PARENTHESIS':
                yield 'close_parenthesis', m.span(), m.group()
                pos = m.end()
            elif g == 'COMMENT':
                pos = self._py_end_comment(m)
            elif g == 'STRING':
                pos = self._py_end_string(m)
            elif g == 'COLON':
                yield 'colon', m.span(), m.group()
                pos = m.end()
            else:
                assert 0

    def _calc_parenthesis_balance(self, tokens):
        p = 0
        for token, tokenpos, s in tokens:
            if token == 'open_parenthesis':
                p += 1
            elif token == 'close_parenthesis':
                p -= 1
        return p

    def _find_parenthesis_open_line(self, pos):
        while pos > 0:
            tol = self.document.gettol(pos)
            tokens = list(self._get_indent_reasons(tol, pos))
            p = self._calc_parenthesis_balance(tokens)
            if p > 0:
                return tol
            pos = tol - 1
        return None

    def calc_next_indent(self, pos):
        tol = self.document.gettol(pos)
        tokens = list(self._get_indent_reasons(tol, pos))
        if not tokens:
            return None

        f, t = self.get_indent_range(pos)
        t = min(t, pos)
        cols = self.calc_cols(f, t)

        if tokens[-1][0] == 'colon':
            return cols + self.indent_width

        p = self._calc_parenthesis_balance(tokens)
        if p > 0:
            return cols + self.indent_width
        elif p == 0:
            return None
        else:
            open_line = self._find_parenthesis_open_line(tol - 1)
            if open_line is None:
                return None
            f, t = self.get_indent_range(open_line)
            t = min(t, pos)
            return self.calc_cols(f, t)

    def get_breakpoints(self):
        for k, v in self.document.marks.items():
            if isinstance(k, port.BreakPoint):
                yield k, v

    def update_python_breakpoints(self):
        filename = self.document.get_filename()
        if not filename:
            return

        bps = []
        for k, v in self.get_breakpoints():
            lineno = self.document.buf.lineno.lineno(v)
            k.lineno = lineno
            bps.append(k)

        port.set_breakpoints(filename, bps)

    def _clear_breakpoints(self):
        bps = [k for k, v in self.get_breakpoints()]
        for bp in bps:
            del self.document.marks[bp]

    def display_breakpoint(self):
        self._clear_breakpoints()
        fname = self.document.get_filename()
        if fname:
            bps = port.get_breakpoints(fname)
            for bp in bps:
                pos = self.document.get_lineno_pos(bp.lineno)
                self.document.marks[bp] = pos

        self.document.style_updated()

    @commandid('debugger.toggle.breakpoint')
    @norec
    @norerun
    def toggle_breakpoint(self, wnd):
        pos = wnd.cursor.pos
        tol = self.document.gettol(pos)
        for bp, pos in self.get_breakpoints():
            if tol == self.document.gettol(pos):
                del self.document.marks[bp]
                break
        else:
            filename = self.document.get_filename()
            if filename:
                lineno = self.document.buf.lineno.lineno(tol)
                bp = port.BreakPoint(filename, lineno)
                self.document.marks[bp] = tol

        self.document.style_updated()

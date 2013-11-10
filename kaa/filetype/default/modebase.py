import itertools, unicodedata, collections

import gappedbuf.re
import kaa
from kaa import keyboard, editmode
import kaa.log
from kaa import highlight
from kaa import theme
from kaa import screen

class SearchOption:
    RE = gappedbuf.re
    def __init__(self):
        self.text = ''
        self.replace_to = ''
        self.ignorecase = True
        self.word = False
        self.regex = False

    def clone(self):
        ret = self.__class__()
        ret.text = self.text
        ret.replace_to = self.replace_to
        ret.ignorecase = self.ignorecase
        ret.word = self.word
        ret.regex = self.regex
        return ret
        
    def get_regex(self):
        text = self.text
        if not self.regex:
            text = self.RE.escape(text)
        if self.word:
            text = r'\b'+text+r'\b'

        opt = self.RE.MULTILINE
        if self.ignorecase:
            opt += self.RE.IGNORECASE

        regex = self.RE.compile(text, opt)
        return regex

SearchOption.LAST_SEARCH = SearchOption()

class ModeBase:
    CLOSE_ON_DEL_WINDOW = True

    SCREEN_NOWRAP = False
    NO_WRAPINDENT = False
    SCREEN_BUILD_ENTIRE_ROWS = False
    SHOW_LINENO = False
    USE_UNDO = True
    DOCUMENT_MODE = False
    HIGHLIGHT_CURSORLINE = False

    tab_width = 8
    indent_width = 4
    indent_tab = False
    auto_indent = True

    closed = False
    current_lastcommands = None
    theme = None
    highlight = None
    _check_fileupdate = 0
    
    def __init__(self):
        self.commands = {}
        self.is_availables = {}

        self.keybind = keyboard.KeyBind()
        self.keybind_vi_commandmode = keyboard.KeyBind()
        self.keybind_vi_visualmode = keyboard.KeyBind()
        self.keybind_vi_visuallinewisemode = keyboard.KeyBind()
        self.init_keybind()

        self.init_commands()
        self.init_menu()

        self.themes = []
        self.init_themes()
        self._build_theme()
        kaa.app.translate_theme(self.theme)
        
        self.tokenizers = []
        self.init_tokenizers()
        self.stylemap = {}
        self.highlight = highlight.Highlighter(self.tokenizers)

    def close(self):
        self.document = None
        self.closed = True

        self.keybind.clear()

        self.theme = None

        self.commands.clear()
        self.commands = None

        self.is_availables = None
        self.highlight.close()
        self.highlight = None
        self.tokenizers = None
        self.stylemap = None

    def _build_style_map(self):
        self.stylemap[0] = self.theme.get_style('default')
        for tokenid in self.highlight.tokenids:
            assert tokenid not in self.stylemap
            token = self.highlight.get_token(tokenid)
            if token:
                stylename = token.get_stylename(tokenid)
                style = self.theme.get_style(stylename)

                self.stylemap[tokenid] = style
            else:
                self.stylemap[tokenid] = self.theme.get_style('default')

    def on_set_document(self, document):
        self.document = document
        self.document.styles.setints(0, len(self.document.styles), 0)

        self._build_style_map()
        self.document.use_undo(self.USE_UNDO)
        
    def on_document_updated(self, pos, inslen, dellen):
        if self.highlight:
            self.highlight.updated(self.document, pos, inslen, dellen)

    def on_add_window(self, wnd):
        self.editmode_insert(wnd)

    def on_del_window(self, wnd):
        if len(self.document.wnds) == 1:
            if self.DOCUMENT_MODE and self.document.fileinfo:
                self.document.fileinfo.save_screenloc(wnd.screen.pos)

    def on_focus(self, wnd):
        kaa.app.show_cursor(self.is_cursor_visible())

        # relocate cursor
        wnd.cursor.setpos(wnd.cursor.pos)

    def register_keys(self, keybind, keys):
        for d in keys:
            keybind.add_keybind(d)

    def init_keybind(self):
        pass

    def init_commands(self):
        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, 'COMMAND_ID') and callable(attr):
                self.commands[getattr(attr, 'COMMAND_ID')] = attr

    def init_menu(self):
        pass
        
    def init_themes(self):
        pass

    def init_tokenizers(self):
        pass

    def register_command(self, cmds):
        self.commands.update(cmds.get_commands())
        self.is_availables.update(cmds.get_commands_is_enable())

    def get_command(self, commandid):
        is_available = self.is_availables.get(commandid, None)
        cmd = self.commands.get(commandid, None)
        return (is_available, cmd)

    def editmode_insert(self, wnd):
        wnd.set_editmode(editmode.EditMode())

    def editmode_visual(self, wnd):
        wnd.set_editmode(editmode.VisualMode())

    def editmode_visual_linewise(self, wnd):
        wnd.set_editmode(editmode.VisualLinewiseMode())

    def editmode_command(self, wnd):
        wnd.set_editmode(editmode.CommandMode())

    def get_styleid(self, stylename):
        if stylename == 'default':
            return 0

        for styleid, style in self.stylemap.items():
            if style.name == stylename:
                return styleid
        else:
            if not self.stylemap:
                ret = 1
            else:
                ret = max(self.stylemap.keys())+1
            self.stylemap[ret] = self.theme.get_style(stylename)
            return ret

    def select_theme(self, theme_name, themes):
        theme = themes.get(theme_name, None)
        if theme is None:
            theme = themes[kaa.app.DEFAULT_THEME]
        return theme

    def _build_theme(self):
        theme_name = kaa.app.get_current_theme()
        self.theme = theme.Theme([])
        for t in self.themes:
            self.theme.update(self.select_theme(theme_name, t))

    def get_style(self, tokenid):
        ret = self.stylemap.get(tokenid, None)
        if ret is None:
            ret = self.theme.get_style('default')
        return ret

    def get_menu(self, itemname):
        return self.menu.get(itemname, None)
        
    def is_cursor_visible(self):
        return 1   # normal

    def on_keypressed(self, wnd, event, s, commands, candidate):
        return s, commands, candidate

    def filter_string(self, wnd, s):
        return s

    def on_edited(self, wnd):
        pass

    def on_str(self, wnd, s):
        self.edit_commands.put_string(wnd, s)
        wnd.screen.selection.clear()

        if kaa.app.macro.is_recording():
            kaa.app.macro.record_string(s)
        if self.highlight:
            # run highlighter a bit to display changes immediately.
            self.highlight.update_style(self.document, batch=50)

    def add_lastcommands(self, commandids):
        if self.current_lastcommands is not None:
            self.current_lastcommands.extend(commandids)

    def on_commands(self, wnd, commandids):
        try:
            if callable(commandids):
                commandids(wnd)
                return

            self.current_lastcommands = []
            for commandid in commandids:
                is_available, command = self.get_command(commandid)
                if not command:
                    msg = 'command {!r} is not registered.'.format(commandid)
                    kaa.app.messagebar.set_message(msg)
                    kaa.log.error(msg)
                    return

                command(wnd)
                if kaa.app.macro.is_recording():
                    kaa.app.macro.record(command)

                if not getattr(command, 'NORERUN', False):
                    self.current_lastcommands.append(commandid)

            if self.current_lastcommands:
                kaa.app.lastcommands = self.current_lastcommands

        finally:
            wnd.editmode.clear_repeat()
            self.current_lastcommands = None

    def on_esc_pressed(self, wnd, event):
        pass

    def on_cursor_located(self, wnd, pos, y, x):
        pass

    def update_charattr(self, wnd):
        if wnd.charattrs:
            wnd.charattrs.clear()
            wnd.screen.style_updated()
            return True

    def on_idle(self):
        if self.closed:
            return

        ret = self.run_highlight()
        return ret

    HIGHLIGHTBATCH = 300
    def run_highlight(self):
        if self.highlight:
            return self.highlight.update_style(self.document, batch=self.HIGHLIGHTBATCH)

    def _split_chars(self, begin, end):
        """split characters by character category."""

        s = self.document.gettext(begin, end)
        for key, chars in itertools.groupby(s, unicodedata.category):
            chars = ''.join(chars)
            end = begin + len(chars)
            yield begin, end, chars, key
            begin = end

    RE_WORDCHAR = r"(?P<L_WORDCHAR>[a-zA-Z0-9_]+)"
    RE_WHITESPACE = r"(?P<Z_WHITESPACE>[\t ]+)"
    RE_LF = r"(?P<_LF>\n)"
    RE_HIRAGANA = r"(?P<L_HIRAGANA>[\u3040-\u309f\u30fc]+)"
    RE_KATAKANA = r"(?P<L_KATAKANA>[\u30a0-\u30ff\u30fc]+)"

    RE_SPLITWORD = gappedbuf.re.compile('|'.join((
        RE_WORDCHAR, RE_WHITESPACE, RE_LF, RE_HIRAGANA, RE_KATAKANA)))

    def split_word(self, begin, all=False):
        """yield word in the document until line ends"""

        for m in self.RE_SPLITWORD.finditer(self.document.buf, pos=begin):
            # split unmatched characters by character category.
            f, t = m.span()
            if f != begin:
                yield from self._split_chars(begin, f)
            begin = t

            yield (f, t, m.group(), m.lastgroup)

            # finish if we reach '\n'
            if not all and m.lastgroup == '_LF':
                return

        yield from self._split_chars(begin, self.document.endpos())

    def get_word_at(self, pos):
        tol = self.document.gettol(pos)
        ret = None
        for f, t, s, cg in self.split_word(tol):
            if t <= pos:
                if cg != 'Z_WHITESPACE':
                    if t==pos and cg[0] == 'L':
                        return (f, t, cg)
                    else:
                        ret = (f, t, cg)
            elif cg == '_LF':
                break
            else:
                if cg == 'Z_WHITESPACE':
                    if f == pos:
                        return ret
                    else:
                        return
                return (f, t, cg)

        if ret and ret[1] == pos:
            return ret

    def get_word_list(self):
        words = collections.OrderedDict()
        for f, t, s, cg in self.split_word(0, all=True):
            if cg in {'Z_WHITESPACE', '_LF'}:
                continue
            if cg[0] in 'LMN': # Letter, Mark, Number
                if len(s) > 2:
                    words[s] = None
        return list(words.keys())

    def search_next(self, pos, searchinfo):
        regex = searchinfo.get_regex()
        pos = min(max(0, pos), self.document.endpos())
        m = regex.search(self.document.buf, pos)
        return m

    def search_prev(self, pos, searchinfo):
        regex = searchinfo.get_regex()
        last = None
        for m in regex.finditer(self.document.buf, 0):
            span = m.span()
            if span[1] >= pos:
                break
            last = m
        return last

    def get_line_sel(self, wnd):
        doc = wnd.document
        sel = wnd.screen.selection.get_selrange()
        if not sel:
            f = t = wnd.cursor.pos
        else:
            f, t = sel

        tol =  doc.gettol(f)

        t_tol =  doc.gettol(t)
        if t != t_tol:
            eol = doc.geteol(t)
        else:
            eol = t

        return tol, eol

    def get_indent_range(self, pos):
        tol =  self.document.gettol(pos)
        regex = gappedbuf.re.compile(self.RE_WHITESPACE)
        m = regex.match(self.document.buf, tol)
        if m:
            return m.span()
        else:
            return (tol, tol)

    def build_indent_str(self, col):
        if self.indent_tab:
            ctab = col // self.tab_width
            cspc = col % self.tab_width
            return  '\t' * ctab + ' ' * cspc
        else:
            return ' ' * col

    def on_auto_indent(self, wnd):
        pos = wnd.cursor.pos
        f, t = self.get_indent_range(pos)
        indent = self.document.gettext(f, min(pos, t))
        if pos <= t:
            self.edit_commands.insert_string(wnd, f, '\n', 
                    update_cursor=False)
            wnd.cursor.setpos(wnd.cursor.pos+1)
        else:
            indent = '\n'+indent
            self.edit_commands.insert_string(wnd, pos, indent, 
                    update_cursor=False)
            wnd.cursor.setpos(pos+len(indent))
        
        wnd.cursor.savecol()

    def calc_cols(self, f, t):
        chars = self.document.gettext(f, t)
        (dispchrs, dispcols, positions,
         intervals) = screen.translate_chars(f, chars, self.tab_width, 
                         kaa.app.config.AMBIGUOUS_WIDTH)

        return sum(dispcols)

    def on_global_next(self, wnd):
        return

    def on_global_prev(self, wnd):
        return
 
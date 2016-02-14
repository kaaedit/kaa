import re
import itertools
import unicodedata
import collections

from kaa import doc_re
import kaa
from kaa import keyboard, editmode
import kaa.log
from kaa import theme
from kaa import screen
from kaa import addon
from kaa import syntax_highlight


class SearchOption:
    RE = doc_re

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
            text = r'\b' + text + r'\b'

        opt = self.RE.MULTILINE
        if self.ignorecase:
            opt += self.RE.IGNORECASE

        regex = self.RE.compile(text, opt)
        return regex

SearchOption.LAST_SEARCH = SearchOption()

DefaultTokenizer = syntax_highlight.Tokenizer()


class ModeBase:
    (UNDO_INSERT,
     UNDO_REPLACE,
     UNDO_DELETE) = range(3)

    CLOSE_ON_DEL_WINDOW = True

    SCREEN_NOWRAP = False
    NO_WRAPINDENT = False
    SHOW_LINENO = False
    SHOW_BLANK_LINE = False
    USE_UNDO = True
    DOCUMENT_MODE = False
    HIGHLIGHT_CURSOR_ROW = False
    SHOW_CURSOR = True
    DELAY_STR = True

    tab_width = 8
    indent_width = 4
    indent_tab = False
    auto_indent = True

    closed = False
    theme = None
    _check_fileupdate = 0
    _last_autoindent = None

    tokenizer = DefaultTokenizer

    DEFAULT_MENU_MESSAGE = ''

    @classmethod
    def update_fileinfo(cls, fileinfo, document=None):
        pass

    def __init__(self):
        self.commands = {}
        self.is_availables = {}

        self.keybind = keyboard.KeyBind()
        self.keybind_vi_commandmode = keyboard.KeyBind()
        self.keybind_vi_visualmode = keyboard.KeyBind()
        self.keybind_vi_visuallinewisemode = keyboard.KeyBind()
        self.init_keybind()
        self.init_addon_keys()

        self.init_commands()
        self.init_addon_commands()

        self.init_menu()

        self.themes = []
        self.init_themes()
        self.init_addon_themes()

        self.tokenizers = []
        self.init_tokenizers()

        self._highlight_done = 0
        self._highlight_iter = None

        self.stylemap = {}
        self.stylenamemap = {}

        self.setup()
        self.setup_addon()

        self._build_theme()
        kaa.app.translate_theme(self.theme)

    def setup_addon(self):
        names = []
        for cls in self.__class__.__mro__:
            modulename = cls.__module__
            name = '.'.join((modulename, cls.__name__))
            names.insert(0, name)

        for name in names:
            for f in addon.get_addon(name, 'setup'):
                f(self)

    def setup(self):
        pass

    def close(self):
        self.document = None
        self.closed = True

        self.keybind.clear()

        self.theme = None

        self.commands.clear()
        self.commands = None

        self.is_availables = None
        self.tokenizers = None
        self.tokenizer = None
        self.stylemap = None
        self._highlight_done = 0
        self._highlight_iter = None

    def _build_style_map(self):
        self.stylemap[0] = self.theme.get_style('default')
        for styleid, token in self.tokenizer.styleid_map.items():
            if token:
                stylename = token.get_stylename(styleid)
                style = self.theme.get_style(stylename)

                self.stylemap[styleid] = style
                self.stylenamemap[style.name] = styleid
            else:
                style = self.theme.get_style('default')
                self.stylemap[styleid] = style
                self.stylenamemap[style.name] = styleid

    def on_set_document(self, document):
        self.document = document
        self.document.styles.setints(0, len(self.document.styles), 0)

        self._build_style_map()
        self.document.use_undo(self.USE_UNDO)

    def on_document_updated(self, pos, inslen, dellen):
        self._last_autoindent = None
        if pos <= self._highlight_done:
            self._highlight_done = pos
            self._highlight_iter = None

    def on_file_saved(self, fileinfo):
        pass

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

    def get_class_name(self):
        modulename = self.__class__.__module__
        name = '.'.join((modulename, self.__class__.__name__))
        return name

    def add_keybinds(self, editmode='input', keys=None):
        if not keys:
            return
        if editmode == 'input':
            self.keybind.add_keybind(keys)
        elif editmode == 'command':
            self.keybind_vi_commandmode.add_keybind(keys)
        elif editmode == 'visual':
            self.keybind_vi_visualmode.add_keybind(keys)
        elif editmode == 'visualline':
            self.keybind_vi_visuallinewisemode.add_keybind(keys)

    def init_addon_keys(self):
        name = self.get_class_name()
        keydef = addon.get_addon(name, 'keybind')
        for edit_mode, keys in keydef:
            if edit_mode == 'input':
                self.keybind.add_keybind(keys)
            elif edit_mode == 'command':
                self.keybind_vi_commandmode.add_keybind(keys)
            elif edit_mode == 'visual':
                self.keybind_vi_visualmode.add_keybind(keys)
            elif edit_mode == 'visualline':
                self.keybind_vi_visuallinewisemode.add_keybind(keys)

    def init_commands(self):
        from kaa.commands import (editorcommand, editmodecommand, vicommand)

        # todo: re-design command injection
        self.register_commandobj(editorcommand.CursorCommands())
        self.register_commandobj(editorcommand.EditCommands())
        self.register_commandobj(editorcommand.CodeCommands())
        self.register_commandobj(editorcommand.SelectionCommands())
        self.register_commandobj(editorcommand.SearchCommands())
        self.register_commandobj(editmodecommand.EditModeCommands())
        self.register_commandobj(vicommand.ViCommands())

        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, 'COMMAND_ID') and callable(attr):
                self.commands[getattr(attr, 'COMMAND_ID')] = attr

    def init_addon_commands(self):
        name = self.get_class_name()
        commands = addon.get_addon(name, 'command')

        for f in commands:
            self.commands[f.COMMAND_ID] = f

    def init_menu(self):
        pass

    def init_themes(self):
        pass

    def init_addon_themes(self):
        name = self.get_class_name()
        themes = addon.get_addon(name, 'style')
        self.themes.extend(themes)

    def add_theme(self, theme):
        self.themes.append(theme)

    def init_tokenizers(self):
        pass

    def add_command(self, f, command_id=None):
        if command_id is not None:
            f.COMMAND_ID = command_id

        self.commands[f.COMMAND_ID] = f

    def register_commandobj(self, cmds):
        self.commands.update(cmds.get_commands())
        self.is_availables.update(cmds.get_commands_is_enable())

    def get_command(self, commandid):
        ret = kaa.app.get_command(commandid)
        if ret:
            return ret
        is_available = self.is_availables.get(commandid, None)
        cmd = self.commands.get(commandid, None)
        return (is_available, cmd)

    def editmode_insert(self, wnd):
        wnd.set_editmode(editmode.EditMode())

    def editmode_replace(self, wnd):
        wnd.set_editmode(editmode.ReplaceMode())

    def editmode_visual(self, wnd):
        wnd.set_editmode(editmode.VisualMode())

    def editmode_visual_linewise(self, wnd):
        wnd.set_editmode(editmode.VisualLinewiseMode())

    def editmode_command(self, wnd):
        wnd.set_editmode(editmode.CommandMode())

    def get_styleid(self, stylename):
        if stylename == 'default':
            return 0

        styleid = self.stylenamemap.get(stylename, None)
        if styleid is not None:
            return styleid

        if not self.stylemap:
            ret = 1
        else:
            ret = max(self.stylemap.keys()) + 1

        style = self.theme.get_style(stylename)
        self.stylemap[ret] = style
        self.stylenamemap[stylename] = ret
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
        self.theme.finish_update()

    def get_style(self, tokenid):
        ret = self.stylemap.get(tokenid, None)
        if ret is None:
            ret = self.theme.get_style('default')
        return ret

    def get_menu(self, itemname):
        return self.menu.get(itemname, None)

    def is_cursor_visible(self):
        return self.SHOW_CURSOR

    def on_keypressed(self, wnd, event, s, commands, candidate):
        return s, commands, candidate

    def filter_string(self, wnd, s):
        return s

    def on_edited(self, wnd):
        pass

    def on_str(self, wnd, s, overwrite=False):
        self.put_string(wnd, s, overwrite=overwrite)
        wnd.screen.selection.clear()

        if kaa.app.macro.is_recording():
            kaa.app.macro.record_string(s, overwrite)

        # run highlighter a bit to display changes immediately.
        self.run_tokenizer(batch=50)

    def on_commands(self, wnd, commandids, n_repeat=1):
        wnd.set_command_repeat(n_repeat)
        try:
            if callable(commandids):
                commandids(wnd)
                return

            current_lastcommands = []
            for commandid in commandids:
                is_available, command = self.get_command(commandid)
                if not command:
                    msg = 'command {!r} is not registered.'.format(commandid)
                    kaa.app.messagebar.set_message(msg)
                    kaa.log.error(msg)
                    return

                command(wnd)
                if kaa.app.macro.is_recording():
                    kaa.app.macro.record(n_repeat, command)

                if not getattr(command, 'NORERUN', False):
                    current_lastcommands.append(commandid)

            if current_lastcommands:
                kaa.app.lastcommands = (n_repeat, current_lastcommands)

        finally:
            wnd.set_command_repeat(1)

        def f():
            import kaa.cui.frame
            frames = kaa.cui.frame.MainFrame.childframes
            frame_panels = [f._panel for f in frames]

            import curses.panel
            panels = [curses.panel.top_panel()]
            while True:
                panel = panels[-1].below()
                if panel:
                    panels.append(panel)
                else:
                    break

            for panel in panels:
                if panel in frame_panels:
                    if panel is not frame_panels[0]:
                        _trace('Invalid frame order: %s%s' %
                               (self, commandids,))
                break

        f()

    def on_esc_pressed(self, wnd, event):
        pass

    def on_cursor_located(self, wnd, pos, y, x):
        pass

    def insert_string(self, wnd, pos, s, update_cursor=True):
        """Insert string"""

        cur_pos = wnd.cursor.pos

        wnd.document.insert(pos, s)

        if update_cursor:
            wnd.cursor.setpos(wnd.cursor.pos + len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_INSERT, pos, s,
                                  cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def replace_string(self, wnd, pos, posto, s, update_cursor=True):
        """Replace string"""

        cur_pos = wnd.cursor.pos

        deled = wnd.document.gettext(pos, posto)
        wnd.document.replace(pos, posto, s)

        if update_cursor:
            wnd.cursor.setpos(pos + len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_REPLACE, pos, posto, s,
                                  deled, cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def delete_string(self, wnd, pos, posto, update_cursor=True):
        """Delete string"""

        cur_pos = wnd.cursor.pos

        if pos < posto:
            deled = wnd.document.gettext(pos, posto)
            wnd.document.delete(pos, posto)

            if update_cursor:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            if wnd.document.undo:
                wnd.document.undo.add(self.UNDO_DELETE, pos, posto, deled,
                                      cur_pos, wnd.cursor.pos)
            self.on_edited(wnd)

    def delete_ws(self, wnd, pos, update_cursor=False):
        m = doc_re.compile(r'[ \t]+').match(self.document, pos)
        if m:
            f, t = m.span()
            self.delete_string(wnd, f, t, update_cursor=update_cursor)
            return t - f

    def replace_rect(self, wnd, repto):
        with wnd.document.undo_group():
            (posfrom, posto, colfrom, colto
             ) = wnd.screen.selection.get_rect_range()

            for s in repto:
                if posto <= posfrom:
                    break

                sel = wnd.screen.selection.get_col_string(
                    posfrom, colfrom, colto)
                if sel:
                    f, t, org = sel
                    if org.endswith('\n'):
                        t = max(f, t - 1)
                    self.replace_string(wnd, f, t, s)
                    posto += (len(s) - (t - f))
                posfrom = wnd.document.geteol(posfrom)

    def put_string(self, wnd, s, overwrite=False):
        s = self.filter_string(wnd, s)

        if wnd.screen.selection.is_selected():
            if wnd.screen.selection.is_rectangular():
                if '\n' not in s:
                    self.replace_rect(wnd, itertools.repeat(s))
                else:
                    self.replace_rect(wnd, s.split('\n'))

            else:
                sel = wnd.screen.selection.get_selrange()
                f, t = sel
                self.replace_string(wnd, f, t, s)
        else:
            if not overwrite:
                self.insert_string(wnd, wnd.cursor.pos, s)
            else:
                eol = wnd.document.get_line_to(wnd.cursor.pos)
                posto = min(wnd.cursor.pos + len(s), eol)
                self.replace_string(wnd, wnd.cursor.pos, posto, s)

    def update_charattr(self, wnd):
        if wnd.charattrs:
            wnd.charattrs.clear()
            wnd.screen.style_updated()
            return True

    def on_idle(self):
        if self.closed:
            return

        ret = self.run_tokenizer()
        return ret

    def get_line_overlays(self):
        return {}

    def _get_highlight_range(self):
        return (0, self.document.endpos())

    HIGHLIGHTBATCH = 300

    def run_tokenizer(self, batch=HIGHLIGHTBATCH):
        range_start, range_end = self._get_highlight_range()

        if self._highlight_done < range_start:
            self._highlight_done = range_start

        if not self._highlight_iter:
            f = max(range_start, self._highlight_done - 1)
            self._highlight_iter = syntax_highlight.begin_tokenizer(
                self.document, self.tokenizer, f)

        updatefrom = self.document.endpos()
        updateto = range_start
        updated = False
        finished = False

        for n, (f, t, style) in enumerate(self._highlight_iter):
            f = max(range_start, f)
            t = min(range_end, t)
            if f < t:
                self.document.styles.setints(f, t, style)

            updated = True
            updatefrom = min(f, updatefrom)
            updateto = max(t, updateto)

            if batch and (n > batch):
                break

            if t >= range_end:
                finished = True
                break
        else:
            finished = True

        if self.document.endpos() == 0 or updated and (updatefrom != updateto):
            self.document.style_updated(updatefrom, updateto)
            self._highlight_done = updateto

        # returns False if finished to terminate idle loop.
        return not finished

    def _split_chars(self, begin, end):
        """split characters by character category."""

        s = self.document.gettext(begin, end)

        def get_category(c):
            return unicodedata.category(c)[0]

        for key, chars in itertools.groupby(s, get_category):
            chars = ''.join(chars)
            end = begin + len(chars)
            yield begin, end, chars, key
            begin = end

    RE_WORDCHAR = r"(?P<L_WORDCHAR>[a-zA-Z0-9_]+)"
    RE_WHITESPACE = r"(?P<Z_WHITESPACE>[\t ]+)"
    RE_LF = r"(?P<_LF>\n)"
    RE_HIRAGANA = r"(?P<L_HIRAGANA>[\u3040-\u309f\u30fc]+)"
    RE_KATAKANA = r"(?P<L_KATAKANA>[\u30a0-\u30ff\u30fc]+)"

    RE_SPLITWORD = doc_re.compile('|'.join((
        RE_WORDCHAR, RE_WHITESPACE, RE_LF, RE_HIRAGANA, RE_KATAKANA)))

# http://unicodebook.readthedocs.org/en/latest/unicode.html
# Unicode 6.0 has 7 character categories, and each category has subcategories:
#
# Letter (L): lowercase (Ll), modifier (Lm), titlecase (Lt), uppercase (Lu), other (Lo)
# Mark (M): spacing combining (Mc), enclosing (Me), non-spacing (Mn)
# Number (N): decimal digit (Nd), letter (Nl), other (No)
# Punctuation (P): connector (Pc), dash (Pd), initial quote (Pi), final quote (Pf), open (Ps), close (Pe), other (Po)
# Symbol (S): currency (Sc), modifier (Sk), math (Sm), other (So)
# Separator (Z): line (Zl), paragraph (Zp), space (Zs)
# Other (C): control (Cc), format (Cf), not assigned (Cn), private use
# (Co), surrogate (Cs)

    def split_word(self, begin, all=False):
        """yield word in the document until line ends"""

        for m in self.RE_SPLITWORD.finditer(self.document, pos=begin):
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
        prev = None
        for f, t, s, cg in self.split_word(tol):
            if pos == t:
                if cg not in {'Z_WHITESPACE', '_LF'}:
                    prev = (f, t, cg)
            elif pos < t:
                if cg not in {'Z_WHITESPACE', '_LF'}:
                    return (f, t, cg)
                else:
                    return prev

        return prev

    def get_word_list(self):
        words = collections.OrderedDict()
        for f, t, s, cg in self.split_word(0, all=True):
            if cg in {'Z_WHITESPACE', '_LF'}:
                continue
            if cg[0] in 'LMN':  # Letter, Mark, Number
                if len(s) > 2:
                    words[s] = None
        return list(words.keys())

    def search_next(self, pos, searchinfo):
        regex = searchinfo.get_regex()
        pos = min(max(0, pos), self.document.endpos())
        m = regex.search(self.document, pos)
        return m

    def search_prev(self, pos, searchinfo):
        regex = searchinfo.get_regex()
        last = None
        for m in regex.finditer(self.document, 0):
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

        tol = doc.gettol(f)

        t_tol = doc.gettol(t)
        if t != t_tol:
            eol = doc.geteol(t)
        else:
            eol = t

        return tol, eol

    def get_indent_range(self, pos):
        tol = self.document.gettol(pos)
        regex = doc_re.compile(self.RE_WHITESPACE)
        m = regex.match(self.document, tol)
        if m:
            return m.span()
        else:
            return (tol, tol)

    def build_indent_str(self, col):
        if self.indent_tab:
            ctab = col // self.tab_width
            cspc = col % self.tab_width
            return '\t' * ctab + ' ' * cspc
        else:
            return ' ' * col

    def get_parent_indent(self, pos):
        tol = self.document.gettol(pos)
        f, t = self.get_indent_range(tol)
        cols = self.calc_cols(f, t)

        while tol:
            eol = tol
            tol = self.document.gettol(eol - 1)
            f, t = self.get_indent_range(tol)
            pcols = self.calc_cols(f, t)
            if pcols < cols:
                return pcols

    def cancel_auto_indent(self, wnd):
        if self._last_autoindent:
            f, t = (min(max(0, p), self.document.endpos())
                    for p in self._last_autoindent)
            self._last_autoindent = None
            if f != t and wnd.cursor.pos == t:
                e = self.document.get_line_break(wnd.cursor.pos)
                if e == t:
                    s = self.document.gettext(f, t)
                    m = re.match(self.RE_WHITESPACE, s)
                    if m and m.group() == s:
                        self.delete_string(
                            wnd, f, t, update_cursor=False)
                        wnd.cursor.setpos(f)
                        return True

    def calc_next_indent(self, pos):
        return None

    MAX_AUTO_INDENT = 30

    def on_auto_indent(self, wnd):
        pos = wnd.cursor.pos
        f, t = self.get_indent_range(pos)
        if pos <= t:
            b = self.document.get_line_break(pos)
            self.insert_string(wnd, f, '\n', update_cursor=False)
            wnd.cursor.setpos(pos + 1)
            wnd.cursor.savecol()

            # if new line don't hava non-ws char,
            # thie line should be subject to cancel-indent.
            if t == b:
                self._last_autoindent = (f + 1, wnd.cursor.pos)
            return

        indentcol = self.calc_next_indent(pos)
        if indentcol is None:
            indent = self.document.gettext(f, min(pos, t))
        else:
            indent = self.build_indent_str(
                min(self.MAX_AUTO_INDENT, indentcol))

        self.insert_string(wnd, pos, '\n' + indent, update_cursor=False)
        self.delete_ws(wnd, pos + len(indent) + 1)
        wnd.cursor.setpos(pos + len(indent) + 1)
        wnd.cursor.savecol()
        self._last_autoindent = (pos + 1, wnd.cursor.pos)

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

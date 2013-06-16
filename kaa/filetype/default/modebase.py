import itertools, unicodedata

import gappedbuf.re
import kaa
from kaa import keyboard, keydispatcher, LOG
from kaa import highlight


class SearchOption:
    def __init__(self):
        self.text = ''
        self.ignorecase = True
        self.word = False
        self.regex = False

    def get_regex(self):
        text = self.text
        if not self.regex:
            text = gappedbuf.re.escape(text)
        if self.word:
            text = r'\b'+text+r'\b'

        opt = gappedbuf.re.MULTILINE
        if self.ignorecase:
            opt += gappedbuf.re.IGNORECASE

        regex = gappedbuf.re.compile(text, opt)
        return regex

class ModeBase:
    SCREEN_NOWRAP = False
    SCREEN_BUILD_ENTIRE_ROW = False

    closed = False

    def __init__(self):
        self.commands = {}
        self.is_availables = {}
        self.keybind = keyboard.KeyBind()
        self.theme = None

        self.init_keybind()
        self.init_commands()
        self.init_theme()
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
        self.commands = None
        self.is_availables = None
        self.highlight.close()
        self.highlight = None
        self.tokenizers = None
        self.stylemap = None

    def _build_style_map(self):
        for tokenid in self.highlight.tokenids:
            token = self.highlight.get_token(tokenid)
            stylename = token.get_stylename(tokenid)
            style = self.theme.get_style(stylename)

            self.stylemap[tokenid] = style

    def on_set_document(self, document):
        self.document = document
        self.document.styles.setints(0, len(self.document.styles), 0)

        self._build_style_map()

    def on_document_updated(self, pos, inslen, dellen):
        pass

    def on_add_window(self, wnd):
        pass

    def init_keybind(self):
        pass

    def init_commands(self):
        pass

    def init_theme(self):
        pass

    def init_tokenizers(self):
        pass

    def register_command(self, cmds):
        self.commands.update(cmds.get_commands())
        self.is_availables.update(cmds.get_commands_is_enable())

    def create_keydispatcher(self):
        return keydispatcher.KeyDispatcher()

    def get_command(self, commandid):
        is_available = self.is_availables.get(commandid, None)
        cmd = self.commands.get(commandid, None)
        return (is_available, cmd)

    def get_styleid(self, stylename):
        for styleid, style in self.stylemap.items():
            if style.name == stylename:
                return styleid
        else:
            assert len(self.stylemap) not in self.stylemap
            ret = len(self.stylemap)
            self.stylemap[ret] = self.theme.get_style(stylename)
            return ret

    def get_style(self, tokenid):
        ret = self.stylemap.get(tokenid, None)
        if ret is None:
            ret = self.theme.get_style('default')
        return ret

    def get_cursor_visibility(self):
        return 1   # normal

    def on_str(self, wnd, s):
        self.edit_commands.put_string(wnd, s)
        if kaa.app.macro.is_recording():
            kaa.app.macro.record_string(s)
        if self.highlight:
            # run highlighter a bit to display changes immediately.
            self.highlight.update_style(self.document, batch=50)

    def on_commands(self, wnd, commandids):
        if callable(commandids):
            commandids(wnd)
            if kaa.app.macro.is_recording():
                kaa.app.macro.record(commandsids)
            return

        for commandid in commandids:
            is_available, command = self.get_command(commandid)
            if not command:
                LOG.warn('command {!r} is not registered.'.format(commandid))
                return

            command(wnd)
            if kaa.app.macro.is_recording():
                kaa.app.macro.record(command)

    def on_esc_pressed(self, wnd, event):
        pass

    def on_cursor_located(self, wnd, pos, y, x):
        pass

    def on_idle(self):
        if self.closed:
            return

        ret = self.run_highlight()
        return ret

    def run_highlight(self):
        pass

    def _split_chars(self, begin, end):
        """split characters by character category."""

        s = self.document.gettext(begin, end)
        for key, chars in itertools.groupby(s, unicodedata.category):
            chars = ''.join(chars)
            end = begin + len(chars)
            yield begin, end, chars
            begin = end

    RE_WORDCHAR = r"(?P<WORDCHAR>[a-zA-Z0-9_]+)"
    RE_WHITESPACE = r"(?P<WHITESPACE>[\t ]+)"
    RE_LF = r"(?P<LF>\n)"
    RE_HIRAGANA = r"(?P<HIRAGANA>[\u3040-\u309f\u30fc]+)"
    RE_KATAKANA = r"(?P<KATAKANA>[\u30a0-\u30ff\u30fc]+)"

    RE_SPLITWORD = gappedbuf.re.compile('|'.join((
        RE_WORDCHAR, RE_WHITESPACE, RE_LF, RE_HIRAGANA, RE_KATAKANA)))

    def split_word(self, begin):
        """yield word in the document until line ends"""

        for m in self.RE_SPLITWORD.finditer(self.document.buf, pos=begin):
            # split unmatched characters by character category.
            f, t = m.span()
            if f != begin:
                yield from self._split_chars(begin, f)
            begin = t

            yield (f, t, m.group())

            # finish if we reach '\n'
            if m.lastgroup == 'LF':
                return

        yield from self._split_chars(begin, self.document.endpos())

    def search_next(self, wnd, pos, searchinfo):
        regex = searchinfo.get_regex()
        m = regex.search(self.document.buf, pos)
        if m:
            return m.span()

    def search_prev(self, wnd, pos, searchinfo):
        regex = searchinfo.get_regex()
        last = None
        for m in regex.finditer(self.document.buf, 0):
            span = m.span()
            if span[1] >= pos:
                break
            last = span
        return last

import kaa
from kaa.keyboard import *
from kaa.ui.dialog import dialogmode
from kaa.filetype.default import modebase, keybind
from kaa.ui.msgbox import msgboxmode
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.ui.selectlist import filterlist
from gappedbuf.sre_constants import error as gre_error

SearchThemes = {
    'basic': [],
}


searchdlg_keys = {
    '\r': ('searchdlg.search.next'),
    '\n': ('searchdlg.search.next'),
    up: ('searchdlg.history'),
}


class SearchDlgMode(dialogmode.DialogMode):
    autoshrink = True

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
    ]
    _last_searchstr = ''

    def __init__(self, target):
        super().__init__()

        self.target = target
        self.initialpos = target.cursor.pos
        self.initialrange = target.screen.selection.get_selrange()
        self.lastsearch = None
        self.lasthit = None
        self.lastmatch = None
        self.option = modebase.SearchOption.LAST_SEARCH

        if target and target.screen.selection.is_selected():
            f, t = target.screen.selection.get_selrange()
            s = target.document.gettext(f, t).split('\n')
            if s:
                s = s[0].strip()
                if s:
                    self.option.text = s

    def close(self):
        super().close()
        self.target = None
        kaa.app.messagebar.set_message("")

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)
        self.keybind.add_keybind(searchdlg_keys)

    def init_themes(self):
        super().init_themes()
        self.themes.append(SearchThemes)

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                                       [dialogmode.MarkRange('searchtext')])

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.set_cursor(self.create_cursor(wnd))
        if self.option.text:
            wnd.screen.selection.set_range(*self.document.marks['searchtext'])
        wnd.cursor.setpos(self.document.marks['searchtext'][1])

    def _build_input(self, f):
        # search text
        f.append_text('caption', 'Search:')
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='searchtext')
        f.append_text('default', ' ')

    def _build_buttons(self, f):
        # buttons
        f.append_text('right-button', '[&Next]',
                      shortcut_style='button.shortcut',
                      on_shortcut=self.search_next)

        f.append_text('right-button', '[&Prev]',
                      shortcut_style='button.shortcut',
                      on_shortcut=self.search_prev)

    def _build_options(self, f):
        f.append_text('right-button', '[&Ignore case]',
                      mark_pair='ignore-case',
                      on_shortcut=self.toggle_option_ignorecase,
                      shortcut_style='right-button.shortcut',
                      shortcut_mark='shortcut-i')

        f.append_text('right-button', '[&Word]',
                      mark_pair='word',
                      on_shortcut=self.toggle_option_word,
                      shortcut_style='right-button.shortcut',
                      shortcut_mark='shortcut-w')

        f.append_text('right-button', '[&Regex]',
                      mark_pair='regex',
                      on_shortcut=self.toggle_option_regex,
                      shortcut_style='right-button.shortcut',
                      shortcut_mark='shortcut-r')

    def build_document(self):
        with dialogmode.FormBuilder(self.document) as f:
            self._build_input(f)
            self._build_buttons(f)
            self._build_options(f)

            self.document.insert(
                self.document.marks['searchtext'][0], self.option.text)

            self.update_option_style()

        kaa.app.messagebar.set_message(
            "Hit alt+N/alt+P to search Next/Prev. Hit up to show history.")

    def _set_option_style(self, mark, style,
                          shortcutmark, shortcutstyle):
        f, t = self.document.marks[mark]
        self.document.setstyles(f, t, self.get_styleid(style))

        f = self.document.marks[shortcutmark]
        self.document.setstyles(f, f + 1, self.get_styleid(shortcutstyle))

    def _get_optionstylename(self, f):
        if f:
            return '.checked'
        else:
            return ''

    def update_option_style(self):
        style = self._get_optionstylename(self.option.ignorecase)
        self._set_option_style(
            'ignore-case', 'right-button' + style, 'shortcut-i',
            'right-button.shortcut' + style)

        style = self._get_optionstylename(self.option.word)
        self._set_option_style('word', 'right-button' + style, 'shortcut-w',
                               'right-button.shortcut' + style)

        style = self._get_optionstylename(self.option.regex)
        self._set_option_style('regex', 'right-button' + style, 'shortcut-r',
                               'right-button.shortcut' + style)

    def _option_updated(self):
        self.update_option_style()

    def _show_histdlg(self, wnd, title, candidates, callback):
        filterlist.show_listdlg(title, candidates, callback)

    @commandid('searchdlg.history')
    @norec
    @norerun
    def search_history(self, wnd):
        def callback(result):
            if result:
                f, t = wnd.document.marks['searchtext']
                wnd.document.replace(f, t, result)
                wnd.cursor.setpos(f)

        self._show_histdlg(wnd, 'Recent searches',
                           [s for s,
                               info in kaa.app.config.hist(
                                   'search_text').get()],
                           callback)

    @commandid('searchdlg.toggle.ignorecase')
    @norec
    @norerun
    def toggle_option_ignorecase(self, wnd):
        self.option.ignorecase = not self.option.ignorecase
        self._option_updated()

    @commandid('searchdlg.toggle.wordsearch')
    @norec
    @norerun
    def toggle_option_word(self, wnd):
        self.option.word = not self.option.word
        self._option_updated()

    @commandid('searchdlg.toggle.regex')
    @norec
    @norerun
    def toggle_option_regex(self, wnd):
        self.option.regex = not self.option.regex
        self._option_updated()

    def get_search_str(self):
        f, t = self.document.marks['searchtext']
        return self.document.gettext(f, t)

    def on_edited(self, wnd):
        self.lastsearch = None
        self.lasthit = None
        self.lastmatch = None
        s = self.get_search_str()

        try:
            if s != self._last_searchstr:
                if not self._search_next(wnd):
                    self.lastsearch = -1
                    self._search_next(wnd)
            self._last_searchstr = s
        except gre_error as e:
            kaa.app.messagebar.set_message(str(e))

    def _show_searchresult(self, hit):
        if hit:
            f, t = hit.span()
            self.target.cursor.setpos(f)
            self.target.screen.selection.set_range(f, t)
            kaa.app.messagebar.set_message('found')
        else:
            self.target.screen.selection.clear()
            kaa.app.messagebar.set_message('not found')

    def _search_next(self, wnd):
        self.option.text = self.get_search_str()
        if not self.option.text:
            self.target.screen.selection.clear()
        else:
            if self.lasthit is self.lastsearch is None:
                # initial search
                if self.initialrange:
                    pos = self.initialrange[0]
                else:
                    pos = self.initialpos

            elif self.lasthit:
                # continue previous search
                pos = self.lasthit[0] + 1

            else:
                # resume from top
                pos = 0

            ret = self.target.document.mode.search_next(pos, self.option)
            self._show_searchresult(ret)

            self.lastsearch = pos
            self.lasthit = ret.span() if ret else None
            self.lastmatch = ret

            return ret

    def _save_searchstr(self):
        s = self.get_search_str()
        if s:
            kaa.app.config.hist('search_text').add(s)

    @commandid('searchdlg.search.next')
    @norec
    @norerun
    def search_next(self, wnd):
        self._save_searchstr()
        return self._search_next(wnd)

    def _search_prev(self, wnd):
        self.option.text = self.get_search_str()
        if self.option.text:
            if self.lasthit is self.lastsearch is None:
                # initial search
                if self.initialrange:
                    pos = self.initialrange[1]
                else:
                    pos = self.initialpos

            elif self.lasthit:
                # continue previous search
                pos = self.lasthit[1] - 1

            else:
                # resume from end
                pos = self.target.document.endpos()

            ret = self.target.document.mode.search_prev(pos, self.option)
            self._show_searchresult(ret)

            self.lastsearch = pos
            self.lasthit = ret.span() if ret else None
            self.lastmatch = ret

            return ret

    @commandid('searchdlg.search.prev')
    @norec
    @norerun
    def search_prev(self, wnd):
        self._save_searchstr()
        return self._search_prev(wnd)

    def on_esc_pressed(self, wnd, event):
        self._save_searchstr()
        self.target.activate()
        self.target = None
        wnd.get_label('popup').destroy()


replacedlg_keys = {
    '\r': ('replacedlg.field.next'),
    '\n': ('replacedlg.field.next'),
    up: ('replacedlg.history'),
}


class ReplaceDlgMode(SearchDlgMode):
    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
    ]

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(replacedlg_keys)

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                                       [dialogmode.MarkRange('searchtext'),
                                        dialogmode.MarkRange('replacetext')])

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

    def _build_input(self, f):
        # search text
        f.append_text('caption', 'Search: ')
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='searchtext')
        f.append_text('default', '\n')

        # replace text
        f.append_text('caption', 'Replace:')
        f.append_text('default', ' ')
        f.append_text('default', '', None, mark_pair='replacetext')
        f.append_text('default', '\n')

    def _build_buttons(self, f):
        # buttons
        super()._build_buttons(f)
        f.append_text('right-button', '[&All]', 'start-all', 'end-all',
                      shortcut_style='button.shortcut', on_shortcut=self.replace_all)

    def build_document(self):
        with dialogmode.FormBuilder(self.document) as f:
            self._build_input(f)
            self._build_buttons(f)
            self._build_options(f)

            self.document.insert(
                self.document.marks['searchtext'][0], self.option.text)

            self.document.insert(
                self.document.marks['replacetext'][0], self.option.replace_to)

            self.update_option_style()

        kaa.app.messagebar.set_message(
            "Hit enter to move field. Hit up to show history.`")
        return

    def get_replace_str(self):
        f, t = self.document.marks['replacetext']
        return self.document.gettext(f, t)

    def _show_replace_msg(self, wnd, on_y, on_n):
        def cb(c):
            wnd.activate()
            if c == 'y':
                on_y(wnd)
            elif c == 'n':
                on_n(wnd)
            elif c == 'a':
                self.replace_all(wnd)
            else:
                pass

        msgboxmode.MsgBoxMode.show_msgbox(
            'Replace text?', ['&Yes', '&No', '&All', '&Cancel'], cb,
            border=True)

    def _show_search_again(self, wnd, on_y, is_top):
        def cb(c):
            wnd.activate()
            if c == 'r':
                on_y(wnd)

        pos = 'top' if is_top else 'bottom'
        msgboxmode.MsgBoxMode.show_msgbox(
            'Search failed. Resume from {pos} again?'.format(pos=pos),
            ['&Resume', '&Cancel'], cb)

    def _save_replstr(self):
        kaa.app.config.hist('repl_text').add(self.get_replace_str())

    @commandid('replacedlg.field.next')
    @norec
    @norerun
    def field_next(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']
        replacefrom, replaceto = wnd.document.marks['replacetext']

        if searchfrom <= wnd.cursor.pos <= searchto:
            wnd.cursor.setpos(replacefrom)
            wnd.screen.selection.set_range(replacefrom, replaceto)
        else:
            wnd.cursor.setpos(searchfrom)
            wnd.screen.selection.set_range(searchfrom, searchto)

    def replace_repl_history(self, wnd):
        def callback(result):
            if result:
                f, t = wnd.document.marks['replacetext']
                wnd.document.replace(f, t, result)
                wnd.cursor.setpos(f)

        self._show_histdlg(wnd, 'Recent replace strings',
                           [s for s,
                               info in kaa.app.config.hist('repl_text').get()],
                           callback)

    @commandid('replacedlg.history')
    @norec
    @norerun
    def replace_history(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']

        if searchfrom <= wnd.cursor.pos <= searchto:
            self.search_history(wnd)
        else:
            self.replace_repl_history(wnd)

    @commandid('searchdlg.search.next')
    @norec
    @norerun
    def search_next(self, wnd):
        if not self.get_search_str():
            return

        self.option.replace_to = self.get_replace_str()
        self._save_searchstr()
        self._save_replstr()

        if self.lastsearch is None:
            self._search_next(wnd)

        if self.lasthit:
            self._show_replace_msg(
                wnd, self.replace_and_next, self.skip_and_next)
        else:
            self._show_search_again(wnd, self.skip_and_next, is_top=True)

    _metachars = [
        (r"\\", "\\"),
        (r"\a", "\a"),
        (r"\b", "\b"),
        (r"\f", "\f"),
        (r"\n", "\n"),
        (r"\r", "\r"),
        (r"\t", "\t"),
    ]

    def _repl_str(self, update_cursor):
        f, t = self.lasthit
        if self.option.regex:
            s = self.lastmatch.expand(self.option.replace_to)
        else:
            s = self.option.replace_to

        self.target.document.mode.replace_string(
            self.target, f, t, s, update_cursor=update_cursor)

        self.lasthit = (f, f + len(s))

    def replace_and_next(self, wnd):
        self._repl_str(update_cursor=True)
        self._search_next(wnd)
        self.search_next(wnd)

    def skip_and_next(self, wnd):
        self._search_next(wnd)
        self.search_next(wnd)

    @commandid('searchdlg.search.prev')
    @norec
    @norerun
    def search_prev(self, wnd):
        if not self.get_search_str():
            return

        self.option.replace_to = self.get_replace_str()
        self._save_searchstr()
        self._save_replstr()

        self._search_prev(wnd)

        if self.lasthit:
            self._show_replace_msg(
                wnd, self.replace_and_prev, self.skip_and_prev)
        else:
            self._show_search_again(wnd, self.skip_and_prev, is_top=False)

    def replace_and_prev(self, wnd):
        self._repl_str(update_cursor=True)
        self.search_prev(wnd)

    def skip_and_prev(self, wnd):
        self.search_prev(wnd)

    def replace_all(self, wnd):
        self.option.replace_to = self.get_replace_str()
        self.option.text = self.get_search_str()

        self._save_searchstr()
        self._save_replstr()

        if not self.option.text:
            return
        self.lastsearch = None

        pos = 0
        n = 0
        lastpos = None
        with self.target.document.undo_group():
            while True:
                ret = self.target.document.mode.search_next(pos, self.option)
                self.lasthit = ret.span() if ret else None
                self.lastmatch = ret

                if ret:
                    self._repl_str(update_cursor=False)
                    pos = lastpos = self.lasthit[1]
                    n += 1
                else:
                    break

        if lastpos is not None:
            self.target.cursor.setpos(lastpos)

        kaa.app.messagebar.set_message('Replaced {} time(s)'.format(n))

    def on_esc_pressed(self, wnd, event):
        self._save_replstr()
        super().on_esc_pressed(wnd, event)

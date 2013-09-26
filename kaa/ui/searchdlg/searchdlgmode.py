import kaa
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.filetype.default import modebase, keybind as default_keybind
from . import searchcommand, keybind
from kaa.ui.msgbox import msgboxmode
from kaa.commands import editorcommand

SearchThemes = {
    'default':
    Theme([
        Style('default', 'default', 'Blue'),
        Style('caption', 'red', 'Green'),
        Style('checkbox', 'default', 'magenta', rjust=True, nowrap=True),
        Style('checkbox.checked', 'yellow', 'red', bold=True, rjust=True,
              nowrap=True),
        Style('checkbox.shortcut', 'green', 'magenta', underline=True,
              bold=True, rjust=True, nowrap=True),
    ])
}

LAST_SEARCH = modebase.SearchOption()

class SearchDlgMode(dialogmode.DialogMode):
    autoshrink = True
    def __init__(self, target):
        super().__init__()

        self.target = target
        self.initialpos = target.cursor.pos
        self.initialrange = target.screen.selection.get_range()
        self.lastsearch = None
        self.option = LAST_SEARCH

    def close(self):
        super().close()
        self.target = None

    def init_keybind(self):
        super().init_keybind()

        self.keybind.add_keybind(default_keybind.cursor_keys)
        self.keybind.add_keybind(default_keybind.edit_command_keys)
        self.keybind.add_keybind(default_keybind.emacs_keys)
        self.keybind.add_keybind(default_keybind.search_command_keys)
        self.keybind.add_keybind(default_keybind.macro_command_keys)

        self.keybind.add_keybind(keybind.searchdlg_keys)

    def init_commands(self):
        super().init_commands()

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands)

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self._searchcommands = searchcommand.SearchCommands()
        self.register_command(self._searchcommands)

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
            self.document.insert(
                self.document.marks['searchtext'][0], self.option.text)
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
        f.append_text('checkbox', '[&Next]',
                      shortcut_style='checkbox.shortcut',
                      on_shortcut=self.search_next)

        f.append_text('checkbox', '[&Prev]',
                      shortcut_style='checkbox.shortcut',
                      on_shortcut=self.search_prev)

    def _build_options(self, f):
        f.append_text('checkbox', '[&Ignore case]',
                      mark_pair='ignore-case',
                      on_shortcut=self.toggle_option_ignorecase,
                      shortcut_style='checkbox.shortcut',
                      shortcut_mark='shortcut-i')

        f.append_text('checkbox', '[&Word]',
                      mark_pair='word',
                      on_shortcut=self.toggle_option_word,
                      shortcut_style='checkbox.shortcut',
                      shortcut_mark='shortcut-w')

        f.append_text('checkbox', '[&Regex]',
                      mark_pair='regex',
                      on_shortcut=self.toggle_option_regex,
                      shortcut_style='checkbox.shortcut',
                      shortcut_mark='shortcut-r')

    def build_document(self):
        f = dialogmode.FormBuilder(self.document)
        self._build_input(f)
        self._build_buttons(f)
        self._build_options(f)

        self.update_option_style()

    def _set_option_style(self, mark, style,
                          shortcutmark, shortcutstyle):
        f, t = self.document.marks[mark]
        self.document.styles.setints(f, t, self.get_styleid(style))

        f = self.document.marks[shortcutmark]
        self.document.styles.setints(f, f+1, self.get_styleid(shortcutstyle))

    def _get_optionstylename(self, f):
        if f:
            return 'checkbox.checked'
        else:
            return 'checkbox'

    def update_option_style(self):
        style = self._get_optionstylename(self.option.ignorecase)
        self._set_option_style('ignore-case', style, 'shortcut-i',
                               'checkbox.shortcut')

        style = self._get_optionstylename(self.option.word)
        self._set_option_style('word', style, 'shortcut-w',
                               'checkbox.shortcut')

        style = self._get_optionstylename(self.option.regex)
        self._set_option_style('regex', style, 'shortcut-r',
                               'checkbox.shortcut')

    def _option_updated(self):
        self.update_option_style()
        self.document.style_updated(0, self.document.endpos())

    def toggle_option_ignorecase(self, wnd):
        self.option.ignorecase = not self.option.ignorecase
        self._option_updated()

    def toggle_option_word(self, wnd):
        self.option.word = not self.option.word
        self._option_updated()

    def toggle_option_regex(self, wnd):
        self.option.regex = not self.option.regex
        self._option_updated()

    def get_search_str(self):
        f, t = self.document.marks['searchtext']
        return self.document.gettext(f, t)

    def _show_searchresult(self, hit):
        if hit:
            self.target.cursor.setpos(hit[0])
            self.target.screen.selection.start = hit[0]
            self.target.screen.selection.end = hit[1]
            self.lastsearch = hit

            kaa.app.messagebar.set_message('found')
        else:
            kaa.app.messagebar.set_message('not found')

    def search_next(self, wnd):
        self.option.text = self.get_search_str()
        if self.option.text:
            if not self.lastsearch:
                if self.initialrange:
                    pos = self.initialrange[0]
                else:
                    pos = self.initialpos
            else:
                pos = self.lastsearch[1]

            if pos >= self.target.document.endpos():
                return

            ret = self.target.document.mode.search_next(self.target, pos, self.option)
            self._show_searchresult(ret)
            return ret

    def search_prev(self, wnd):
        self.option.text = self.get_search_str()
        if self.option.text:
            if not self.lastsearch:
                if self.initialrange:
                    pos = self.initialrange[1]
                else:
                    pos = self.initialpos
            else:
                pos = self.lastsearch[0]

            ret = self.target.document.mode.search_prev(self.target, pos, self.option)
            self._show_searchresult(ret)
            return ret

    def on_esc_pressed(self, wnd, event):
        self.target.activate()
        self.target = None
        wnd.get_label('popup').destroy()
        self.document.close()

    def on_document_updated(self, pos, inslen, dellen):
        super().on_document_updated(pos, inslen, dellen)
        if self.lastsearch:
            newstr = self.get_search_str()
            if newstr != self.option.text:
                self.lastsearch = None


class ReplaceDlgMode(SearchDlgMode):

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(keybind.replacedlg_keys)

    def init_commands(self):
        super().init_commands()
        self._replacecommands = searchcommand.ReplaceCommands()
        self.register_command(self._replacecommands)

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                  [dialogmode.MarkRange('searchtext'),
                   dialogmode.MarkRange('replacetext')])

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

    def _build_input(self, f):
        # search text
        f.append_text('caption', 'Search:')
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
        f.append_text('checkbox', '[&All]', 'start-all', 'end-all',
                      shortcut_style='checkbox.shortcut', on_shortcut=self.replace_all)

    def build_document(self):
        f = dialogmode.FormBuilder(self.document)
        self._build_input(f)
        self._build_buttons(f)
        self._build_options(f)

        self.update_option_style()

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
            msgdoc.close()

        msgdoc = msgboxmode.MsgBoxMode.show_msgbox(
            'Replace text?', ['&Yes', '&No', '&All', '&Cancel'], cb)

    def search_next(self, wnd):
        ret = super().search_next(wnd)
        if ret:
            self._show_replace_msg(wnd, self.replace_and_next, self.search_next)

    def replace_and_next(self, wnd):
        if self.lastsearch:
            f, t = self.lastsearch
            newstr = self.get_replace_str()
            self.target.document.mode.edit_commands.replace_string(
                self.target, f, t, newstr)

            f, t = self.lastsearch
            self.lastsearch = (f, f+len(newstr))
            self.search_next(wnd)

    def search_prev(self, wnd):
        ret = super().search_prev(wnd)
        if ret:
            self._show_replace_msg(wnd, self.replace_and_prev, self.search_prev)

    def replace_and_prev(self, wnd):
        if self.lastsearch:
            f, t = self.lastsearch
            newstr = self.get_replace_str()
            self.target.document.mode.edit_commands.replace_string(
                self.target, f, t, newstr)

            f, t = self.lastsearch
            self.lastsearch = (f, f+len(newstr))
            self.search_prev(wnd)

    def replace_all(self, wnd):
        self.option.text = self.get_search_str()
        if not self.option.text:
            return
        self.lastsearch = None
        newstr = self.get_replace_str()

        self.target.document.undo.beginblock()
        pos = 0
        n = 0
        try:
            while True:
                ret = self.target.document.mode.search_next(self.target, pos, self.option)
                if ret:
                    f, t = ret
                    self.target.document.mode.edit_commands.replace_string(
                        self.target, f, t, newstr, update_cursor=False)
                    self.lastsearch = (f, f+len(newstr))
                    pos = self.lastsearch[1]
                    n += 1
                else:
                    break
        finally:
            self.target.document.undo.endblock()

        if self.lastsearch:
            self.target.cursor.setpos(self.lastsearch[0])

        kaa.app.messagebar.set_message('Replaced {} time(s)'.format(n))

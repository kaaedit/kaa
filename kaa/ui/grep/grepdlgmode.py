import re
import os
import kaa
import kaa.utils
from kaa import encodingdef, consts
from kaa.keyboard import *
from kaa.ui.dialog import dialogmode
from kaa.filetype.default import modebase, keybind
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.ui.selectlist import filterlist
from kaa.ui.selectfile import selectfile
from kaa.ui.itemlist import itemlistmode
from kaa.ui.grep import grepmode


class GrepOption(modebase.SearchOption):
    RE = re

    def __init__(self):
        super().__init__()
        self.tree = True
        self.directory = '.'
        self.filenames = '*.*'
        self.encoding = 'utf-8'
        self.newline = 'auto'

    def clone(self):
        ret = super().clone()
        ret.tree = self.tree
        ret.directory = self.directory
        ret.filenames = self.filenames
        ret.encoding = self.encoding
        ret.newline = self.newline
        return ret

GrepOption.LASTOPTION = GrepOption()


GrepDlgThemes = {
    'basic': [],
}


grepdlg_keys = {
    '\r': ('grepdlg.field.next'),
    '\n': ('grepdlg.field.next'),
    up: ('grepdlg.history'),
    tab: ('grepdlg.select-dir'),
}


class GrepDlgMode(dialogmode.DialogMode):
    autoshrink = True

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
        grepdlg_keys,
    ]

    target = None

    def __init__(self, wnd=None):
        super().__init__()
        if isinstance(wnd.document.mode, grepmode.GrepMode):
            GrepOption.LASTOPTION = wnd.document.mode.grepoption
            self.target = wnd
        else:
            config = kaa.app.config

            if wnd and wnd.screen.selection.is_selected():
                f, t = wnd.screen.selection.get_selrange()
                s = wnd.document.gettext(f, t).split('\n')
                if s:
                    s = s[0].strip()
                    if s:
                        GrepOption.LASTOPTION.text = s

            grepdir = config.hist('grep_dirname').get()
            if grepdir:
                GrepOption.LASTOPTION.directory = grepdir[0][0]

            grepfiles = config.hist('grep_filename').get()
            if grepfiles:
                GrepOption.LASTOPTION.filenames = grepfiles[0][0]

        self.option = GrepOption.LASTOPTION

    def close(self):
        super().close()

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(GrepDlgThemes)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        cursor = dialogmode.DialogCursor(wnd,
                                         [dialogmode.MarkRange('searchtext'),
                                          dialogmode.MarkRange('directory'),
                                             dialogmode.MarkRange('filenames')])
        wnd.set_cursor(cursor)
        f, t = self.document.marks['searchtext']
        wnd.cursor.setpos(f)
        wnd.screen.selection.set_range(f, t)

    def build_document(self):
        with dialogmode.FormBuilder(self.document) as f:
            # search text
            f.append_text('caption', '   Search:')
            f.append_text('default', ' ')
            f.append_text('default', self.option.text, mark_pair='searchtext')
            f.append_text('default', '\n')

            # directory
            f.append_text('caption', 'Directory:')
            f.append_text('default', ' ')

            path = self.option.directory
            if path:
                p = kaa.utils.shorten_filename(path)
                path = p if len(p) < len(path) else path
            f.append_text('default', path, mark_pair='directory')
            f.append_text('default', '\n')

            # filename
            f.append_text('caption', 'Filenames:')
            f.append_text('default', ' ')
            f.append_text('default', self.option.filenames,
                          mark_pair='filenames')
            f.append_text('default', '\n')

            # working directory
            f.append_text('default', '(current dir)')
            f.append_text('default', ' ')
            f.append_text('default', os.getcwd())
            f.append_text('default', '\n')

            # buttons
            f.append_text('right-button', '[&Search]',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=self.run_grep)

            f.append_text('right-button', '[&Dir]',
                          mark_pair='select-dir',
                          shortcut_style='right-button.shortcut',
                          on_shortcut=self._select_dir)

            f.append_text('right-button', '[&Tree]',
                          mark_pair='search-tree',
                          on_shortcut=self.toggle_option_tree,
                          shortcut_style='right-button.shortcut',
                          shortcut_mark='shortcut-t')

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

            f.append_text(
                'right-button', '[&Encoding:{}]'.format(self.option.encoding),
                mark_pair='enc',
                shortcut_style='right-button.shortcut',
                on_shortcut=lambda wnd:
                wnd.document.mode.select_encoding(wnd))

            f.append_text(
                'right-button', '[&Newline:{}]'.format(self.option.newline),
                mark_pair='newline',
                shortcut_style='right-button.shortcut',
                on_shortcut=lambda wnd:
                wnd.document.mode.select_newline(wnd))

            self.update_option_style()
            kaa.app.messagebar.set_message(
                "Hit alt+S to begin search. Hit up to show history.")

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
        style = self._get_optionstylename(self.option.tree)
        self._set_option_style(
            'search-tree', 'right-button' + style, 'shortcut-t',
            'right-button.shortcut' + style)

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
        self.document.style_updated()

    def _select_dir(self, wnd):
        def cb(dir):
            wnd.set_visible(True)
            if dir:
                path = kaa.utils.shorten_filename(dir)
                self.set_dir(wnd, path)

        wnd.set_visible(False)
        dir = os.path.abspath(self.get_dir())
        selectfile.show_selectdir(dir, cb)

    @commandid('grepdlg.field.next')
    @norec
    @norerun
    def field_next(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']
        dirfrom, dirto = wnd.document.marks['directory']
        filefrom, fileto = wnd.document.marks['filenames']

        if searchfrom <= wnd.cursor.pos <= searchto:
            wnd.cursor.setpos(dirfrom)
            wnd.screen.selection.set_range(dirfrom, dirto)

        elif dirfrom <= wnd.cursor.pos <= dirto:
            wnd.cursor.setpos(filefrom)
            wnd.screen.selection.set_range(filefrom, fileto)

        else:
            wnd.cursor.setpos(searchfrom)
            wnd.screen.selection.set_range(searchfrom, searchto)

    @commandid('grepdlg.history')
    @norec
    @norerun
    def grep_history(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']
        dirfrom, dirto = wnd.document.marks['directory']
        filefrom, fileto = wnd.document.marks['filenames']

        if searchfrom <= wnd.cursor.pos <= searchto:
            def callback(result):
                if result:
                    f, t = wnd.document.marks['searchtext']
                    wnd.document.replace(f, t, result)
                    wnd.cursor.setpos(f)
                    f, t = wnd.document.marks['searchtext']
                    wnd.screen.selection.set_range(f, t)

            filterlist.show_listdlg('Recent searches',
                                    [s for s,
                                        info in kaa.app.config.hist('grep_text').get(
                                        )],
                                    callback)

        elif dirfrom <= wnd.cursor.pos <= dirto:
            def callback(result):
                if result:
                    f, t = wnd.document.marks['directory']
                    wnd.document.replace(f, t, result)
                    wnd.cursor.setpos(f)
                    f, t = wnd.document.marks['directory']
                    wnd.screen.selection.set_range(f, t)

            hist = []
            for p, info in kaa.app.config.hist('grep_dirname').get():
                path = kaa.utils.shorten_filename(p)
                hist.append(path if len(path) < len(p) else p)

            filterlist.show_listdlg('Recent directories',
                                    hist, callback)

        else:
            def callback(result):
                if result:
                    f, t = wnd.document.marks['filenames']
                    wnd.document.replace(f, t, result)
                    wnd.cursor.setpos(f)
                    f, t = wnd.document.marks['filenames']
                    wnd.screen.selection.set_range(f, t)

            filterlist.show_listdlg('Recent filenames',
                                    [s for s,
                                        info in kaa.app.config.hist('grep_filename').get(
                                        )],
                                    callback)

    @commandid('grepdlg.select-dir')
    @norec
    @norerun
    def select_dir(self, wnd):
        f, t = self.document.marks['directory']
        if f <= wnd.cursor.pos <= t:
            self._select_dir(wnd)

    def toggle_option_tree(self, wnd):
        self.option.tree = not self.option.tree
        self._option_updated()

    def toggle_option_ignorecase(self, wnd):
        self.option.ignorecase = not self.option.ignorecase
        self._option_updated()

    def toggle_option_word(self, wnd):
        self.option.word = not self.option.word
        self._option_updated()

    def toggle_option_regex(self, wnd):
        self.option.regex = not self.option.regex
        self._option_updated()

    def _get_encnames(self):
        return sorted(encodingdef.encodings + ['japanese'],
                      key=lambda k: k.upper())

    def select_encoding(self, wnd):
        encnames = self._get_encnames()

        def callback(n):
            if n is None:
                return

            enc = encnames[n]
            if enc != self.option.encoding:
                self.option.encoding = enc
                f, t = self.document.marks['enc']
                # [Encoding:{mode}]
                # 01234567890    10
                self.document.replace(f + 10, t - 1, self.option.encoding)

        doc = itemlistmode.ItemListMode.build(
            'Select character encoding:',
            encnames,
            encnames.index(self.option.encoding),
            callback)

        kaa.app.show_dialog(doc)

    def select_newline(self, wnd):
        def callback(n):
            if n is None:
                return

            nl = consts.NEWLINES[n]
            if nl != self.option.newline:
                self.option.newline = nl
                f, t = self.document.marks['newline']
                # [Newline:{mode}]
                # 0123456789    10
                self.document.replace(f + 9, t - 1, self.option.newline)

        doc = itemlistmode.ItemListMode.build(
            'Select newline mode:',
            consts.NEWLINES,
            consts.NEWLINES.index(self.option.newline),
            callback)

        kaa.app.show_dialog(doc)

    def get_search_str(self):
        f, t = self.document.marks['searchtext']
        return self.document.gettext(f, t)

    def get_dir(self):
        f, t = self.document.marks['directory']
        return self.document.gettext(f, t)

    def set_dir(self, wnd, dir):
        f, t = self.document.marks['directory']
        self.replace_string(
            wnd, f, t, dir, update_cursor=True)

    def get_files(self):
        f, t = self.document.marks['filenames']
        return self.document.gettext(f, t)

    def run_grep(self, wnd):
        self.option.text = self.get_search_str()
        self.option.directory = self.get_dir()
        self.option.filenames = self.get_files()

        if (self.option.text and self.option.directory and
                self.option.filenames):

            kaa.app.config.hist('grep_text').add(self.option.text)
            path = os.path.abspath(os.path.expanduser(
                self.option.directory))
            kaa.app.config.hist('grep_dirname').add(path)
            kaa.app.config.hist('grep_filename').add(self.option.filenames)

            grepmode.grep(self.option, self.target)

        wnd.get_label('popup').destroy()

    def on_esc_pressed(self, wnd, event):
        wnd.get_label('popup').destroy()
        kaa.app.messagebar.set_message("")

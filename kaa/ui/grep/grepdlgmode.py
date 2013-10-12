import kaa
from kaa.keyboard import *
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.filetype.default import modebase, keybind
from kaa.ui.msgbox import msgboxmode
from kaa.command import command, Commands, norec, norerun
from kaa.commands import editorcommand
from kaa.ui.selectlist import filterlist


class GrepOption:
    def __init__(self):
        self.text = ''
        self.ignorecase = True
        self.word = False
        self.regex = False
        self.tree = True
        self.directory = ''
        self.filename = ''

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

GrepOption.LASTOPTION = GrepOption()


GrepThemes = {
    'default':
        Theme([
            Style('default', 'default', 'Blue'),
            Style('caption', 'default', 'magenta'),
            Style('checkbox', 'default', 'magenta', rjust=True, nowrap=True),
            Style('checkbox.checked', 'yellow', 'red', bold=True, rjust=True,
                  nowrap=True),
            Style('checkbox.shortcut', 'green', 'magenta', underline=True,
                  bold=True, rjust=True, nowrap=True),
        ])
}


class GrepCommands(editorcommand.EditCommands):
    @command('grepdlg.field.next')
    @norec
    @norerun
    def field_next(self, wnd):
        searchfrom, searchto = wnd.document.marks['searchtext']
        dirfrom, dirto = wnd.document.marks['directory']
        filefrom, fileto = wnd.document.marks['filename']

        if searchfrom <= wnd.cursor.pos <= searchto:
            wnd.cursor.setpos(dirfrom)
            wnd.screen.selection.set_range(dirfrom, dirto)

        elif dirfrom <= wnd.cursor.pos <= dirto:
            wnd.cursor.setpos(filefrom)
            wnd.screen.selection.set_range(filefrom, fileto)

        else:
            wnd.cursor.setpos(searchfrom)
            wnd.screen.selection.set_range(searchfrom, searchto)

    def _show_histdlg(self, wnd, title, candidates, callback):
        doc = filterlist.FilterListInputDlgMode.build(
                title, callback)
        dlg = kaa.app.show_dialog(doc)
    
        filterlistdoc = filterlist.FilterListMode.build()
        dlg.add_doc('dlg_filterlist', 0, filterlistdoc)
        
        filterlistdoc.mode.set_candidates(candidates)
    
        list = dlg.get_label('dlg_filterlist')
        filterlistdoc.mode.set_query(list, '')
        dlg.on_console_resized()
        
    @command('grepdlg.history')
    @norec
    @norerun
    def grep_history(self, wnd):
        def callback(result):
            if result:
                f, t = wnd.document.marks['searchtext']
                wnd.document.replace(f, t, result)
            
        self._show_histdlg(wnd, 'Recent searches', 
                kaa.app.config.hist_grepstr, callback)
        

grepdlg_keys = {
    '\r': ('grepdlg.field.next'),
    '\n': ('grepdlg.field.next'),
    up: ('searchdlg.history'),
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

    def __init__(self):
        super().__init__()

        self.option = GrepOption.LASTOPTION

    def close(self):
        super().close()
        kaa.app.messagebar.set_message("")

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def init_commands(self):
        super().init_commands()

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands)

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self._grepcommands = GrepCommands()
        self.register_command(self._grepcommands)

    def init_themes(self):
        super().init_themes()
        self.themes.append(GrepThemes)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        cursor = dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('searchtext'), 
                    dialogmode.MarkRange('directory'), 
                    dialogmode.MarkRange('filename')])
        wnd.set_cursor(cursor)

        if self.option.text:
            self.document.insert(
                self.document.marks['searchtext'][0], self.option.text)
            wnd.screen.selection.set_range(*self.document.marks['searchtext'])
        wnd.cursor.setpos(self.document.marks['searchtext'][1])

    def build_document(self):
        f = dialogmode.FormBuilder(self.document)

        # search text
        f.append_text('caption', '   Search:')
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='searchtext')
        f.append_text('default', '\n')

        # directory
        f.append_text('caption', 'Directory:')
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='directory')
        f.append_text('default', '\n')

        # filename
        f.append_text('caption', ' Filename:')
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='filename')
        f.append_text('default', ' ')

        # buttons
        f.append_text('checkbox', '[&Search]',
                      shortcut_style='checkbox.shortcut',
                      on_shortcut=self.search_next)

        f.append_text('checkbox', '[&Tree]',
                      mark_pair='search-tree',
                      on_shortcut=self.toggle_option_tree,
                      shortcut_style='checkbox.shortcut',
                      shortcut_mark='shortcut-t')

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

        self.update_option_style()
        kaa.app.messagebar.set_message(
            "Hit alt+S to begin search. Hit up to show history.")

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
        style = self._get_optionstylename(self.option.tree)
        self._set_option_style('search-tree', style, 'shortcut-t',
                               'checkbox.shortcut')

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

    def get_search_str(self):
        f, t = self.document.marks['searchtext']
        return self.document.gettext(f, t)

    def search_next(self, wnd):
        kaa.app.config.hist_searchstr.add(self.get_search_str())
        return self._search_next(wnd)

    def on_esc_pressed(self, wnd, event):
        wnd.get_label('popup').destroy()


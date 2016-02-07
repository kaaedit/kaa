import os
import kaa
from kaa import document
from kaa.theme import Style
from kaa.ui.dialog import dialogmode
from kaa.filetype.default import keybind
from kaa.ui.itemlist import itemlistmode

FileInfoThemes = {
    'basic': [
        Style('button', 'Base3', 'Blue'),
        Style('shortcut', 'Base3', 'Orange', bold=True,
              underline=True, nowrap=True),
    ],
}


class FileInfoMode(dialogmode.DialogMode):
    autoshrink = True

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
    ]

    def __init__(self, target):
        super().__init__()

        self.target = target

    def close(self):
        super().close()
        self.target = None
        kaa.app.messagebar.set_message("")

    def init_themes(self):
        super().init_themes()
        self.themes.append(FileInfoThemes)

    def build_doc(self):
        self.document.delete(0, self.document.endpos())

        filename = self.target.document.get_filename()
        dir, fname = os.path.split(filename)

        mode = self.target.document.mode
        fileinfo = self.target.document.fileinfo

        with dialogmode.FormBuilder(self.document) as f:
            f.append_text('caption', '    File name: ')
            f.append_text('default', ' {}\n'.format(fname.replace('&', '&&')))

            f.append_text('caption', '    Directory: ')
            f.append_text('default', ' {}\n'.format(dir.replace('&', '&&')))

            f.append_text('default', '\n')

            f.append_text('caption', '         Mode: ')
            f.append_text('default', ' {}     '.format(mode.MODENAME))
            f.append_text('button', '[Change &Mode]\n',
                          on_shortcut=self._on_update_mode,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

            f.append_text('caption', '     Encoding: ')
            f.append_text('default', ' {}\n'.format(
                fileinfo.encoding if fileinfo else ''))

            f.append_text('caption', '      Newline: ')
            f.append_text('default', ' {}\n'.format(
                fileinfo.newline if fileinfo else ''))

            f.append_text('caption', '  Line number: ')
            f.append_text('default', ' {}       '.format(
                'Show' if mode.SHOW_LINENO else 'Hide'))
            f.append_text('button', '[Change &Line number]\n',
                          on_shortcut=self._on_update_lineno,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

            f.append_text('default', '\n')

            f.append_text('caption', '    Tab width: ',
                          shortcut_style='shortcut')
            f.append_text('default', ' {}          '.format(mode.tab_width))
            f.append_text('button', '[Change &Tab width]\n',
                          on_shortcut=self._on_update_tab,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

            f.append_text('caption', ' Indent width: ',
                          shortcut_style='shortcut')
            f.append_text('default', ' {}          '.format(mode.indent_width))
            f.append_text('button', '[Change &Indent width]\n',
                          on_shortcut=self._on_update_indent,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

            f.append_text('caption', '      Use tab: ',
                          shortcut_style='shortcut')
            f.append_text('default', ' {}        {}'.format(
                'Yes' if mode.indent_tab else 'No', '' if mode.indent_tab else ' '))
            f.append_text('button', '[Change &Use tab]\n',
                          on_shortcut=self._on_update_usetab,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

            f.append_text('caption', '  Auto Indent: ',
                          shortcut_style='shortcut')
            f.append_text('default', ' {}        {}'.format(
                'Yes' if mode.auto_indent else 'No', '' if mode.auto_indent else ' '))
            f.append_text('button', '[&Auto Indent]\n',
                          on_shortcut=self._on_update_autoindent,
                          shortcut_style='shortcut',
                          shortcut_need_alt=False)

    def is_cursor_visible(self):
        return 0   # hide cursor

    def on_str(self, wnd, s, overwrite=False):
        # does nothing
        pass

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()

    def _on_update_mode(self, c):
        modes = []
        for pkg in kaa.app.config.get_mode_packages():
            modes.append(pkg.FileTypeInfo.get_modetype())

        names = [mode.MODENAME for mode in modes]
        titles = ['%s' % name.replace('&', '&&') for name in names]

        def callback(n):
            if n is None:
                return

            mode = modes[n]
            if mode is not type(self.target.document.mode):
                self.target.document.setmode(mode())
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Select file mode:',
            titles,
            names.index(self.target.document.mode.MODENAME),
            callback)

        kaa.app.show_dialog(doc)

    def _on_update_lineno(self, c):
        values = ['Hide', 'Show']

        def callback(n):
            if n is None:
                return

            v = bool(n)
            if self.target.document.mode.SHOW_LINENO != v:
                self.target.document.mode.SHOW_LINENO = v
                self.target.document.update_screen(0, 0, 0)
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Show line number?',
            values,
            int(self.target.document.mode.SHOW_LINENO),
            callback)

        kaa.app.show_dialog(doc)

    def _on_update_tab(self, c):
        values = [str(i) for i in range(2, 9)]

        def callback(n):
            if n is None:
                return

            width = int(values[n])
            if self.target.document.mode.tab_width != width:
                self.target.document.mode.tab_width = width
                self.target.document.update_screen(0, 0, 0)
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Select tab width:',
            values,
            values.index(str(self.target.document.mode.tab_width)),
            callback)

        kaa.app.show_dialog(doc)

    def _on_update_indent(self, c):
        values = [str(i) for i in range(2, 9)]

        def callback(n):
            if n is None:
                return

            width = int(values[n])
            if self.target.document.mode.indent_width != width:
                self.target.document.mode.indent_width = width
                self.target.document.update_screen(0, 0, 0)
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Select indent width:',
            values,
            values.index(str(self.target.document.mode.indent_width)),
            callback)

        kaa.app.show_dialog(doc)

    def _on_update_usetab(self, c):
        values = ['No', 'Yes']

        def callback(n):
            if n is None:
                return

            v = bool(n)
            if self.target.document.mode.indent_tab != v:
                self.target.document.mode.indent_tab = v
                self.target.document.update_screen(0, 0, 0)
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Use tab for indent?',
            values,
            int(self.target.document.mode.indent_tab),
            callback)

        kaa.app.show_dialog(doc)

    def _on_update_autoindent(self, c):
        values = ['No', 'Yes']

        def callback(n):
            if n is None:
                return

            v = bool(n)
            if self.target.document.mode.auto_indent != v:
                self.target.document.mode.auto_indent = v
                self.target.document.update_screen(0, 0, 0)
                self.build_doc()

        doc = itemlistmode.ItemListMode.build(
            'Use auto indentation?',
            values,
            int(self.target.document.mode.auto_indent),
            callback)

        kaa.app.show_dialog(doc)


def show_fileinfo(target):
    doc = document.Document()
    mode = FileInfoMode(target)
    doc.setmode(mode)

    mode.build_doc()
    kaa.app.show_dialog(doc)
    kaa.app.messagebar.set_message(
        'Hit underlined character to update.')

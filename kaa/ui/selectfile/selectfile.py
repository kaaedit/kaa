import os, re, collections
import kaa
from kaa import document, encodingdef, utils, consts
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import selectlist
from kaa.ui.itemlist import itemlistmode
from kaa.ui.msgbox import msgboxmode

from kaa.theme import Theme, Style

from kaa.command import Commands, command
from kaa.keyboard import *
from kaa.commands import editorcommand
import kaa.filetype.default.keybind


FileOpenDlgThemes = {
    'default':
        Theme([
            Style('default', 'default', 'Blue'),
            Style('caption', 'Red', 'Yellow'),
            Style('dirname', 'Green', 'Blue', nowrap=True),
            Style('dirname-active', 'White', 'Red', nowrap=True),
            Style('filename', 'Yellow', 'Blue', nowrap=True),
            Style('filename-active', 'Yellow', 'Red', nowrap=True),
        ])
}

class DirFileListMode(selectlist.SelectItemList):
    dirname = None
    filename = None
    dirs = files = ()

    def init_themes(self):
        super().init_themes()
        self.themes.append(FileOpenDlgThemes)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)
        wnd.set_label('filelist', wnd)

    def set_dir(self, dirname):
        self.caption = self.dirname = os.path.abspath(
            os.path.expanduser(dirname))
        try:
            self.dirs, self.files = kaa.app.storage.listdir(self.dirname)
        except OSError as e:
            kaa.app.messagebar.set_message(str(e))
            self.dirs = []
            self.files = []

        # add '..' if dir is not root
        if self.dirname != '/' and os.path.exists(os.path.join(self.dirname, '..')):
            self.dirs.insert(0, '..')
        self.dirs = [name+'/' for name in self.dirs]

    def set_filename(self, filename):
        if filename:
            try:
                self.filterfunc = re.compile(filename, re.I).search
            except re.error:
                upper = filename.upper()
                self.filterfunc = lambda s:s.upper() in upper
        else:
            self.filterfunc = None

    def show_files(self):
        self.cursel = None
        dirs = [selectlist.SelectItem('dirname', name, name)
                    for name in self.dirs]
        files = [selectlist.SelectItem('filename', name, name)
                    for name in self.files]
        items = dirs + files
        if self.filterfunc:
            items = [item for item in items if self.filterfunc(item.text)]
        self.update_doc(items)

FileNameDlgThemes = {
    'default':
        Theme([
            Style('default', 'Red', 'Cyan'),
            Style('caption', 'Red', 'Yellow'),

            Style('option', 'default', 'magenta', rjust=True, nowrap=True),
            Style('option.shortcut', 'green', 'magenta', underline=True,
                  bold=True, rjust=True, nowrap=True),
        ])
}


fileopendlg_keys = {
    tab: 'fileopendlg.next',
    (shift, tab): 'fileopendlg.prev',
    '\r': 'fileopendlg.openfile',
    '\n': 'fileopendlg.openfile',
}

class FileOpenDlgCommands(Commands):
    def _update_filefield(self, wnd, filename):
        if filename and wnd.document.mode.get_filename() != filename:
            wnd.document.mode.set_filename(wnd, filename)

    @command('fileopendlg.prev')
    def prev(self, wnd):
        filelist = wnd.get_label('filelist')
        cursel = filelist.document.mode.sel_prev(filelist)
        if cursel:
            self._update_filefield(wnd, cursel.value)

    @command('fileopendlg.next')
    def next(self, wnd):
        filelist = wnd.get_label('filelist')
        cursel = filelist.document.mode.sel_next(filelist)
        if cursel:
            self._update_filefield(wnd, cursel.value)

    def _build_filename(self, wnd):
        filename = wnd.document.mode.get_filename()
        filename = os.path.expanduser(filename)

        if not os.path.isabs(filename):
            filelist = wnd.get_label('filelist')
            filename = os.path.join(filelist.document.mode.dirname, filename)

        return filename

    def show_filename(self, wnd, filename):
        # split filename into existing sub-directories and rest of filename.
        dir, rest = utils.split_existing_dirs(filename)

        # set existing directory as current dir.
        filelist = wnd.get_label('filelist')
        filelist.document.mode.set_dir(dir)

        # set rest of filename to filename filter.
        filelist.document.mode.set_filename(rest)

        filelist.document.mode.show_files()
        filelist.get_label('popup').on_console_resized()

        # set rest of filename filename field.
        wnd.document.mode.set_filename(wnd, rest)

    @command('fileopendlg.openfile')
    def openfile(self, wnd):
        filename = self._build_filename(wnd)
        if os.path.isfile(filename):
            wnd.document.mode.callback(filename, wnd.document.mode.encoding,
                                       wnd.document.mode.newline)
            popup = wnd.get_label('popup')
            popup.destroy()
            return

        if os.path.isdir(filename):
            if not filename.endswith(os.path.sep):
                filename += os.path.sep
        self.show_filename(wnd, filename)

class FilenameEditCommand(editorcommand.EditCommands):
    def on_edited(self, wnd):
        filename = wnd.document.mode.get_filename()
        if os.sep not in filename:
            filelist = wnd.get_label('filelist')
            filelist.document.mode.set_filename(filename)
            filelist.document.mode.show_files()
            filelist.get_label('popup').on_console_resized()

class OpenFilenameDlgMode(dialogmode.DialogMode):
    MAX_INPUT_HEIGHT = 4

    @classmethod
    def build(cls, newline, encoding, callback):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        mode.newline = newline if newline else kaa.app.config.DEFAULT_NEWLINE
        mode.encoding = encoding if encoding else kaa.app.config.DEFAULT_ENCODING
        mode.callback = callback

        f = dialogmode.FormBuilder(doc)
        f.append_text('caption', 'Filename:' )
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='filename')
        f.append_text('default', ' ')

        f.append_text('option', '[&Encoding:{}]'.format(mode.encoding), mark_pair='enc',
                      shortcut_style='option.shortcut',
                      on_shortcut=lambda wnd:wnd.document.mode.select_encoding(wnd))

        f.append_text('option', '[&Newline:{}]'.format(mode.newline), mark_pair='newline',
                      shortcut_style='option.shortcut',
                      on_shortcut=lambda wnd:wnd.document.mode.select_newline(wnd))

        return doc

    def close(self):
        super().close()
        kaa.app.messagebar.set_message("")

    def init_themes(self):
        super().init_themes()
        self.themes.append(FileNameDlgThemes)

    def init_keybind(self):
        self.keybind.add_keybind(kaa.filetype.default.keybind.edit_command_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.cursor_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.emacs_keys)
        self.keybind.add_keybind(fileopendlg_keys)

    def init_commands(self):
        super().init_commands()

        self.fileopendlg_commands = FileOpenDlgCommands()
        self.register_command(self.fileopendlg_commands)

        self.edit_commands = FilenameEditCommand()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands )

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('filename')])

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.CURSOR_TO_MIDDLE_ON_SCROLL = False
        wnd.set_cursor(self.create_cursor(wnd))
        wnd.cursor.setpos(self.document.marks['filename'][1])

        wnd.set_label('filename_field', self)
        kaa.app.messagebar.set_message("Hit tab/shift+tab to complete.")

    def calc_position(self, wnd):
        w, h = wnd.getsize()
        height = self.calc_height(wnd)
        height = min(height, self.MAX_INPUT_HEIGHT)
        top = wnd.mainframe.height - height - wnd.mainframe.MESSAGEBAR_HEIGHT
        return 0, top, wnd.mainframe.width, top+height

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()

    def get_filename(self):
        f, t = self.document.marks['filename']
        return self.document.gettext(f, t)

    def set_filename(self, wnd, s):
        f, t = self.document.marks['filename']
        self.document.replace(f, t, s)
        wnd.screen.selection.set_range(f, f+len(s))
        wnd.cursor.setpos(f+len(s))

    def select_encoding(self, wnd):
        def callback(n):
            enc = encodingdef.encodings[n]
            if enc != self.encoding:
                self.encoding = enc
                f, t = self.document.marks['enc']
                # [Encoding:{mode}]
                # 01234567890    10
                self.document.replace(f+10, t-1, self.encoding)

        doc = itemlistmode.ItemListMode.build(
            'Select character encoding:',
            encodingdef.encodings,
            encodingdef.encodings.index(self.encoding),
            callback)

        kaa.app.show_dialog(doc)

    def select_newline(self, wnd):
        def callback(n):
            nl = consts.NEWLINES[n]
            if nl != self.newline:
                self.newline = nl
                f, t = self.document.marks['newline']
                # [Newline:{mode}]
                # 0123456789    10
                self.document.replace(f+9, t-1, self.newline)

        doc = itemlistmode.ItemListMode.build(
            'Select newline mode:',
            consts.NEWLINES,
            consts.NEWLINES.index(self.newline),
            callback)

        kaa.app.show_dialog(doc)


def show_fileopen(filename, callback):
    filename = os.path.abspath(
        os.path.expanduser(filename))

    if os.path.isdir(filename) and not filename.endswith(os.path.sep):
        filename += os.path.sep

    doc = OpenFilenameDlgMode.build(None, None, callback)
    dlg = kaa.app.show_dialog(doc)

    filelist = DirFileListMode.build()
    dlg.add_doc('dlg_filelist', 0, filelist)
    filelist.mode.set_dir('.')
    filelist.mode.show_files()
    dlg.on_console_resized()
    return doc

class FileSaveAsDlgCommands(FileOpenDlgCommands):
    @command('fileopendlg.openfile')
    def openfile(self, wnd):
        filename = self._build_filename(wnd)

        # change current directory if filename is existing directory.
        if not os.path.isdir(filename):

            # Is filename contain valid filename?
            dir, rest = utils.split_existing_dirs(filename)
            if rest and os.sep not in rest:

                # query overwrite if file already exists.
                if os.path.exists(filename):
                    def choice(c):
                        if c in 'yY':
                            wnd.document.mode.callback(filename, wnd.document.mode.encoding,
                                       wnd.document.mode.newline)
                            wnd.get_label('popup').destroy()

                    msgboxmode.MsgBoxMode.show_msgbox(
                        'File `{}` already exists. Overwrite?: '.format(filename),
                        ['&Yes', '&No'], choice)
                else:
                    wnd.document.mode.callback(filename, wnd.document.mode.encoding,
                                       wnd.document.mode.newline)
                    wnd.get_label('popup').destroy()
                return

        return super().openfile(wnd)

class SaveAsFilenameDlgMode(OpenFilenameDlgMode):
    def init_commands(self):
        super().init_commands()

        self.fileopendlg_commands = FileSaveAsDlgCommands()
        self.register_command(self.fileopendlg_commands)


def show_filesaveas(filename, encoding, newline, callback):
    filename = os.path.abspath(
        os.path.expanduser(filename))
    if os.path.isdir(filename) and not filename.endswith(os.path.sep):
        filename += os.path.sep

    doc = SaveAsFilenameDlgMode.build(encoding, newline, callback)
    dlg = kaa.app.show_dialog(doc)

    filelist = DirFileListMode.build()
    dlg.add_doc('dlg_filelist', 0, filelist)

    doc.mode.fileopendlg_commands.show_filename(
        dlg.get_label('editor'), filename)


    return doc
import re, string, os, sys
import kaa
from kaa.command import Commands, command
from kaa import document, utils, encodingdef
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.keyboard import *
from kaa.ui.msgbox import msgboxmode
from kaa.ui.itemlist import itemlistmode

from kaa.commands import editorcommand
import kaa.filetype.default.keybind

config = kaa.app.config

FileOpenDlgTheme = Theme('default', [
    Style('default', 'default', 'Blue'),
    Style('caption', 'Magenta', 'Yellow'),
    Style('dirname', 'Green', 'Blue', nowrap=True),
    Style('dirname-active', 'red', 'Green', nowrap=True),
    Style('filename', 'Yellow', 'Blue', nowrap=True),
    Style('filename-active', 'Yellow', 'Green', nowrap=True),

])



class FileListDlgMode(dialogmode.DialogMode):
    filename_check = None
    filename = ''
    @classmethod
    def build(cls):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)
        mode._cur_items = ()

        return doc

    def set_dir(self, dirname):
        self.dirname = os.path.abspath(
            os.path.expanduser(dirname))
        try:
            self.dirs, self.files = kaa.app.storage.listdir(self.dirname)
        except OSError as e:
            kaa.app.messagebar.set_message(str(e))
            self.dirs = []
            self.files = []

        # add '..' if parent directory exists
        if os.path.exists(os.path.join(self.dirname, '..')):
            self.dirs.insert(0, '..')
        self.cursel = None

    def set_filename(self, filename):
        if filename:
            try:
                self.filename_check = re.compile(filename, re.I).search
            except re.error:
                upper = filename.upper()
                self.filename_check = lambda s:s.upper() in upper
        else:
            self.filename_check = None

        self.filename = filename
        self.cursel = None

    def build_doc(self):
        with self.document.suspend_update():
            self.document.delete(0, self.document.endpos())
            if self.filename_check:
                files = [file for file in self.files if self.filename_check(file)]
                dirs = [dir for dir in self.dirs if self.filename_check(dir)]
            else:
                files = self.files
                dirs = self.dirs

            self._cur_items = dirs+files

            f = dialogmode.FormBuilder(self.document)

            f.append_text('caption', self.dirname+':\n')
            for dir in dirs:
                start = f.document.endpos()
                f.append_text('dirname', dir.replace('&', '&&')+'/',
                              mark_pair=dir)
                f.append_text('default', ' ')

            for file in files:
                start = f.document.endpos()
                f.append_text('filename', file.replace('&', '&&'),
                              mark_pair=file)
                f.append_text('default', ' ')


    def init_keybind(self):
        pass

    def init_commands(self):
        pass

    def init_theme(self):
        self.theme = FileOpenDlgTheme

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('filename')])

    def get_cursor_visibility(self):
        return 0   # hide cursor

    def calc_position(self, wnd):
        l, t, r, b = super().calc_position(wnd)
        # display above FilenameDlgMode
        return (l, t-2, r, b-2)

    def on_esc_pressed(self, wnd, event):
        self.fileopendlg_commands.close(wnd)

    def _update_item_style(self, wnd, name, activate):
        if self.cursel in self.dirs:
            style = 'dirname'
        else:
            style = 'filename'

        if activate:
            style = style+'-active'

        f, t = self.document.marks[name]
        self.document.styles.setints(f, t, self.get_styleid(style))
        if activate:
            wnd.get_label('editor').cursor.setpos(f)

    def init_selitem(self, wnd):
        if self._cur_items:
            self.set_selitem(wnd, self._cur_items[0])

    def set_selitem(self, wnd, name):
        if self.cursel:
            self._update_item_style(wnd, self.cursel, False)
        self.cursel = None

        self._update_item_style(wnd, name, True)
        self.cursel = name

    def set_selnext(self, wnd):
        name = ''
        if not self.cursel:
            self.init_selitem(wnd)
            return

        try:
            idx = self._cur_items.index(self.cursel)
            if idx < len(self._cur_items)-1:
                name = self._cur_items[idx+1]
        except ValueError:
            pass

        if name:
            self._update_item_style(wnd, self.cursel, False)
            self._update_item_style(wnd, name, True)
            self.cursel = name

    def set_selprev(self, wnd):
        name = ''
        if not self.cursel:
            self.init_selitem(wnd)
            return

        try:
            idx = self._cur_items.index(self.cursel)
            if idx > 0:
                name = self._cur_items[idx-1]
        except ValueError:
            pass

        if name:
            self._update_item_style(wnd, self.cursel, False)
            self._update_item_style(wnd, name, True)
            self.cursel = name


FileNameDlgTheme = Theme('default', [
    Style('default', 'Magenta', 'Cyan'),
    Style('caption', 'Magenta', 'Yellow'),

    Style('option', 'default', 'magenta', rjust=True, nowrap=True),
    Style('option.shortcut', 'green', 'magenta', underline=True,
          bold=True, rjust=True, nowrap=True),
])

fileopendlg_keys = {
    tab: 'fileopendlg.next',
    (shift, tab): 'fileopendlg.prev',
    '\r': 'fileopendlg.openfile',
    '\n': 'fileopendlg.openfile',
}

class FileOpenDlgCommands(Commands):
    def _update_filefield(self, wnd):
        filelist = wnd.document.mode.filelist
        cursel = filelist.document.mode.cursel
        if cursel and wnd.document.mode.get_filename() != cursel:
            wnd.document.mode.set_filename(wnd, cursel)

    @command('fileopendlg.prev')
    def prev(self, wnd):
        filelist = wnd.document.mode.filelist
        filelist.document.mode.set_selprev(
            wnd.document.mode.filelist)
        self._update_filefield(wnd)

    @command('fileopendlg.next')
    def next(self, wnd):
        wnd.document.mode.filelist.document.mode.set_selnext(
            wnd.document.mode.filelist)
        self._update_filefield(wnd)

    def _build_filename(self, wnd):
        filelist = wnd.document.mode.filelist
        filename = wnd.document.mode.get_filename()
        filename = os.path.expanduser(filename)
        if not os.path.isabs(filename):
            filename = os.path.join(filelist.document.mode.dirname, filename)
        return filename

    def show_filename(self, wnd, filename):
        # split filename into existing sub-directories and rest of filename.
        filelist = wnd.document.mode.filelist
        dir, rest = utils.split_existing_dirs(filename)

        # set existing directory as current dir.
        filelist.document.mode.set_dir(dir)

        # set rest of filename to filename filter.
        filelist.document.mode.set_filename(rest)

        filelist.document.mode.build_doc()
        filelist.get_label('popup').on_console_resized()

        # set rest of filename filename field.
        wnd.document.mode.set_filename(wnd, rest)

    @command('fileopendlg.openfile')
    def openfile(self, wnd):
        filename = self._build_filename(wnd)
        if os.path.isfile(filename):
            wnd.document.mode.callback(filename, wnd.document.mode.encoding,
                                       wnd.document.mode.newline)
            self.close(wnd)
            return

        if os.path.isdir(filename):
            if not filename.endswith(os.path.sep):
                filename += os.path.sep
        self.show_filename(wnd, filename)

    @command('fileopendlg.complete')
    def completename(self, wnd):
        filename = wnd.document.mode.get_filename()
        if os.sep in filename:
            filename = self._build_filename(wnd)
            self.show_filename(wnd, filename)
        else:
            self.next(wnd)

    @command('fileopendlg.close')
    def close(self, wnd):
        # Destroy popup window
        popup = wnd.document.mode.filelist.get_label('popup')
        popup.destroy()
        wnd.document.mode.filelist = None

        popup = wnd.get_label('popup')
        popup.destroy()

class FilenameEditCommand(editorcommand.EditCommands):
    def on_edited(self, wnd):
        filename = wnd.document.mode.get_filename()
        if os.sep not in filename:
            filelist = wnd.document.mode.filelist
            filelist.document.mode.set_filename(filename)
            filelist.document.mode.build_doc()
            filelist.get_label('popup').on_console_resized()


class OpenFilenameDlgMode(dialogmode.DialogMode):
    min_height = 2

    @classmethod
    def build(cls, filelist, newline, encoding):
        buf = document.Buffer()
        doc = document.Document(buf)
        doc.undo = None
        mode = cls()
        doc.setmode(mode)

        mode.filelist = filelist
        mode.newline = newline if newline else config.DEFAULT_NEWLINE
        mode.encoding = encoding if encoding else config.DEFAULT_ENCODING
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

    @classmethod
    def show_dialog(cls):
        doc = cls.build()
        kaa.app.show_dialog(doc)
        return doc

    def init_keybind(self):
        self.keybind.add_keybind(kaa.filetype.default.keybind.edit_command_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.cursor_keys)
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

    def init_theme(self):
        self.theme = FileNameDlgTheme

    def create_cursor(self, wnd):
        return dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('filename')])

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.CURSOR_TO_MIDDLE_ON_SCROLL = False
        wnd.set_cursor(self.create_cursor(wnd))
        wnd.cursor.setpos(self.document.marks['filename'][1])

    def on_esc_pressed(self, wnd, event):
        self.fileopendlg_commands.close(wnd)

    def calc_position(self, wnd):
        w, h = wnd.getsize()
        height = self.calc_height(wnd)
        height = min(height, wnd.mainframe.height)
        top = wnd.mainframe.height - height -1 # todo: get height of messagebar
        return 0, top, wnd.mainframe.width, top+height

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
            encodingdef.encodings.index(self.encoding), callback)

        kaa.app.show_dialog(doc)

    def select_newline(self, wnd):
        def callback(n):
            nl = config.NEWLINES[n]
            if nl != self.newline:
                self.newline = nl
                f, t = self.document.marks['newline']
                # [Newline:{mode}]
                # 0123456789    10
                self.document.replace(f+9, t-1, self.newline)

        doc = itemlistmode.ItemListMode.build(
            'Select newline mode:',
            config.NEWLINES, config.NEWLINES.index(self.newline), callback)

        kaa.app.show_dialog(doc)

def show_fileopen(filename, callback):
    filename = os.path.abspath(
        os.path.expanduser(filename))

    if os.path.isdir(filename) and not filename.endswith(os.path.sep):
        filename += os.path.sep

    doc = FileListDlgMode.build()
    dlg = kaa.app.show_dialog(doc)

    doc = OpenFilenameDlgMode.build(dlg, config.DEFAULT_NEWLINE, config.DEFAULT_ENCODING)

    doc.mode.callback = callback
    dlg = kaa.app.show_dialog(doc)
    doc.mode.fileopendlg_commands.show_filename(
        dlg.get_label('editor'), filename)

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
                            self.close(wnd)

                    msgboxmode.MsgBoxMode.show_msgbox(
                        'File `{}` already exists. Overwrite?: '.format(filename),
                        ['&Yes', '&No'], choice)
                else:
                    wnd.document.mode.callback(filename, wnd.document.mode.encoding,
                                       wnd.document.mode.newline)
                    self.close(wnd)
                return

        return super().openfile(wnd)

    def on_str(self, wnd, s):
        return super().on_str(wnd, s)

    def on_commands(self, wnd, commandids):
        return super().on_commands(wnd, commandids)

class SaveAsFilenameDlgMode(OpenFilenameDlgMode):
    def init_commands(self):
        super().init_commands()

        self.fileopendlg_commands = FileSaveAsDlgCommands()
        self.register_command(self.fileopendlg_commands)

        self.edit_commands = FilenameEditCommand()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands )

def show_filesaveas(filename, encoding, newline, callback):
    filename = os.path.abspath(
        os.path.expanduser(filename))
    if os.path.isdir(filename) and not filename.endswith(os.path.sep):
        filename += os.path.sep

    doc = FileListDlgMode.build()
    dlg = kaa.app.show_dialog(doc)

    doc = SaveAsFilenameDlgMode.build(dlg, encoding, newline)
    doc.mode.callback = callback
    dlg = kaa.app.show_dialog(doc)

    doc.mode.fileopendlg_commands.show_filename(
        dlg.get_label('editor'), filename)

    return doc

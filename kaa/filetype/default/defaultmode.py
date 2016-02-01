import copy
import time
from collections import defaultdict, namedtuple
import kaa
from . import keybind, theme, modebase, menu


class DefaultMode(modebase.ModeBase):
    DOCUMENT_MODE = True
    MODENAME = 'default'
    SHOW_LINENO = False
    SHOW_BLANK_LINE = True
    VI_COMMAND_MODE = False

    KEY_BINDS = [
        keybind.app_keys,
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.addtional_edit_command_keys,
        keybind.emacs_keys,
        keybind.search_command_keys,
        keybind.macro_command_keys,
        keybind.rerun_keys,
    ]

    VI_KEY_BIND = [
        keybind.command_mode_keys
    ]

    VI_VISUAL_MODE_KEY_BIND = [
        keybind.visual_mode_keys
    ]
    VI_VISUAL_LINEWISE_MODE_KEY_BIND = [
        keybind.visual_linewise_mode_keys
    ]

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.KEY_BINDS)
        self.register_keys(self.keybind_vi_commandmode, self.VI_KEY_BIND)
        self.register_keys(self.keybind_vi_visualmode,
                           self.VI_VISUAL_MODE_KEY_BIND)
        self.register_keys(self.keybind_vi_visuallinewisemode,
                           self.VI_VISUAL_LINEWISE_MODE_KEY_BIND)

    def init_menu(self):
        self.menu = copy.deepcopy(menu.MENUS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(theme.DefaultThemes)

    def close(self):
        super().close()
        self.keybind_vi_commandmode.clear()
        self.keybind_vi_visualmode.clear()
        self.keybind_vi_visuallinewisemode.clear()

    def on_idle(self):
        if self.closed:
            return

        ret = super().on_idle()
        if not ret:
            ret = self.check_fileupdate()

        return ret

    INTERVAL_CHECKUPDATE = 10

    def check_fileupdate(self):
        if not self.DOCUMENT_MODE:
            return
        if not kaa.app.mainframe.is_idle():
            return

        t = time.time()
        if t - self._check_fileupdate < self.INTERVAL_CHECKUPDATE:
            return

        self._check_fileupdate = t
        if self.document.fileinfo:
            if self.document.fileinfo.check_update():
                kaa.app.file_commands.notify_fileupdated(self.document)

    def on_esc_pressed(self, wnd, event):
        # Pressing esc key starts command mode.
        if self.VI_COMMAND_MODE:
            is_available, command = self.get_command('editmode.command')
            if command:
                command(wnd)
                if kaa.app.macro.is_recording():
                    kaa.app.macro.record(1, command)

    def on_keypressed(self, wnd, event, s, commands, candidate):
        if not commands and not candidate:
            if not s or s[0] < ' ':
                msg = self.DEFAULT_MENU_MESSAGE or kaa.app.DEFAULT_MENU_MESSAGE
                kaa.app.messagebar.set_message(msg)

        return super().on_keypressed(wnd, event, s, commands, candidate)

    def _show_parenthesis(self, charattrs, pos):
        charattrs[pos] = self.get_styleid('parenthesis_cur')
        matchpos = self.find_match_parenthesis(pos)
        if matchpos is not None:
            charattrs[matchpos] = self.get_styleid('parenthesis_match')

    def update_charattr(self, wnd):
        pos = wnd.cursor.pos
        d = {}
        c = ''
        if pos < self.document.endpos():
            c = self.document.buf[pos]

        if c and (c in self.PARENTHESIS):
            self._show_parenthesis(d, pos)
        elif 1 < pos:
            c = self.document.buf[pos - 1]
            if c in self.PARENTHESIS_CLOSE:
                self._show_parenthesis(d, pos - 1)

        if d != wnd.charattrs:
            wnd.charattrs = d
            wnd.screen.style_updated()
            return True

    PARENTHESIS_OPEN = '({['
    PARENTHESIS_CLOSE = ')}]'
    PARENTHESIS = PARENTHESIS_OPEN + PARENTHESIS_CLOSE
    PARENSIS_PAIR = {o: c for (o, c) in
                     zip(PARENTHESIS_OPEN + PARENTHESIS_CLOSE,
                         PARENTHESIS_CLOSE + PARENTHESIS_OPEN)}

    def iter_parenthesis(self, posfrom):
        while True:
            pos = self.document.buf.findchr(
                self.PARENTHESIS, posfrom, self.document.endpos())

            if pos == -1:
                break

            attr = self.document.styles.getint(pos)
            yield pos, self.document.buf[pos], attr
            posfrom = pos + 1

    def iter_rev_parenthesis(self, posfrom):
        posfrom += 1
        while True:
            pos = self.document.buf.rfindchr(
                self.PARENTHESIS, 0, posfrom)

            if pos == -1:
                break

            attr = self.document.styles.getint(pos)
            yield pos, self.document.buf[pos], attr
            posfrom = pos

    def find_match_parenthesis(self, posfrom):
        opener = self.document.buf[posfrom]
        curattr = self.document.styles.getint(posfrom)

        d = defaultdict(int)
        if opener in self.PARENTHESIS_OPEN:
            f = self.iter_parenthesis
            key = (opener, curattr)
        else:
            f = self.iter_rev_parenthesis
            key = (self.PARENSIS_PAIR[opener], curattr)

        for pos, c, attr in f(posfrom):
            if c in self.PARENTHESIS_OPEN:
                d[(c, attr)] += 1
            else:
                d[(self.PARENSIS_PAIR[c], attr)] -= 1

            if d.get(key) == 0:
                return pos

    _headerinfo = namedtuple('_headerinfo',
                             ['token', 'parent', 'name', 'dispname', 'lineno', 'pos'])

    class HeaderInfo(_headerinfo):

        def get_parents(self):
            ret = []
            p = self.parent
            while p:
                ret.insert(0, p)
                p = p.parent
            return ret

    def get_headers(self):
        return ()

import datetime, time
import kaa
from kaa.keyboard import *
from kaa.theme import Style
from kaa.filetype.default import defaultmode
from kaa import document
from kaa.filetype.default import keybind
from kaa.command import commandid
from kaa.ui.git import commitdlgmode
from kaa.ui.viewdiff import viewdiffmode
from kaa.ui.msgbox import msgboxmode
from kaa.ui.dialog import dialogmode
from kaa.ui.viewdiff import viewdiffmode

from . import gitrepo



TZ = datetime.timezone(datetime.timedelta(seconds=time.timezone*-1), 
    time.tzname[0])

GitLogTheme = {
    'basic': [
        Style('default', 'White', 'Base01', False, False),
        Style('git-log-header', 'Orange', 'Base02', fillrow=True),

        # todo: right-button with rjust should be defined in another name.
        Style('right-button', 'Base3', 'Base02', rjust=True, nowrap=True),
        Style('right-button.checked', 'Base3', 'Orange', rjust=True,
              nowrap=True),
        Style('right-button.shortcut', 'Base3', 'Base02', underline=True,
              rjust=True, nowrap=True),
        Style('right-button.shortcut.checked', 'Base3', 'Orange',
              underline=True, rjust=True, nowrap=True),

    ],
}


log_keys = {
    tab: 'git.status.next',
#    right: 'git.status.next',
#    down: 'git.status.next',
    right: 'cursor.right',
    left: 'cursor.left',
    down: 'cursor.down',
    up: 'cursor.up',
    (shift, tab): 'git.status.prev',
#    left: 'git.status.prev',
#    up: 'git.status.prev',

    pagedown: 'cursor.pagedown',
    pageup: 'cursor.pageup',

    ' ': 'git.status.press',
    '\r': 'git.log.diff',
    '\n': 'git.log.diff',
    (alt, 'v'): 'git.log.prevpage',
    (alt, 't'): 'git.log.nextpage',
}


class GitLogMode(defaultmode.DefaultMode):
    # todo: rename key/command names
    SCREEN_NOWRAP = True
    DOCUMENT_MODE = False
    USE_UNDO = False

    KEY_BINDS = [
        keybind.app_keys,
        keybind.search_command_keys,
    ]

    _page_from = 0
    max_count = 100
    _commits = ()

    def init_keybind(self):
        self.register_keys(self.keybind, self.KEY_BINDS)
        self.keybind.add_keybind(log_keys)

    def init_themes(self):
        super().init_themes()
        self.themes.append(dialogmode.DialogThemes)
        self.themes.append(GitLogTheme)

    def on_str(self, wnd, s, overwrite=False):
        # does nothing
        pass

    def on_esc_pressed(self, wnd, event):
        is_available, command = self.get_command('file.close')
        command(wnd)

    def _set_log(self):
        self.document.delete(0, self.document.endpos())

        with dialogmode.FormBuilder(self.document) as f:
            f.append_text('git-log-header', 'git log')
            f.append_text('right-button', '[Pre&v 100]',
                          shortcut_style='right-button.shortcut')
            f.append_text('right-button', '[Nex&t 100]',
                          shortcut_style='right-button.shortcut')
#            f.append_text('right-button', '[&Grep]',
#                          shortcut_style='right-button.shortcut')
#            f.append_text('right-button', '[Pa&th]',
#                          shortcut_style='right-button.shortcut')
            f.append_text('git-log-header', '\n')

        default = self.get_styleid('default')
        self._commits = list(self._repo.iter_commits(max_count=self.max_count, skip=self._page_from))

        for x in self._commits:
            s = datetime.datetime.fromtimestamp(
                x.committed_date, TZ).strftime('%Y/%m/%d %H:%M:%S')
            self.document.append(s+' ', default)
            self.document.append('{:12s} '.format(x.author.name[:12]), default)
            msgs = filter(lambda l:l, (l.strip() for l in x.message.split('\n')))
            self.document.append(x.message.split('\n')[0]+'\n', default)

    def show_log(self, repo):
        self._repo = repo
        self.document.set_title('<git log>')
        self._set_log()

    @commandid('git.log.diff')
    def open_file(self, wnd):
        lineno = self.document.buf.lineno.lineno(wnd.cursor.pos)
        if lineno == 1:
            return
        commit = self._commits[lineno-2]
        d = self._repo.git.log('-1', '-c',  '--patch', commit.hexsha, pretty='format:')

        viewdiffmode.show_diff(d)

    @commandid('git.log.nextpage')
    def nextpage(self, wnd):
        self._page_from += len(self._commits)
        self._set_log()

    @commandid('git.log.prevpage')
    def prevpage(self, wnd):
        self._page_from -= self.max_count
        self._page_from = max(self._page_from, 0)
        self._set_log()

def show_git_log(d):
    repo = gitrepo.open_repo(d)
    doc = document.Document()
    mode = GitLogMode()
    doc.setmode(mode)

    mode.show_log(repo)
    kaa.app.show_doc(doc)

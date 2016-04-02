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

    ' ': 'git.status.press',
    '\r': 'git.status.open',
    '\n': 'git.status.open',
    'r': 'git.status.refresh',
    'c': 'git.commit',
    'a': 'git.add',
    'u': 'git.unstage',
    'd': 'git.status.diff',
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

    def show_log(self, repo):
        self._repo = repo
        self.document.set_title('<git log>')

        with dialogmode.FormBuilder(self.document) as f:
            f.append_text('git-log-header', 'git log')
            f.append_text('right-button', '[&Prev1000]',
                          shortcut_style='right-button.shortcut')
            f.append_text('right-button', '[&Next 1000]',
                          shortcut_style='right-button.shortcut')
            f.append_text('right-button', '[&Grep]',
                          shortcut_style='right-button.shortcut')
            f.append_text('right-button', '[Pa&th]',
                          shortcut_style='right-button.shortcut')
            f.append_text('git-log-header', '\n')

        default = self.get_styleid('default')
        for x in repo.iter_commits(max_count=1000):
            s = datetime.datetime.fromtimestamp(
                x.committed_date, TZ).strftime('%Y/%m/%d %H:%M:%S')
            self.document.append(s+' ', default)
            self.document.append('{:12s} '.format(x.author.name[:12]), default)
            self.document.append(x.message.split('\n')[0]+'\n', default)


def show_git_log(d):
    repo = gitrepo.open_repo(d)
    doc = document.Document()
    mode = GitLogMode()
    doc.setmode(mode)

    mode.show_log(repo)
    kaa.app.show_doc(doc)

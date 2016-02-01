import os, pathlib, bisect, sys, threading, socket
from git import Repo
from pathlib import Path
import kaa
from kaa.keyboard import *
from kaa.theme import Style
from kaa.filetype.default import defaultmode
from kaa import document
from kaa.filetype.default import keybind
from kaa.command import norec, norerun, commandid
from kaa.ui.git import commitdlgmode
from kaa.ui.viewdiff import viewdiffmode

GitTheme = {
    'basic': [
        Style('git-header', 'Cyan', None),
        Style('git-button', 'Orange', 'Base02'),
        Style('git-untracked', 'Orange', None),
        Style('git-not-staged', 'Red', None),
        Style('git-staged', 'Green', None),
    ],
}


status_keys = {
    tab: 'git.status.next',
    right: 'git.status.next',
    down: 'git.status.next',
    (shift, tab): 'git.status.prev',
    left: 'git.status.prev',
    up: 'git.status.prev',

    ' ': 'git.status.press',
    '\r': 'git.status.open',
    '\n': 'git.status.open',
    'r': 'git.status.refresh',
    'c': 'git.commit',
    'a': 'git.add',
    'u': 'git.unstage',
    'd': 'git.status.diff',
}


class GitStatusMode(defaultmode.DefaultMode):
    # todo: rename key/command names
    DOCUMENT_MODE = False
    USE_UNDO = False
    DELAY_STR = False
    DEFAULT_MENU_MESSAGE = 'r:refresh a:add u:unstage d:diff c:commit'

    KEY_BINDS = [
        keybind.app_keys,
        keybind.search_command_keys,
    ]

    def init_keybind(self):
        self.register_keys(self.keybind, self.KEY_BINDS)
        self.keybind.add_keybind(status_keys)

    def init_themes(self):
        super().init_themes()
        self.themes.append(GitTheme)

    def on_str(self, wnd, s, overwrite=False):
        # does nothing
        pass

    def on_esc_pressed(self, wnd, event):
        is_available, command = self.get_command('file.close')
        command(wnd)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)
        self.file_next(wnd)
        
    def _get_marks(self):
        return sorted(((v[0], v[1], k) for k, v in self.document.marks.items()), key=lambda o:o[1])

    def _get_next_mark(self, pos):
        marks = self._get_marks()
        starts = [v[0] for v in marks]
        start = idx = bisect.bisect_right(starts, pos)

        for idx in range(start, len(marks)):
            yield marks[idx]

        idx = 0
        for idx in range(0, start):
            yield marks[idx]
    
    def _get_prev_mark(self, pos):
        marks = self._get_marks()
        starts = [v[0] for v in marks]
        start = idx = bisect.bisect_left(starts, pos)

        for idx in range(start-1, -1, -1):
            yield marks[idx]

        for idx in range(len(marks)-1, start-1, -1):
            yield marks[idx]

    def _get_mark(self, pos):
        for f, t, name in self._get_marks():
            if f <= pos < t:
                return f, t, name

    def _get_file_mark(self, pos):
        ret = self._get_mark(pos)
        if ret:
            if ret[2].startswith(('s_', 'n_', 'u_')):
                return ret

    @commandid('git.status.open')
    def open_file(self, wnd):
        mark = self._get_file_mark(wnd.cursor.pos)
        if not mark:
            return
        f, t, name = mark
        self._repo.git.reset('HEAD', [name[2:]])

        is_available, command = self.get_command('file.close')
        command(wnd)

        is_available, command = self.get_command('file.open')
        command(None,
            filename=os.path.join(self._repo.working_dir, name[2:]))

    def _show_diff(self, s):
        doc = document.Document()
        doc.append(s)
        mode = viewdiffmode.ViewDiffMode()
        doc.setmode(mode)

        kaa.app.show_dialog(doc)


    @commandid('git.status.diff')
    def diff_file(self, wnd):
        mark = self._get_file_mark(wnd.cursor.pos)
        if not mark:
            return
        f, t, name = mark
        _trace(name)
        if name[:2] == 'n_':
            d = self._repo.git.diff(name[2:])
            self._show_diff(d)
        elif name[:2] == 's_':
            d = self._repo.git.diff('--cached', name[2:])
            self._show_diff(d)



    @commandid('git.status.next')
    def file_next(self, wnd):
        for mark in self._get_next_mark(wnd.cursor.pos):
            wnd.cursor.setpos(mark[0])
            break

    @commandid('git.status.prev')
    def file_prev(self, wnd):
        for mark in self._get_prev_mark(wnd.cursor.pos):
            wnd.cursor.setpos(mark[0])
            break

    @commandid('git.status.press')
    def status_press(self, wnd):
        mark = self._get_mark(wnd.cursor.pos)
        if not mark:
            return
        f, t, name = mark
        if name == 'b_refresh':
            self._refresh(wnd)

    @commandid('git.status.refresh')
    def status_refresh(self, wnd):
            self._refresh(wnd)

    @commandid('git.add')
    def git_add(self, wnd):
        mark = self._get_file_mark(wnd.cursor.pos)
        if not mark:
            return
        f, t, name = mark
        self._repo.git.add([name[2:]])

        self._refresh(wnd)

    @commandid('git.unstage')
    def git_unstage(self, wnd):
        mark = self._get_file_mark(wnd.cursor.pos)
        if not mark:
            return
        f, t, name = mark
        self._repo.git.reset('HEAD', [name[2:]])

        self._refresh(wnd)

    @commandid('git.commit')
    def git_commit(self, wnd):

        fname = 'pppp'
        if os.path.exists(fname):
            os.unlink(fname)

        exe = sys.executable
        git_edit = '{exe} -m kaa.ui.git.git_editor '.format(exe=sys.executable)
        self._repo.git.update_environment(KAA_SOCKNAME=fname, GIT_EDITOR=git_edit)


        git_result = None
        def f():
            nonlocal git_result
            try:
                git_result = self._repo.git.commit(with_extended_output=True)
            except Exception as e:
                git_result = e

            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                s.connect(fname)
                s.send(b'close')
                s.close()
            except FileNotFoundError:
                pass

        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.bind(fname)
            s.listen()

            t = threading.Thread(target=f, daemon=True)
            t.start()

            conn, addr = s.accept()
            if git_result:
                kaa.app.messagebar.set_message(' '.join(str(git_result).split('\n')))

            recv = conn.recv(4096)
            if recv == b'ok\n':
                filename = os.path.join(self._repo.git_dir, 'COMMIT_EDITMSG')
                doc = kaa.app.storage.openfile(filename, nohist=True, filemustexists=True)
                s = doc.gettext(0, doc.endpos())
                doc.close()

                doc = commitdlgmode.CommitDialogMode.build(s)
                # todo: bad interface
                doc.mode.commitmsg = filename
                doc.mode.conn = conn
                doc.mode.status_refresh = lambda :self.status_refresh(wnd)
                doc.mode.wait_for = t
                kaa.app.show_dialog(doc)
        finally:
            if os.path.exists(fname):
                os.unlink(fname)

        self._refresh(wnd)


    def _add_diff(self, d, style, mark_prefix):
        if d.new_file:
            f = self.document.append('new file:    ', style)
            t = self.document.append(d.b_path, style)
            self.document.marks[mark_prefix+d.b_path] = (f, t)
            
        elif d.deleted_file:
            f = self.document.append('deleted:     ', style)
            t = self.document.append(d.b_path, style)
            self.document.marks[mark_prefix+d.b_path] = (f, t)

        elif d.renamed:
            f = self.document.append('renamed:     ', style)
            t = self.document.append(d.rename_from, style)
            self.document.marks[mark_prefix+d.rename_from] = (f, t)

            f = self.document.append(' -> ', style)
            t = self.document.append(d.rename_to, style)
            self.document.marks[mark_prefix+d.rename_to] = (f, t)

        else:
            f = self.document.append('modified:    ', style)
            t = self.document.append(d.b_path, style)
            self.document.marks[mark_prefix+d.b_path] = (f, t)

    def _refresh(self, wnd):
        if wnd:
            lineno = self.document.buf.lineno.lineno(wnd.cursor.pos)

        # clear
        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())
        
        self._untracked_files = list(self._repo.untracked_files)

        self.document.set_title('<git status>')

        # todo: define lock_mark() method
        self.document.marks.locked = True
        indent = '    '
        try:
            style_header = self.get_styleid('git-header')
            style_button= self.get_styleid('git-button')
            style_staged = self.get_styleid('git-staged')
            style_not_staged = self.get_styleid('git-not-staged')
            style_untracked = self.get_styleid('git-untracked')

            f = self.document.append('On branch {repo.active_branch.name}\n'.format(repo=self._repo), style_header)
            t = self.document.append('<< Refresh >>', style_button)
            self.document.marks['b_refresh'] = (f, t)

            self.document.append('\n\n')
            
            # add staged files
            self.document.append('Changes to be committed:\n\n', style_header)
            d = self._repo.head.commit.diff()
            for c in d:
                self.document.append(indent)
                self._add_diff(c, style_staged, 's_')
                self.document.append('\n')

            # add not staged files
            self.document.append('\nChanges not staged for commit:\n\n', style_header)

            d = self._repo.index.diff(None)
            for c in d:
                self.document.append(indent)
                self._add_diff(c, style_not_staged, 'n_')
                self.document.append('\n')

            # add untracked files
            self.document.append('\n\nUntracked fies:\n\n', style_header)
            for f in self._untracked_files:
                self.document.append(indent)
                posfrom = self.document.endpos()
                self.document.append(f, style_untracked)
                posto = self.document.endpos()

                self.document.marks['u_'+f] = (posfrom, posto)
                self.document.append('\n')

        finally:
            self.document.marks.locked = False

        if wnd:
            pos = self.document.get_lineno_pos(lineno)
            tol = wnd.document.gettol(pos)
            for f, t, name in self._get_marks():
                if tol <= f:
                    break
            wnd.cursor.setpos(f)

        kaa.app.messagebar.set_message(self.DEFAULT_MENU_MESSAGE)

    def show_status(self, repo):
        self._repo = repo
        self._refresh(None)

def show_git_status(d):
    cur = Path(d).absolute()
    while not cur.joinpath('.git').is_dir():
        p = cur.parent
        if p == cur:
            raise RuntimeError('Not a git repogitory')
        cur = p

    repo_dir = str(cur)
    repo = Repo(repo_dir)

    doc = document.Document()
    mode = GitStatusMode()
    doc.setmode(mode)

    mode.show_status(repo)
    kaa.app.show_doc(doc)


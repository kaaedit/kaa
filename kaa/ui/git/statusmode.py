import os
import bisect
import sys
import threading
import socket
import tempfile
from git import Repo
from git import BaseIndexEntry
from pathlib import Path
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
from . import gitrepo

GitStatusTheme = {
    'basic': [
        Style('git-header', 'Cyan', None),
        Style('git-button', 'Orange', 'Base02'),
        Style('git-untracked', 'Orange', None),
        Style('git-not-staged', 'Red', None),
        Style('git-staged', 'Green', None),
    ],
}


status_keys = {
    right: 'git.status.next',
    down: 'git.status.next',
    left: 'git.status.prev',
    up: 'git.status.prev',
    pagedown: 'cursor.pagedown',
    pageup: 'cursor.pageup',

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
        self.themes.append(GitStatusTheme)

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
        return sorted(((v[0], v[1], k) for k, v in self.document.marks.items()), key=lambda o: o[1])

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

        for idx in range(start - 1, -1, -1):
            yield marks[idx]

        for idx in range(len(marks) - 1, start - 1, -1):
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

        is_available, command = self.get_command('file.close')
        command(wnd)

        f, t, name = mark

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

        if self._repo.head.is_valid():
            self._repo.git.reset('HEAD', [name[2:]])
        else:
            self._repo.git.rm('--cached', [name[2:]])

        self._refresh(wnd)

    @commandid('git.commit')
    def git_commit(self, wnd):

        fname = tempfile.mktemp()
        if os.path.exists(fname):
            os.unlink(fname)

        git_edit = '{exe} -m kaa.ui.git.git_editor '.format(exe=sys.executable)
        self._repo.git.update_environment(
            KAA_SOCKNAME=fname, GIT_EDITOR=git_edit)

        git_result = None

        def f():
            nonlocal git_result
            try:
                code, msg1, msg2 = git_result = self._repo.git.commit(
                    with_extended_output=True)
                # todo: check gitpython to know what they are...
                git_result = msg1 + msg2
            except Exception as e:
                git_result = e

            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                s.connect(fname)
                s.send(b'finished\n')
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
                kaa.app.messagebar.set_message(
                    ' '.join(str(git_result).split('\n')))

            def callback_commit():
                t.join()
                if git_result:
                    msg = str(git_result)
                    msgboxmode.MsgBoxMode.show_msgbox(
                        msg, ['&Ok'], lambda c: self.status_refresh(wnd), [
                            '\r', '\n'],
                        border=True)
                else:
                    self.status_refresh(wnd)

            recv = conn.recv(4096)
            if recv == b'ok\n':
                filename = os.path.join(self._repo.git_dir, 'COMMIT_EDITMSG')
                doc = kaa.app.storage.openfile(
                    filename, nohist=True, filemustexists=True)
                s = doc.gettext(0, doc.endpos())
                doc.close()

                doc = commitdlgmode.CommitDialogMode.build(s)
                # todo: bad interface
                doc.mode.commitmsg = filename
                doc.mode.conn = conn

                doc.mode.commit_callback = callback_commit
                kaa.app.show_dialog(doc)
            else:
                callback_commit()

        finally:
            if os.path.exists(fname):
                os.unlink(fname)

    def _add_new_file(self, indent, style, name, mark_prefix):
        mark = mark_prefix + name
        if mark in self.document.marks:
            return

        f = self.document.append(indent+'new file:    ', style)
        t = self.document.append(name, style)
        self.document.marks[mark] = (f, t)
        return True

    def _add_diff(self, indent, d, style, mark_prefix):
        if d.new_file:
            return self._add_new_file(indent, style, d.b_path, mark_prefix)

        elif d.deleted_file:
            mark = mark_prefix + d.b_path
            if mark in self.document.marks:
                return

            f = self.document.append(indent + 'deleted:     ', style)
            t = self.document.append(d.b_path, style)
            self.document.marks[mark] = (f, t)

        elif d.renamed:
            mark_from = mark_prefix + d.rename_from
            if mark_from in self.document.marks:
                return

            mark_to = mark_prefix + d.rename_to
            if mark_to in self.document.marks:
                return

            f = self.document.append(indent + 'renamed:     ', style)
            t = self.document.append(d.rename_from, style)
            self.document.marks[mark_from] = (f, t)

            f = self.document.append(' -> ', style)
            t = self.document.append(d.rename_to, style)
            self.document.marks[mark_to] = (f, t)

        else:
            mark = mark_prefix + d.b_path
            if mark in self.document.marks:
                return

            f = self.document.append(indent + 'modified:    ', style)
            t = self.document.append(d.b_path, style)
            self.document.marks[mark_prefix + d.b_path] = (f, t)

        return True

    def _refresh(self, wnd):
        if wnd:
            lineno = self.document.buf.lineno.lineno(wnd.cursor.pos)

        # clear
        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())
        self.document.set_title('<git status>')

        untracked_files = list(self._repo.untracked_files)

        # todo: define lock_mark() method
        self.document.marks.locked = True
        indent = '    '
        try:
            style_header = self.get_styleid('git-header')
            style_button = self.get_styleid('git-button')
            style_staged = self.get_styleid('git-staged')
            style_not_staged = self.get_styleid('git-not-staged')
            style_untracked = self.get_styleid('git-untracked')

            try:
                branch = 'On branch {repo.active_branch.name}'.format(repo=self._repo)
            except TypeError:
                branch = '(no branch)'

            f = self.document.append(branch+'\n\n', style_header)
            t = self.document.append('<< Refresh >>', style_button)
            self.document.marks['b_refresh'] = (f, t)

            self.document.append('\n\n')

            # unmerged
            unmerged = {}
            if self._repo.head.is_valid():
                d = self._repo.index.unmerged_blobs()
                for path, blobs in d.items():
                    stagemask = 0
                    for stage, blob in blobs:
                        stagemask |= (1 << (stage-1))   # see man git-merge, wt-status.c: unmerged_mask()

                    unmerged[path] = stagemask

            
            # add staged files
            unmerged_diffs = []
            self.document.append('Changes to be committed:\n\n', style_header)
            if self._repo.head.is_valid():
                d = self._repo.head.commit.diff()
                for c in d:
                    if c.b_path in unmerged:
                        unmerged_diffs.append(c)
                        continue

                    if self._add_diff(indent, c, style_staged, 's_'):
                        self.document.append('\n')
            else:
                files = [name for name, state in self._repo.index.entries]
                files.sort()
                for file in files:
                    if self._add_new_file(indent, style_staged, file, 's_'):
                        self.document.append('\n')

            # add unmerged files
            if unmerged_diffs:
                self.document.append('\nUnmerged paths:\n\n', style_header)
                for c in unmerged_diffs:
                    if self._add_diff(indent, c, style_staged, 'n_'):
                        self.document.append('\n')

            # add not staged files
            self.document.append(
                '\nChanges not staged for commit:\n\n', style_header)

            d = self._repo.index.diff(None)
            for c in d:
                if self._add_diff(indent, c, style_not_staged, 'n_'):
                    self.document.append('\n')

            # add untracked files
            self.document.append('\n\nUntracked fies:\n\n', style_header)
            for f in untracked_files:
                self.document.append(indent)
                posfrom = self.document.endpos()
                self.document.append(f, style_untracked)
                posto = self.document.endpos()

                self.document.marks['u_' + f] = (posfrom, posto)
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
    repo = gitrepo.open_repo(d)

    doc = document.Document()
    mode = GitStatusMode()
    doc.setmode(mode)

    mode.show_status(repo)
    kaa.app.show_doc(doc)

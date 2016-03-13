import os
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class GitCommands(Commands):

    def _get_cur_dir(self, wnd):
        if wnd.document.fileinfo:
            return wnd.document.fileinfo.dirname
        else:
            return os.getcwd()

    @commandid('git.status')
    @norec
    @norerun
    def status(self, wnd):
        from kaa.ui.git import statusmode
        statusmode.show_git_status(self._get_cur_dir(wnd))

    @commandid('git.log')
    @norec
    @norerun
    def log(self, wnd):
        from kaa.ui.git import logmode
        logmode.show_git_log(self._get_cur_dir(wnd))

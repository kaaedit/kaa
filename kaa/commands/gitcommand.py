import os
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun


class GitCommands(Commands):

    @commandid('git.status')
    @norec
    @norerun
    def status(self, wnd):
        from kaa.ui.git import statusmode
        if wnd.document.fileinfo:
            dirname = wnd.document.fileinfo.dirname
        else:
            dirname = os.getcwd()
        statusmode.show_git_status(dirname)

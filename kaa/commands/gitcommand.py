import os
import kaa
from kaa.command import Commands, commandid, is_enable, norec, norerun


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


import kaa
from kaa.command import Commands, command

class EditModeCommands(Commands):
    @command('editmode.command')
    def editmode_commandmode(self, wnd):
        wnd.document.mode.editmode_command(wnd)
        kaa.app.messagebar.set_message('You are in command mode now. Type `i` to return insert mode.')

    @command('editmode.insert')
    def editmode_insertmode(self, wnd):
        wnd.document.mode.editmode_insert(wnd)
        kaa.app.messagebar.set_message('You are in insert mode now. Type `ESC` to return command mode.')

    @command('editmode.visual')
    def editmode_visualmode(self, wnd):
        wnd.screen.selection.clear()
        wnd.document.mode.editmode_visual(wnd)

    @command('editmode.visual-linewise')
    def editmode_visualmode_linewise(self, wnd):
        wnd.screen.selection.clear()
        wnd.document.mode.screen_commands.select_cur_line(wnd)
        wnd.document.mode.editmode_visual_linewise(wnd)


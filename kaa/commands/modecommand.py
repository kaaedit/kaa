import kaa
from kaa.command import Commands, command

class ModeCommands(Commands):
    @command('mode.normal')
    def mode_nomalmode(self, wnd):
        wnd.document.mode.mode_normal(wnd)

    @command('mode.insert')
    def mode_insertmode(self, wnd):
        wnd.document.mode.mode_insert(wnd)

    @command('mode.visual')
    def mode_visualmode(self, wnd):
        wnd.screen.selection.clear()
        wnd.document.mode.mode_visual(wnd)

    @command('mode.visual-linewise')
    def mode_visualmode_linewise(self, wnd):
        wnd.screen.selection.clear()
        wnd.document.mode.screen_commands.select_cur_line(wnd)
        wnd.document.mode.mode_visual_linewise(wnd)


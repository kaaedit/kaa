import kaa
from kaa.command import Commands, commandid


class EditModeCommands(Commands):

    @commandid('editmode.command')
    def editmode_commandmode(self, wnd):
        wnd.document.mode.editmode_command(wnd)
        kaa.app.messagebar.set_message(
            'You are in command mode now. Type `i` to return insert mode.')

    @commandid('editmode.insert')
    def editmode_insertmode(self, wnd):
        wnd.document.mode.editmode_insert(wnd)
        kaa.app.messagebar.set_message(
            'You are in insert mode now. Type `ESC` to return command mode.')

    @commandid('editmode.replace')
    def editmode_replacemode(self, wnd):
        wnd.document.mode.editmode_replace(wnd)
        kaa.app.messagebar.set_message(
            'You are in replace mode now. Type `ESC` to return command mode.')

    @commandid('editmode.visual')
    def editmode_visualmode(self, wnd):
        wnd.screen.selection.clear()
        wnd.document.mode.editmode_visual(wnd)

    @commandid('editmode.visual-linewise')
    def editmode_visualmode_linewise(self, wnd):
        wnd.screen.selection.clear()
        tol = wnd.cursor.adjust_nextpos(
            wnd.cursor.pos, wnd.document.gettol(wnd.cursor.pos))
        wnd.screen.selection.begin_cursor_sel(tol)
        wnd.document.mode.editmode_visual_linewise(wnd)

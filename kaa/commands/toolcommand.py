import subprocess
import kaa
from kaa.command import Commands, command, is_enable, norec, norerun


class ToolCommands(Commands):
    @command('python.console')
    @norerun
    def pythonconsole(self, wnd):
        from kaa.ui.pyconsole import pythonconsolemode
        pythonconsolemode.show_console()

    @command('command.rerun')
    @norerun
    def reruncommand(self, wnd):
        mode = wnd.document.mode
        for commandid in kaa.app.lastcommands:
            is_available, command = mode.get_command(commandid)
            if not command:
                msg = 'command {!r} is not registered.'.format(commandid)
                kaa.app.messagebar.set_message(msg)
                kaa.log.error(msg)
                return
            command(wnd)

    @command('edit.paste-lines')
    @norerun
    def edit_pastelines(self, wnd):
        from kaa.ui.pastelines import pastelinesmode
        doc = pastelinesmode.PasteLinesMode.build(wnd)

        kaa.app.show_dialog(doc)

    @command('tools.execute-shell-command')
    @norerun
    def execute_shell_command(self, wnd):
        def callback(w, s):
            s = s.strip()
            if s:
                ret = subprocess.check_output(
                    s, stderr=subprocess.STDOUT,
                    shell=True,
                    universal_newlines=True)

                wnd.document.mode.edit_commands.put_string(wnd, ret)
                wnd.screen.selection.clear()
                
                kaa.app.messagebar.set_message(
                    "{} letters inserted".format(len(ret)))

                popup = w.get_label('popup')
                popup.destroy()

        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Shell command:', callback)
        kaa.app.messagebar.set_message("Execute shell command")

        kaa.app.show_dialog(doc)

    
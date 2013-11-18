import sys, os, curses, subprocess
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
                kaa.app.config.hist_shellcommands.add(s)
                ret = subprocess.check_output(
                    s, stderr=subprocess.STDOUT,
                    shell=True,
                    universal_newlines=True)

                wnd.document.mode.edit_commands.put_string(wnd, ret)
                wnd.screen.selection.clear()
                
                kaa.app.messagebar.set_message(
                    "{} letters inserted".format(len(ret)))

        hist = [s for s, info in kaa.app.config.hist_shellcommands.get()]
        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Shell command:', 
                    callback, history=hist)
        kaa.app.messagebar.set_message('Execute shell command')

        kaa.app.show_dialog(doc)

    def _exec_cmd(self, cmd):
        # todo: move to util
        import select, errno
        master, slave = os.pipe()
        with subprocess.Popen(cmd, shell=True, stdout=slave, 
                stderr=slave, bufsize=1,
                universal_newlines=True) as process:

            os.close(slave)

            output = os.fdopen(master)
            try:
                lines = []
                while process.poll() is None:
                    rlist, _, _ = select.select([master], [], [])
                    for f in rlist:
                        l = output.readline()
                        lines.append(l)
                        print(l, end='')
            finally:
                output.close()
                
            retcode = process.poll()
            if retcode:
                code = errno.errorcode.get(retcode)
                if code:
                    code = '(%s):' % code
                else:
                    code = ''
                
                msg = os.strerror(retcode)
                kaa.app.messagebar.set_message(
                    '{code}{msg}'.format(
                        code=code, msg=msg, retcode=retcode))

            return ''.join(lines)
            
    @command('tools.make')
    @norerun
    def execute_make(self, wnd):
        def callback(w, s):
            s = s.strip()
            if s:
                kaa.app.config.hist_makecommands.add(s)
                # todo: move these lines to kaa.cui.*
                curses.def_prog_mode()
                curses.endwin()
                try:
                    ret = self._exec_cmd(s)
                finally:
                    curses.reset_prog_mode()
                    wnd.mainframe.refresh()

                from kaa.ui.makeoutput import makeoutputmode
                makeoutputmode.show(s, ret)

        from kaa.ui.inputline import inputlinemode
        hist = [s for s, info in kaa.app.config.hist_makecommands.get()]
        value = 'make' if not hist else hist[0]
        doc = inputlinemode.InputlineMode.build('Make command:', callback,
                history=hist, value=value)
        kaa.app.messagebar.set_message('Execute command')

        kaa.app.show_dialog(doc)


============================
Kaa - console text editor
============================

Kaa is a small and easy CUI text editor for console/terminal emulator environments.

.. contents::
    :depth: 2


Overview
============

Kaa is an easy yet powerful text editor for console user interface, providing numerous features like 

- Macro recording.

- Undo/Redo.

- Multiple windows/frames.

- Syntax highlighting.

- Grep.

- Python console.

- Python debugger.

- Open source software(MIT).

- More to come!

.. image:: http://www.gembook.org/static/images/kaa_multiwindow.png

See http://kaaedit.github.io for more screen shots.


Kaa is easy!
------------

Kaa is very easy to learn in spite of its rich functionality. Only thing you need to remember is **"To display menu, hit F1 key or alt+'m' key"**. Most of basic features could be accessed from fancy menus by hitting underlined character in the menu items. You can use kaa as easy as you are with Notepad on MS-Windows.


Customizable
------------

Kaa is written in `Python <http://www.python.org/>`_. So, you can easily customize many aspects of kaa through simple Python scripts.


Cross platform
---------------------

Kaa is a CUI editor that runs on most of modern UN*X flavor operating systems like Linux or Mac OS X. Kaa requires Unicode friendly environment both platform running kaa and terminal emulator/console to interact with kaa.

Cygwin environment on Windows platform is not supported at this time, but will be tested after they provide Python 3.3 package.


Setup 
============


Requirements
------------

To run kaa, you need following component:

* Python 3.3 or later

* Development files for Python 3.3. For recent Debian/Ubuntu, you can install required libraries by ::

    $ sudo apt-get install python3-dev

* If your Python installation is not system-supplied package but built by yourself, please ensure you have installed ncurses library with wide character support before you built Python. Consult documentation of your platform for details. For recent Debian/Ubuntu, you can install required libraries by ::

    $ sudo apt-get install libncursesw5 libncurses5-dev libncursesw5-dev 
 
  After theses packages are installed, rebuild Python installation to take effect.

* Kaa can use system clipboard. To use clipboard on Unix platform, `xclip` command should be installed. For Ubuntu Linux, following command installs `xclip` command.

    .. code:: sh

       $ sudo apt-get install xclip

* UTF-8 locales

* (optional) Cython


Installation
-------------

Use easy_install3 or pip3 to install kaa from PyPI ::

   $ sudo easy_install3 -U kaaedit


Terminal setting
================

Keyboard setting
----------------

Kaa uses alt key for keyboard shortcut like `alt+k`. On most of recent Windows or Linux terminal, alt key works out of box. But on Mac OS X, Terminal app should be configured:

1. Select Preferences menu.
2. Open the Settings tab.
3. Open the keyboard tab.
4. Check `Use option as meta key`.

Or, if you use iTerm2 on Mac, you should configure:

1. Select Preferences menu.
2. Open the Profiles tab.
3. Open the Keys tab.
4. Check `Left option Key acts as: +Esc.` and `Right option Key acts as: +Esc.` button.

If you use Gnome terminal and wishes to access menu by F1 key, you should configure:

1. Select Edit | Keyboard shortcuts menu.
2. Scroll to the Help/Contents shortcut and change key from F1 to some another key.

Color setting
-------------

Kaa looks better with 256 color mode of terminal emulator. For Terminal.app on Mac OS X, you can set 256 color mode with following procedure:

1. Select Preferences menu.
2. Open the Settings tab.
3. Select `xterm-256color` for `"Declare terminal as"` field.

For iTerm2, you can set 256 color mode with following procedure:

1. Select Preferences menu.
2. Open the Profiles tab.
3. Open the Terminal tab.
4. Select `xterm-256color` for `"Report terminal type"` field.

Otherwise, you should manually update terminal setting. e.g., If you use bash, add following line to `~/.bashrc` file:

.. code:: sh

   $ export TERM=xterm-256color

For detail, see http://www.pixelbeat.org/docs/terminal_colours/#256 to enable 256 color on your terminal.


Command line options
====================

::

   kaa [-h] [--version] [--no-init] [--init-script INIT_SCRIPT] 
       [--palette PALETTE] [--term TERM] [file [file ...]]

-h, --help            show this help message and exit
--version             show version info and exit
--no-init             skip loading initialization script
--init-script INIT_SCRIPT  execute file as initialization script instead of default initialization file
--palette PALETTE     color palette. available values: dark, light.
--term TERM, -t TERM  specify terminal type
--command command, -x command   spefify kaa command id to execute at start-up e.g: kaa -x python.console / kaa -x tools.grep

Usage
=====

Using kaa is intuitive. Typing alphabet keys will update file as you expected. Functional keys like arrow or delete keys also works.


Using menu
-----------

To display menu, type F1 key or alt+m (type 'm' key with alt key). Each items in the menu has one underlined character. The menu item is executed by typing the underlined key with or without pressing alt key.

Typing escape key hides menu.


File menu
++++++++++

+------------+----------------------------------------------------+
| New        | Create new file.                                   |
+------------+----------------------------------------------------+
| Open       | Open existing file.                                |
+------------+----------------------------------------------------+
| File info  | Show file information. Also update per file        |
|            | settings of tab or indentation.                    |
+------------+----------------------------------------------------+
| View Diff  | Show difference between original file and current  |
|            | buffer.                                            |
+------------+----------------------------------------------------+
| Save       | Save current file.                                 |
+------------+----------------------------------------------------+
| Save As    | Save current file as new file.                     |
+------------+----------------------------------------------------+
| Close      | Close current frame.                               |
+------------+----------------------------------------------------+
| Save all   | Save all current files.                            |
+------------+----------------------------------------------------+
| Close all  | Close all frames.                                  |
+------------+----------------------------------------------------+
| [Recently] | Show recently used files menu.                     |
+------------+----------------------------------------------------+
| Quit       | Terminate kaa.                                     |
+------------+----------------------------------------------------+


Recently used files menu
~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+-----------------------------------------+
| Recently used files | Show list of recently used files.       |
+---------------------+-----------------------------------------+
| Recently used dirs  | Show list of recently used directories. |
+---------------------+-----------------------------------------+


Edit menu
+++++++++

+---------------------+-----------------------------------------+
| Cut                 | Cut selected text.                      |
+---------------------+-----------------------------------------+
| Copy                | Copy selected text.                     |
+---------------------+-----------------------------------------+
| Paste               | Paste from clipboard.                   |
+---------------------+-----------------------------------------+
| Paste History       | Paste from clipboard history.           |
+---------------------+-----------------------------------------+
| Undo                | Undo last modification.                 |
+---------------------+-----------------------------------------+
| Redo                | Redo last undo.                         |
+---------------------+-----------------------------------------+
| Search              | Search text.                            |
+---------------------+-----------------------------------------+
| Replace             | Replace text.                           |
+---------------------+-----------------------------------------+
| Complete            | Word completion.                        |
+---------------------+-----------------------------------------+
| [Convert]           | Show text convert menu.                 |
+---------------------+-----------------------------------------+


Text convert menu
~~~~~~~~~~~~~~~~~~~~

+---------------+----------------------------------------------------+
| Upper         | Convert selected text to upper case.               |
+---------------+----------------------------------------------------+
| Lower         | Convert selected text to lower case.               |
+---------------+----------------------------------------------------+
| Normalization | Convert selected text to Unicode Normalization     |
|               | Forms(NFKC).                                       |
+---------------+----------------------------------------------------+
| Full-width    | Convert alphabet and numbers in the selected text  |
|               | to full-width character.                           |
+---------------+----------------------------------------------------+


Code menu
+++++++++

Code menu differs among file types. Following items are typical in programming languages.

+---------------+----------------------------------------------------+
| Comment       | Insert line comment character at top of lines in   |
|               | selected region.                                   |
+---------------+----------------------------------------------------+
| Uncomment     | Delete line comment character at top of lines in   |
|               | selected region.                                   |
+---------------+----------------------------------------------------+
| Table of      | Show table of contents to move cursor.             |
| contents      |                                                    |
+---------------+----------------------------------------------------+


Macro menu
++++++++++

+---------------+----------------------------------------------------+
| Start record  | Start macro recording.                             |
+---------------+----------------------------------------------------+
| End record    | End macro recording.                               |
+---------------+----------------------------------------------------+
| Run macro     | Run last macro.                                    |
+---------------+----------------------------------------------------+


Tools menu
++++++++++

+-----------------+----------------------------------------------------+
| Grep            | Search text from disk.                             |
+-----------------+----------------------------------------------------+
| Paste lines     | Insert lines of text without auto indentation.     |
+-----------------+----------------------------------------------------+
| Shell command   | Execute external shell command and insert the      |
|                 | output.                                            |
+-----------------+----------------------------------------------------+
| Make            | Run ``make`` to compile source files and capture   |
|                 | error  messages. Use f9/10 key to traverse errors. |
+-----------------+----------------------------------------------------+
| Spell checker   | Run English spell checker.                         |
+-----------------+----------------------------------------------------+
| Python console  | Start python console.                              |
+-----------------+----------------------------------------------------+
| Python debugger | Start Python debugger.                             |
+-----------------+----------------------------------------------------+
| Python debugger | Wait for external debugger connection.             |
| server          |                                                    |
+-----------------+----------------------------------------------------+


Window menu
+++++++++++

+----------------+-------------------------------------------------+
| Frame list     | Show list of frame windows. Use left/right      |
|                | arrow key to change active frame.               |
+----------------+-------------------------------------------------+
| Split vert     | Split current window vertically.                |
+----------------+-------------------------------------------------+
| Split horz     | Split current window horizontally.              |
+----------------+-------------------------------------------------+
| Move separator | Move window separator. Use left/right arrow key | 
|                | to move separator.                              |
+----------------+-------------------------------------------------+
| Next window    | Activate next window.                           |
+----------------+-------------------------------------------------+
| Prev window    | Activate previous window.                       |
+----------------+-------------------------------------------------+
| Join window    | Join split window.                              |
+----------------+-------------------------------------------------+
| [Switch file]  | Show switch window menu.                        |
+----------------+-------------------------------------------------+


Switch file menu
+++++++++++++++++

+---------------------+-------------------------------------------------+
| Switch file         | Switch content of active window.                |
+---------------------+-------------------------------------------------+
| New file here       | Create new file to active window.               |
+---------------------+-------------------------------------------------+
| open file here      | Open existing file to active window.            |
+---------------------+-------------------------------------------------+
| Recently used files | Show list of recently used files.               |
+---------------------+-------------------------------------------------+
| Recently used dirs  | Show list of recently used directories.         |
+---------------------+-------------------------------------------------+


Key bindings
------------

Menu keys
+++++++++++++++++++

+---------------+----------------------------------------------------+
| F1, alt+m     | Show menu.                                         |
+---------------+----------------------------------------------------+
| Alt-w         | Show switch file menu.                             |
+---------------+----------------------------------------------------+


Cursor keys
++++++++++++++++

+--------------------+------------------------------------------------+
| left, Control+b    | Cursor left.                                   |
+--------------------+------------------------------------------------+
| right, Control+f   | Cursor right.                                  |
+--------------------+------------------------------------------------+
| up                 | Cursor up.                                     |
+--------------------+------------------------------------------------+
| down               | Cursor down.                                   |
+--------------------+------------------------------------------------+
| Control+p          | Move cursor to previous physical line.         |
+--------------------+------------------------------------------------+
| Control+n          | Move cursor to next physical line.             |
+--------------------+------------------------------------------------+
| Control+left,      | Move cursor to previous word boundary.         |
| Alt+b              |                                                |
+--------------------+------------------------------------------------+
| Control+right,     | Move cursor to next word boundary.             |
| Alt+f              |                                                |
+--------------------+------------------------------------------------+
| Alt+p, Page up     | Previous page.                                 |
+--------------------+------------------------------------------------+
| Alt+n, Page down   | Next page.                                     |
+--------------------+------------------------------------------------+
| Control+a, Home    | Move cursor to top of line.                    |
+--------------------+------------------------------------------------+
| Control+^          | Move cursor to first letter of line.           |
+--------------------+------------------------------------------------+
| Control+e, End     | Move cursor to end of line.                    |
+--------------------+------------------------------------------------+
| Alt+<, Control+Home| Move cursor to top of file.                    |
+--------------------+------------------------------------------------+
| Alt+>, Control+End | Move cursor to end of file.                    |
+--------------------+------------------------------------------------+
| Control+g          | Go to line number.                             |
+--------------------+------------------------------------------------+
| Control+t          | Table of contents.                             |
+--------------------+------------------------------------------------+


Text selection
+++++++++++++++++++

+--------------------+------------------------------------------------+
| Shift+left         | Select to previous character.                  |
+--------------------+------------------------------------------------+
| Shift+right        | Select to next character.                      |
+--------------------+------------------------------------------------+
| Shift+up           | Select to previous line.                       |
+--------------------+------------------------------------------------+
| Shift+down         | Select to next line.                           |
+--------------------+------------------------------------------------+
| Shift+Home         | Select text to top of line.                    |
+--------------------+------------------------------------------------+
| Shift+End          | Select text to end of line.                    |
+--------------------+------------------------------------------------+
| Control+Shift+Home | Selects text to top of file.                   |
+--------------------+------------------------------------------------+
| Control+Shift+End  | Select text to end of file.                    |
+--------------------+------------------------------------------------+
| Control+Space,     | Set mark to select text region.                |
| Control+@          |                                                |
+--------------------+------------------------------------------------+
| Alt+#              | Set mark to select text rectangularly.         |
+--------------------+------------------------------------------------+
| Alt+a              | Select all text.                               |
+--------------------+------------------------------------------------+
| Alt+c              | Select current word at first press. Subsequent |
|                    | press selects entire current line, and the     |
|                    | third press selects entire text                |
+--------------------+------------------------------------------------+


Text deletion
++++++++++++++++

+--------------------+------------------------------------------------+
| Backspace,         | Delete the character to the left.              |
| Control+h          |                                                |
+--------------------+------------------------------------------------+
| Delete,            | Delete the character at the cursor.            |
| Control+d          |                                                |
+--------------------+------------------------------------------------+
| Control+backspace, | Delete the word to the left.                   |
| Alt+h              |                                                |
+--------------------+------------------------------------------------+
| Control+Delete,    | Delete the word to the right.                  |
| Alt+d              |                                                |
+--------------------+------------------------------------------------+
| Control+k          | Delete the line to the right.                  |
+--------------------+------------------------------------------------+
| Alt+k              | Delete the current line.                       |
+--------------------+------------------------------------------------+


Clipboard
++++++++++++++++

+--------------------+------------------------------------------------+
| Control+v          | Paste from clipboard.                          |
+--------------------+------------------------------------------------+
| Control+x          | Cut selection.                                 |
+--------------------+------------------------------------------------+
| Control+c          | Copy selection.                                |
+--------------------+------------------------------------------------+
| Alt+v              | Paste from clipboard history.                  |
+--------------------+------------------------------------------------+


Undo/Redo
+++++++++++++++

+--------------------+------------------------------------------------+
| Control+z          | Undo last change.                              |
+--------------------+------------------------------------------------+
| Control+y          | Redo last undo.                                |
+--------------------+------------------------------------------------+


Search/Replace
+++++++++++++++++

+--------------------+------------------------------------------------+
| Control+s          | Search text.                                   |
+--------------------+------------------------------------------------+
| Alt+s              | Replace text.                                  |
+--------------------+------------------------------------------------+
| F2                 | Search prev.                                   |
+--------------------+------------------------------------------------+
| F3                 | Search next.                                   |
+--------------------+------------------------------------------------+

Other
+++++++++++++++

+--------------------+------------------------------------------------+
| F6                 | Toggle macro recording on/off.                 |
+--------------------+------------------------------------------------+
| F5                 | Run macro.                                     |
+--------------------+------------------------------------------------+
| Alt+.              | Run last executed edit command again.          |
+--------------------+------------------------------------------------+
| Tab                | Indent selected lines.                         |
+--------------------+------------------------------------------------+
| Shift+Tab          | Dedent selected lines.                         |
+--------------------+------------------------------------------------+
| Control+o          | Word completion.                               |
+--------------------+------------------------------------------------+
| Control+u Alt+!    | Execute command and insert the output.         |
+--------------------+------------------------------------------------+
| Alt+z              | Suspend kaa and back to shell.                 |
+--------------------+------------------------------------------------+



Replace dialog
--------------

When `regex` button is checked, `Replace` string is also regular expression string. In this case, special characters like `\\t` or `\\n` are converted to tab character and newline character. Also, back-reference character will be replaced to sub-string matched group in the search string. For example, when search string is `'(a+)(b+)'` and replace string is `'\\2\\1'`,  matched string `'aabb'` will be replaced to `'bbaa'`.


Grep dialog
------------

Grep dialog has three input field. `Search` is a plain text or regular expression string to search. `Directory` is a directory to start searching. If `Tree` button was checked, files are searched recursively. `Filenames` is space separated list of file spec in shell-style wild-cards (e.g., `*.txt *.py *.doc`). Up arrow key displays history of each input field.

In the grep result window, use F9 and F10 key to traverse matches forward/backward. 


Python console
--------------

You can type Python script as normal Python interpreter. To execute script, you should hit enter key at very last of the script. Otherwise, newline character is inserted as text editor. You can move cursor upper or below to edit multiline script.

To show script history window, hit alt+Enter key on the console.

Spell checker
--------------

To use spell checker, `PyEnchant <https://pypi.python.org/pypi/pyenchant>`_ module should be installed. 

On MAC OS-X install `enchant <http://www.abisource.com/projects/enchant/>`_ with homebrew before installing PyEnchant.

.. code:: sh

    $ brew install enchant
    $ pip-3.3 install PyEnchant


Make
--------------

``[Tools]|Make`` executes ``make`` command to build your files. You can alter command and options to build. To retrieve previous command and options, hit up cursor key to display history window.

Output of ``make`` displayed on the window. You can traverse source files cause of the error forth and back with f9 and f10 key.

Python debugger
---------------

.. warning::
   Python debugger is experimental at this point.
    

Kaa can be used as front-end of Python debugger module(``bdb``) running in another process. Although kaa itself requires Python 3.3 or later, you can use Python 2.6 or later in the target process. 

Starting debugger
++++++++++++++++++

There are three ways to start debugger.

kaadbg.run module
~~~~~~~~~~~~~~~~~~~~~~~~

``Kaadbg`` package executes your Python script with Python debugger connected to debugger window of kaa. Usually, ``kaadbg`` is Python package installed as a part of kaa. To use another Python interpreter than kaa installed, you can install ``kaadbg`` separately.

::

   $ sudo pip install -U kaadbg


Currently, ``kaadbg`` supports from Python 2.6 to Python 3.x.

To activate kaa remote debugger, select ``[Tools]|Python debugger server`` and enter port number to connect debugger(default 28110).

Next, open new terminal window and run following command in the terminal window.

::

    $ python -m kaadbg.run my_test_stript.py arg1 args


If you need use other port than `28110`, you should provide port number with ``-p`` option.

::

    $ python -m kaadbg.run -p 29000 my_test_stript.py arg1 args


set_trace
~~~~~~~~~~~~~~~~~~~~~~~~

Like Python's standard ``pdb`` module, you can import ``kaadbg`` package and call ``set_trace()`` to start debug session.

You should start activate kaa remote debugger by menu ``[Tools]|Python debugger server`` and enter port number to connect debugger(default 28110).

To connect kaa remote debugger, open your target script and insert following lines of code.

.. code:: python

    import kaadbg.debug
    kaadbg.debug.set_trace()

If you need use other port than `28110`, you should provide port number to ``set_trace()``.

.. code:: python

    import kaadbg.debug
    kaadbg.debug.set_trace(29000)

Now you can start your target script. Kaa remote debugger will be opened when ``kaadbg.debug.set_trace()`` is hit.


Run child process
~~~~~~~~~~~~~~~~~~~~~~~~

You can run your target script as child process of kaa to debug.

To start child process, select ``[Tools]|Python debugger`` in kaa menu and specify command line as follow.

::

    python2.7 -m kaadbg.run myscript.py arg1 arg2

Command line should starts with Python interpreter you use and ``-m kaadbg.run``. Name of target script and arguments follows.

Note that kaa doesn't capture standard output and standard error of target process, so you cannot see outputs of the target script. Also, standard input of the target process is closed just after command started.

Breakpoints
++++++++++++++++++

To set/unset breakpoints, select ``[Code]|Toggle Breakpoint`` in menu in editor. By default, ``f8`` key is bounded to this menu item.

While debugger window is opened, you can suspend the debugger window by escape key. After you finish to update breakpoints in editor window, select ``[Tools]|Python debugger`` menu again to resume debugger. To view list of current breakpoints, select *breakpoints* button with ``alt+E`` key.

Inspect variables
++++++++++++++++++

To see value of variables, select ``Expr`` on the debugger window by pressing ``alt+E`` key and enter Python expression you want to inspect like ``self.spam``.


Vi binding
----------

.. warning::
   Python debugger is experimental at this point.

Kaa currentry supports some basic vi-like key bindings, but are disabled by default. To activate vi bindings, create `~/.kaa/__kaa__.py` file with following lines.

.. code:: python

   from kaa.filetype.default.defaultmode import DefaultMode
   DefaultMode.VI_COMMAND_MODE = True


Command mode
++++++++++++++++++

Unlike vi, kaa is in insert-mode at start up. Hit escape key to move to command mode.

mode commands
~~~~~~~~~~~~~~~~~~~~~~~~

+--------------------+------------------------------------------------+
| i                  | Insert mode.                                   |
+--------------------+------------------------------------------------+
| R                  | Replace mode.                                  |
+--------------------+------------------------------------------------+
| A                  | Append text after the end of line.             |
+--------------------+------------------------------------------------+
| v                  | Characterwise visual mode.                     |
+--------------------+------------------------------------------------+
| V                  | Linewise visual mode.                          |
+--------------------+------------------------------------------------+


cursor commands
~~~~~~~~~~~~~~~~~~~~~~~~

+--------------------+------------------------------------------------+
| h                  | Cursor right.                                  |
+--------------------+------------------------------------------------+
| l                  | Cursor left.                                   |
+--------------------+------------------------------------------------+
| k                  | Cursor up.                                     |
+--------------------+------------------------------------------------+
| j                  | Cursor down.                                   |
+--------------------+------------------------------------------------+
| w                  | Cursor word right.                             |
+--------------------+------------------------------------------------+
| b                  | Cursor word left.                              |
+--------------------+------------------------------------------------+
| 0                  | Cursor to top of line.                         |
+--------------------+------------------------------------------------+
| ^                  | Cursor to first character of line.             |
+--------------------+------------------------------------------------+
| $                  | Cursor to end of line.                         |
+--------------------+------------------------------------------------+
| gg                 | Cursor to top of file.                         |
+--------------------+------------------------------------------------+
| G                  | Cursor to end of file.                         |
+--------------------+------------------------------------------------+
| Control+b          | Page up.                                       |
+--------------------+------------------------------------------------+
| Control+f          | Page down.                                     |
+--------------------+------------------------------------------------+


Edit commands
~~~~~~~~~~~~~~~~

+--------------------+------------------------------------------------+
| r                  | Replace a character.                           |
+--------------------+------------------------------------------------+
| x                  | Delete a character.                            |
+--------------------+------------------------------------------------+
| d                  | Delete to next move.                           |
+--------------------+------------------------------------------------+
| u                  | Undo last edit.                                |
+--------------------+------------------------------------------------+
| Control+r          | Redo last undo.                                |
+--------------------+------------------------------------------------+
| y                  | Copy selection.                                |
+--------------------+------------------------------------------------+


Customization
==================

Kaa executes a Python script file at `~/.kaa/__kaa__.py` on start up. You can write Python script to customize kaa as you like.


Change default color palette
----------------------------------

To change default color palette, you can modify kaa.app.DEFAULT_PALETTE.

.. code:: python

   import kaa
   kaa.app.DEFAULT_PALETTE = 'light'  # Use `light' palette. Default is `dark'


Customize editor mode
-------------------------------

Each file type has file editor mode. `kaa.filetype.default import defaultmode` is base class of all text file modes. You can change attributes of filetype classes.

Show line numbers
+++++++++++++++++++++++++++

To show line number in editor screen, you can update `SHOW_LINENO` attribute of file mode classes.

.. code:: python

   from kaa.filetype.default import defaultmode
   defaultmode.DefaultMode.SHOW_LINENO = True


To show line number in HTML mode, you should change attribute of htmlmode.HTMLMode class.

.. code:: python

   # Show line number in HTML mode
   from kaa.filetype.html import htmlmode
   htmlmode.HTMLMode.SHOW_LINENO = True


File type customization hook
-------------------------------

Each mode object calls setup function to customize. `kaa.addon.setup()` decorator registers setup function.

.. code:: python

    setup(filemode='kaa.filetype.default.defaultmode.DefaultMode')


Setup function is called when mode object is created. In the setup function, you can customize various aspect of file type object.


Customize keybind
++++++++++++++++++++++++++

`mode.add_keybinds()` method registers custom key bind.

.. code:: python

    add_keybinds(self, editmode='input', keys=None):



`editmode` is a name of editmode which should be one of `input`, `command`, `visual` or `visualline`. `keymap` is a dictionary of keybind and command name.


Following example assign `Control+x 2` key to split window as Emacs.

.. code:: python

    from kaa.addon import *

    @setup('kaa.filetype.default.defaultmode.DefaultMode')
    def my_keybind(mode):
        mode.add_keybinds(keys={
            ((ctrl, 'x'), '2'): 'editor.splithorz'   # Assign C-x 2 to split window.
        })

Create custom command
+++++++++++++++++++++++++++++++

`kaa.command.commandid()` decorator declare a function as kaa's editor command.

.. code:: python

    commandid(commandid)

`commandid` is a unique command name in string.

Command functions can be registered to mode objects.

To register commands to mode, use `add_command()` method.

.. code:: python

    add_command(command)

`command` is a command function.

.. code:: python

    from kaa.addon import *
    
    # sample command to insert text at the top of file.
    @commandid('test.command')
    def testcommand(wnd):
        wnd.cursor.setpos(0)
        wnd.document.mode.put_string(wnd, 'sample text\n')

    @setup('kaa.filetype.default.defaultmode.DefaultMode')
    def command_sample(mode):

        # register command to the mode
        mode.add_command(testcommand)

        # add key bind th execute 'test.command'
        mode.add_keybinds(keys={
            (alt, '1'): 'test.command'   # Assign alt-1 to test.command
        })


Change color theme
++++++++++++++++++++++++++++++

Function `mode.add_theme()` could be used to customize color theme.

.. code:: python

    def add_theme(theme)

`theme` is a dictionary of theme name and list of styles. Currently, the only valid theme name is `basic`.

.. code:: python

    @setup('kaa.filetype.default.defaultmode.DefaultMode')
    def theme_sample(mode):

        # update foreground color of comments to red.
        mode.add_theme({
        'basic': [
           Style('default', 'red', None),
        ]
    }


Hacking
==========

You can get the recent source code from `github <https://github.com/kaaedit/kaa.git>`_.

.. code:: sh

   $ git clone https://github.com/kaaedit/kaa.git

To run test, you need to install `py.test <http://pytest.org/latest/>`_

.. code:: sh

   $ pip-3.3 install -U pytest
   $ cd kaa
   $ py.test

There is an experimental script to run freeze to build standalone kaa binary file.
To freeze kaa,  You must proceed with the following steps: 

1. Apply following two patches to your Python 3.3 installation.

   - http://bugs.python.org/issue11824
   - http://bugs.python.org/issue16047

2. Clone kaa source code.

.. code:: sh

   $ git clone https://github.com/kaaedit/kaa.git

3. In source directory of kaa, cd to kaa/freezing directory.

.. code:: sh

   $ cd kaa/freezing

4. Edit PYTHON variable in build.sh for your environment.

5. run build.sh

.. code:: sh

   $ ./build.sh

6. Check if freezing/dist/kaa exists.


Acknowledgments
=================

I really appreciate for your help.

* `Allan Clark <https://github.com/allanderek>`_


Links
==========

- `Github project page <http://kaaedit.github.io/>`_

- `Github repository <http://github.com/kaaedit/kaa>`_

- `Python Package Index(PyPI) <http://pypi.python.org/pypi/kaaedit/>`_

- `Twitter account to notify new releases <https://twitter.com/kaaedit>`_


Version history
=================

0.54.0 - 2023.1.14
--------------------

- Support Python 3.10 

0.53.0 - 2016.8.8
--------------------

- Display git log.

- Display unmerged diffs in git status screen.

- Fix clipboard error in Linux.

- Autocomplete around puctuation now works better.


0.52.0 - 2016.2.6
--------------------

- Display result of git commit command.

- Stage/unstage in no-commit repogitory now works.


0.51.0 - 2016.2.4
--------------------

- git status doesn't work if git has no commit.

- Stop Emacs-style set-mark command to clear ongoing-selection.

- Normalize Short-key of menu items. Now you can use double-width-F letter to open File menu.


0.50.0 - 2016.2.2
--------------------

- Add git support.

- [Markdown] Recognize nested lists.

0.49.0 - 2016.1.16
--------------------

- [CSS] Improve syntax highlight.

- Deprecate old addon functions. Use kaa.addon.setup() instead.

- Add suspend command to send kaa to the background. Bound to `alt-Z` key by default.

0.48.0 - 2015.12.28
--------------------

- Pasting long text to Python console was failed.

- [CSS] Highlight real number without preceding digits.

- Fix bug if diaog size is greater than screen size.


0.47.0 - 2015.12.10
--------------------

- Range of word in word completion is fixed.

- Use X11 clipboard only if environment variable ``DISPLAY`` is provided.

- Fix bug if diaog size is greater than screen size.


0.46.0 - 2015.11.06
--------------------

- Cursor word-right/left now skips white-space.

- Initial directory of file-open dialog is same directory as file now active.

- Various highlighting bugs.

0.45.0 - 2015.10.27
--------------------

- Handle terminal resize in Python 3.5.

- Reworked syntax highligh.

- [CSS mode] Highlight @media rules.



        
Copyright 
=========================

Copyright (c) 2013 - 2016 Atsuo Ishimoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

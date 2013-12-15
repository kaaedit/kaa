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

- Python debugger.

- Open source software(MIT).

- More to come!

.. image:: http://www.gembook.org/static/images/kaa_multiwindow.png

See http://kaaedit.github.io for more screen shots.


Kaa is easy!
------------

Kaa is very easy to learn in spite of its rich functionality. Only thing you need to remember is **"To display menu, hit F1 key or alt+'/' key"**. Most of basic feartures could be accessed from fancy menus by hitting underlined character in the menu items. You can use kaa as easy as you are with Notepad on MS-Windows.


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

* If your Python installation is not system-supplyed package but built by yourself, please ensure you have installed ncurses library with wide character support before you built Python. Consult documentation of your platform for details. For recent Debian/Ubuntu, you can install required libraries by ::

    $ sudo apt-get install libncursesw5 libncurses5-dev libncursesw5-dev 
 
  After theses packages are installed, rebuild Python installation to take effect.

* Kaa can use system clipboard. To use clipboard on Unix platform, `xsel` command should be installed. For Ubuntu linux, following command installs `xsel` command.

    .. code:: sh

       $ sudo apt-get install xsel

* UTF-8 locales

* (optional) Cython


Installation
-------------

Use easy_install3 or pip3 to install kaa from PyPI ::

   $ sudo easy_install3 -U kaaedit


Command line options
====================

To start kaa, type ::

    usage: kaa [-h] [--version] [--no-init] [--init-script INIT_SCRIPT]
               [--palette PALETTE] [--term TERM]
               [file [file ...]]
    
    positional arguments:
      file
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             show version info and exit
      --no-init             skip loading initialization script
      --init-script INIT_SCRIPT
                            execute file as initialization script instead of
                            default initialization file
      --palette PALETTE     color palette. available values: dark, light.
      --term TERM, -t TERM  specify terminal type


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

Kaa looks better with 256 color mode of terminal emulator. With Terminal.app you can set 256 color mode:

1. Select Preferences menu.
2. Open the Settings tab.
3. Select `xterm-256color` for `"Declare terminal as"` field.

For iTerm2, you can:

1. Select Preferences menu.
2. Open the Profiles tab.
3. Open the Terminal tab.
4. Select `xterm-256color` for `"Report terminal type"` field.

Otherwise, you should manually update terminal setting. e.g., If you use bash, add following line to `~/.bashrc` file:

.. code:: sh

   $ export TERM=xterm-256color

For detail, see http://www.pixelbeat.org/docs/terminal_colours/#256 to enable 256 color on your terminal.


Usage
=====

Using kaa is intuitive. Typing alphabet keys will update file as you expected. Functional keys like arrow or delete keys also works.


Using menu
-----------

To display menu, type F1 key or alt+/ (type slash key with alt key). Each items in the menu has one underlined character. The menu item is execused by typing the underlined key with or without pressing alt key.

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


Recently used files memu
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


Code memu
+++++++++

Code menu differs among file types. Following items are typical in programming languages.

+---------------+----------------------------------------------------+
| Comment       | Insert line comment character at top of lines in   |
|               | selected regin.                                    |
+---------------+----------------------------------------------------+
| Uncomment     | Delete line comment character at top of lines in   |
|               | selected regin.                                    |
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

+----------------+----------------------------------------------------+
| Python console | Execute Python script.                             |
+----------------+----------------------------------------------------+
| Grep           | Search text from disk.                             |
+----------------+----------------------------------------------------+
| Paste lines    | Insert lines of text without auto indentation.     |
+----------------+----------------------------------------------------+
| Shell command  | Execute external shell command and insert the      |
|                | output.                                            |
+----------------+----------------------------------------------------+
| Make           | Run ``make`` to compile source files and capture   |
|                | error  messages. Use f9/10 key to traverse errors. |
+----------------+----------------------------------------------------+


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
| Join window    | Join splitted window.                           |
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
| F1, alt+/     | Show menu.                                         |
+---------------+----------------------------------------------------+
| Alt-w         | Show switch file menu.                             |
+---------------+----------------------------------------------------+
| Alt-m alt-v   | Show text conversion menu.                         |
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
| Alt+.              | Run last execused edit command again.          |
+--------------------+------------------------------------------------+
| Tab                | Indent selected lines.                         |
+--------------------+------------------------------------------------+
| Shift+Tab          | Dedent selected lines.                         |
+--------------------+------------------------------------------------+
| Control+o          | Word completion.                               |
+--------------------+------------------------------------------------+
| Control+u Alt+!    | Execute command and insert the output.         |
+--------------------+------------------------------------------------+



Replace dialog
--------------

When `regex` button is checked, `Replace` string is also regular expression string. In this case, special characters like `\\t` or `\\n` are converted to tab character and newline character. Also, backreference character will be replaced to substring matched group in the search string. For example, when search string is `'(a+)(b+)'` and replace string is `'\\2\\1'`,  matched string `'aabb'` will be replaced to `'bbaa'`.


Grep dialog
------------

Grep dialog has three input field. `Search` is a plain text or regular expression string to search. `Directory` is a directory to start searching. If `Tree` button was checked, files are searched recursively. `Filenames` is space separeted list of file spec in shell-style wildcards (e.g., `*.txt *.py *.doc`). Up arrow key displays history of each input field.

In the grep result window, use F9 and F10 key to traverse matches forward/backward. 


Python console
--------------

Unlike Python's interactive console, Python console in kaa does not execute Python script until you hit alt+Enter key. Until then you can edit Python script as if you are with editors without worrying about newlines and indentations.

When alt+Enter key was hit, all text in the window is executed as Python script and the value of the expression is printed out to console window. If the script contains print expression, the text will also be printed out to console window. If a part of text in the console window is selected, only text in the selected region will be execused.


Make
--------------

``[Tools]|Make`` executes ``make`` command to build your files. You can alter command and options to build. To retrieve previous command and options, hit up cursor key to display history window.

Output of ``make`` displayed on the window. You can traverse source files cause of the error forth and back with f9 and f10 key.

Python debugger
---------------

.. warning::
   Python debugger is highly exprimental at this point.
    

Kaa can be used as front-end of Python debugger module(``bdb``) running in another process. Although kaa itself requires Python 3.3 or later, you can use Python 2.6 or later in the target process. 

Starting debugger
++++++++++++++++++

There are three ways to start debugger.

kaadbg.run module
~~~~~~~~~~~~~~~~~~~~~~~~

Execute ``kaadbg`` package in Python interpreter to connect target program with kaa debugger. ``kaadbg`` is Python package installed as a part of kaa. To use another Python interpreter than kaa installed, you can install ``kaadbg`` separetely.

::

   $ sudo pip install -U kaadbg


Currentry, ``kaadbg`` supports from Python 2.6 to Python 3.x.

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

While debugger window is opend, you can suspend the debugger window by escape key. After you finish to update breakpoints in editor window, select ``[Tools]|Python debugger`` menu again to resume debugger. To view list of current breakpoints, select *breakpoints* button with ``alt+E`` key.

Inspect variables
++++++++++++++++++

To see value of variables, select ``Expr`` on the debugger window by pressing ``alt+E`` key and enter Python expression you want to inspect like ``self.spam``.


Customization
==================

Kaa executes a Python script file at `~/.kaa/__kaa__.py` on startup. You can write Python script to customize kaa as you like.


Sample - Show line numbers
----------------------------------

.. code:: python

   from kaa.filetype.default import defaultmode
   defaultmode.DefaultMode.SHOW_LINENO = True

`defaultmode.DefaultMode` is base class of all text file types. Line number is diplayed if `Defaultmode.SHOW_LINENO` is True. If you want to show line number of paticular file types, you can update SHOW_LINENO attribute of each file type classes.

.. code:: python

   # Show line number in HTML mode
   from kaa.filetype.html import htmlmode
   htmlmode.HTMLMode.SHOW_LINENO = True

Sample - Customize key binding
----------------------------------

Assign same keyboard shortcut of splitting windows command as Emacs.

.. code:: python

    from kaa.keyboard import *
    from kaa.filetype.default.defaultmode import DefaultMode
    
    DefaultMode.KEY_BINDS.append({
       ((ctrl, 'x'), '2'): 'editor.splithorz'    # Assign C-x 2 
    })
   
In this example, key sequence C-x 2 (control+x followed by 2) is assigned to 'editor.splithorz' command.

Sample - Change color palette
----------------------------------

Change color palette to ``light``.

.. code:: python

   import kaa
   kaa.app.DEFAULT_PALETTE = 'light'  # Use `light' palette. Default is `dark'


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

There is an expreimental script to run freeze to build standalone kaa binary file.
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


Acknowledgement
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

0.21.0 - 2013.12.15
--------------------

- Respect encoding declaration on loading/saving file in HTML/Python mode.

- Paste from OS clipboard didn't work on Mac.


Past versions
--------------

0.20.0 - 2013.12.13
+++++++++++++++++++++

- Save clipboard history to disk.

- Python debugger: Display status of target process.


0.19.0 - 2013.12.11
+++++++++++++++++++++

- Support system clipboard.


0.18.0 - 2013.12.10
+++++++++++++++++++++

- Optimizations. Kaa responds quicker than previous version.

- Error highlighting javascipt attribute in html mode was fixed.

- White space characters inserted by auto-indent are automatically removed if cursor moved to another position without entering a character.

- reStructuredText Mode: Non-ASCII punctuations were not recognized as separater of inline mark ups.


0.17.0 - 2013.12.06
+++++++++++++++++++++

- reStructuredText Mode: Recognize non-ASCII punctuation as separater of inline mark ups.

- Indent command: Don't indent blank line. (Contributed by `allanderek <https://github.com/kaaedit/kaa/pull/94>`_)

- Separate `kaadbg <https://pypi.python.org/pypi/kaadbg>`_ as new package.


0.16.0 - 2013.12.03
+++++++++++++++++++++

- Defer to save history information. Kaa now works much smoother than ever on PC with slow hard disk. 


0.15.1 - 2013.11.30
+++++++++++++++++++++

- Removed debugging code.


0.15 - 2013.11.29
+++++++++++++++++++++

- Python debugger now runs 20+ times faster than in 0.14.

- Highlight Python constant.


0.14 - 2013.11.27
+++++++++++++++++++++

- Experimental Python debugger.


0.13 - 2013.11.18
+++++++++++++++++++++

- New file mode: C language.

- New command: *[Tools] | Make*. Invoke ``make`` command to build and view output without leaving kaa.

- Move initial selection of Table Of Contents to current cursor position.


0.12 - 2013.11.16
+++++++++++++++++++++

- Show table of contents in Markdown mode. Hit Ctrl+t to display TOC.

- Show table of contents reStructuredText mode. Hit Ctrl+t to display TOC.

- Improve highlighting in Markdown mode.

- Bugs fixed.


0.11 - 2013.11.14
+++++++++++++++++++++

- Show table of contents in Python mode. Hit Ctrl+t to display TOC.

- Improve highlighting in reStructured mode.


0.10 - 2013.11.11
+++++++++++++++++++++

- Add 'japanese' encoding that detects text encoding from file.

- Specify text encoding to grep file.

- New commandline option: --no-init, --init-script, --palette, --term.

- New color palette: dark, light.


0.9 - 2013.11.9
+++++++++++++++++++++

- Markdown mode.

- reStructuredText mode.


0.8 - 2013.11.7
+++++++++++++++++++++

- View diff between original file and current buffer.

- Grep dialog now has 'Dir' button to select directory.
 
- Handle SIGTERM to restore terminal state before exit.

- Prompt to reload file when file modified by other process.


0.7 - 2013.11.5
+++++++++++++++++++++

- Paste from clipboard history.

- Word completion list now contains text from clipboard history.

- New command: New file here.

- New command: Open file here.

- New command: Open recently used file here.

- New command: Open recently used directory here.


0.6 - 2013.11.1
+++++++++++++++++++++

- Basic word completion with ctrl+o.

- Display blank line if the line is selected.

- Various minor changes.


0.5 - 2013.10.30
+++++++++++++++++++++

- Locate position of opened file where the file located last time.

- Changed history database scheme. By this change, old history will be deleted.

- Changed default color setting.

- Kaa didn't run if $TERM is 'xterm-color'.


0.4 - 2013.10.27
+++++++++++++++++++++

- Rectangular selection can be started by Alt+'#' key.

- `Window|Join` menu caused error.

- `File|Save all` caused error.


0.3.1 - 2013.10.25
+++++++++++++++++++++

- Python console window now works with Gnome terminal.

- `Window|Switch file` menu caused error.

- ^G (Goto line number) dialog shouldn't accept '0' if field is empty.


0.3.0 - 2013.10.24
+++++++++++++++++++++

- Python console window.

- Emacs style region selection. Now you can select region by ctrl+SPACE or ctrl+'@'key.

- Changed some default keyboard binding.

- A lot of bugs fixed.


0.2.0 - 2013.10.20
+++++++++++++++++++++

- Comment/Uncomment region.

- In replace dialog, replace-to text is now treated as regular expression text.

- A lot of bugs fixed.


0.1.0 - 2013.10.14
+++++++++++++++++++++

- Grep

- Various improvements.


0.0.4 - 2013.10.11
+++++++++++++++++++++

- New command: Close all.

- New command: Recently used file/directory.

- Search/Replace history.

- Line number display setting at menu | File | File Info.


0.0.3 - 2013.10.9
+++++++++++++++++++++

- Incremental search.

- Accept directory name as command line argument.

- New command: Go to line(^g).

- New command: Select current word(^c).

- New command: Save all files(menu | file | Save All).

- Improve file open dialog.


0.0.2 - 2013.10.5
+++++++++++++++++++++

- Misc commands.

- Highlight parenthesis at cursor.

- Support text encodnig other than utf-8.

- Other a lot of changes.


0.0.1 - 2013.6.16
+++++++++++++++++++++

- Initial release.

        
Copyright 
=========================

Copyright (c) 2013 Atsuo Ishimoto

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

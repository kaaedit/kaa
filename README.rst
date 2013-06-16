============================
Kaa - console text editor
============================

Kaa is a small and easy text editor for console environment.

.. DANGER::
   Kaa is still in the very early stage of development. Don't use kaa for other purpose than evaluation.

.. contents::

Requirements
============

* Python 3.3 or later

* Headers and librares for ncurses. Consult documentation of your platform for detail. With Debian/Ubuntu, you can install ncurses library with ::

  $ sudo apt-get install libncurses-dev

* (optional) Cython

Installation
============

1. Get source from github ::

   $ git clone git@github.com:atsuoishimoto/kaa.git

2. Install kaa ::
   
   $ cd kaa
   $ python setup.py install

Command line options
====================

To start kaa, type ::

   $ kaa [FILE]...

Usage
=====

Using kaa is intuitive. Typing alphabet keys will update file as you expected. Functional keys like arrow or delete keys also works.

Using menu
-----------

To display menu, type F1 key. Each items in the menu has one underlined character. Typing the underlined character extecutes the menu item. 

To hide menu, type escape key.

File menu
++++++++++

Open
   Open existing file.

Save
   Save current file.

Save As
   Save current file as new file.

Close
   Close current frame.

Quit
   Terminate kaa.


Edit menu
+++++++++

Cut
   Cut selected text.

Copy
   Copy selected text.
   
Paste
   Paste from clipboard.

Undo
   Undo last modification.

Redo
   Redo last undo.


Macro menu
++++++++++

Start record
   Start macro recording.

End record
   End macro recording.

Run macro
   Run last macro.


Window menu
+++++++++++

Frame list
   Show list of frame windows. Use left/right arrow key to change active frame.

Split vert
   Split current window vertically.

Split horz
   Split current window horizontally.

Move separator
   Move window separator. Use left/right arrow key to move separator.

Next window
   Activate next window.

Join window
   Join splitted window.

Switch file
   Switch content of active window.


Key bindings
------------

Arrow keys
   Move cursor.

Shift+arrow keys
   Select text.

Control+left/right arrow keys
   Move cursor to next/prev word boundary.

Backspace
   Delete the character to the left.

Delete
   Delete the character at the cursor.

Control+z
   Undo last change.

Control+r
   Redo last undoi.

F6
   Toggle macro recording on/off.

F5
   Run macro.

Control+S
   Search text.

Alt+S
   Replace text.

Control+b|Control+f|Control+p|Control+n
   Move cursor to left|right|up|down.

Alt+b|Alt+f
   Move cursor to next/prev word boundary.


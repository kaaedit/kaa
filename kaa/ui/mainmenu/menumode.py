import kaa
from kaa.ui.msgbox import msgboxmode


class MenuMode(msgboxmode.MsgBoxMode):
    SEPARATOR = '/'
    USE_UNDO = False
    CLOSE_ON_DEL_WINDOW = True

    @classmethod
    def show_menu(cls, wnd, itemname, parentitems=None):

        items = wnd.document.mode.MENU[itemname]
        doc = cls.build_msgbox(
                '', [item for (item, submenu, commandid) in items],
                lambda c:doc.mode._selected(c))
        
        doc.mode.target = wnd
        doc.mode.itemname = itemname
        doc.mode.parentitems = parentitems
        
        kaa.app.show_dialog(doc)
        return doc

    def close(self):
        super().close()
        self.target = None

    def _selected(self, c):
        if not c:
            if self.parentitems:
                doc = MenuMode.show_menu(
                    self.target, self.parentitems[-1], self.parentitems[:-1])
            
            return
        
        itemname = self.shortcuts[c]
        menus = self.target.document.mode.MENU
        for item, submenu, commandid in menus[self.itemname]:
            if itemname == item:
                if submenu:
                    parents = self.parentitems if self.parentitems else []
                    parents.append(self.itemname)
                    
                    MenuMode.show_menu(self.target, submenu, parents)
                else:
                    self.target.document.mode.on_commands(
                        self.target, [commandid])
                    

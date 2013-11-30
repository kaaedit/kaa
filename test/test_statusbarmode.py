from kaa.ui.statusbar import statusbarmode
import kaa_testutils


class TestStatusBarMode(kaa_testutils._TestDocBase):

    def _getmodeclass(self):
        return statusbarmode.StatusBarMode

    def test_sbarinfo(self):
        sbarinfo = statusbarmode.StatusInfo()
        sbarinfo.set_info(filename='filename',
                          modified=1)

        doc = self._getdoc('')
        doc.mode.build_status(sbarinfo)

        assert doc.gettext(0, doc.endpos()) == 'filename* [1:1] 1'

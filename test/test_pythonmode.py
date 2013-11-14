import kaa_testutils
from kaa import highlight
from kaa.filetype.python import pythonmode


class TestPythonMode(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = pythonmode.PythonMode
    def test_get_headers(self):
        script = '''
class spam:
    def ham(self, \, x=(def xxx)):
        'def\\''
# class xyz
def egg():
   """\\""""
def bacon():
'''
        doc = self._getdoc(script)
        tokens = [t for t in doc.mode.get_headers()]
        assert tokens == [
            ('namespace', (), 'spam', 'spam', None, 1), 
            ('function', (tokens[0],), 'spam.ham', 'ham()', None, 13),
            ('function', (), 'egg', 'egg()', None, 76), 
            ('function', (), 'bacon', 'bacon()', None, 99)] 

from kaa.theme import Overlay
from kaa.theme import Style

DefaultThemes = {
    'basic': [
        Style('default', 'default', 'default'),
        Style('lineno', 'White', 'Blue'),
        Style('blank-line-header', 'Blue', None),
        Style('parenthesis_cur', 'White', 'Blue'),
        Style('parenthesis_match', 'Red', 'Yellow'),

        Style('keyword', 'Magenta', None),
        Style('constant', 'Red', None),
        Style('directive', 'Orange', None),
        Style('comment', 'Cyan', None),
        Style('string', 'Blue', None),
        Style('number', 'Green', None),


        Overlay('cursor-row', None, 'Base02'),
        Overlay('breakpoint', None, 'Base02'),
        Overlay('current-row', None, 'Yellow'),
    ],
}

from kaa.theme import Theme, Style

DefaultThemes = {
    'basic':
        Theme([
            Style('default', 'default', 'default'),
            Style('lineno', 'White', 'Blue'),
            Style('parenthesis_cur', 'White', 'Blue'),
            Style('parenthesis_match', 'Red', 'Yellow'),

            Style('keyword', 'Magenta', 'default'),
            Style('directive', 'Orange', 'default'),
            Style('comment', 'Cyan', 'default'),
            Style('string', 'Blue', 'default'),
            Style('number', 'Green', 'default'),
        ]),
    
}

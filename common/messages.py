# (c) 2014 jano <janoh@ksp.sk>
# Various types of messages with colors
import sys
from enum import Enum

class Status(Enum):
    ok = 0
    wa = 1
    tle = 2
    exc = 3
    ce = 4 # not used yet
    err = 5
    valid = 6

    def __str__(self):
        return self.name.upper()

    def colored(self, end=None):
        return '%s%s%s' % (Color.status[self], self, end or Color.normal)


class Color:
    colorful = False

    def setup(args):
        Color.colorful = args.colorful
        Color.normal = Color('normal')
        Color.infog = Color('good')
        Color.infob = Color('fine')
        Color.warning = Color('bad')
        Color.error = Color('error')
        Color.table = Color('blue')
        Color.scores = [Color('special1', 'special2', 'score%s' % i) for i in range(5)]
        Color.status = {}
        for s in Status:
            Color.status[s] = Color(str(s), 'bold')

    def __init__(self, *args):
        if Color.colorful:
            modifiers = [str(_codemap[c]) for c in args]
            self.code = '\033[%sm' % ';'.join(modifiers)
        else:
            self.code = ''
    def __str__(self):
        return self.code

    def score_color(points, maxpoints):
        bounds = [0,4,7,9,10]
        p = 0
        while p < 4 and points * 10 > maxpoints * bounds[p]:
            p += 1
        return Color.scores[p]

    def colorize(status, text, end=None):
        index = (status in (Status.ok, Status.valid))
        return '%s%s%s' % ((Color.warning, Color.infog)[index],
                            text, 
                            end or Color.normal)
      

_sow = sys.stdout.write
_sew = sys.stderr.write

_codemap = {
    'OK': 'green', 'WA': 'red', 'TLE': 'purple', 'EXC': 45, 'CE':'ERR', 'ERR': 41, 'VALID': 'OK',
    'bad': 'red', 'good': 'green', 'ok': 'yellow', 'fine': 'blue', 'error': 'ERR',
    
    'score0': 196, 'score1': 208, 'score2': 226, 'score3': 228, 'score4': 46,
    
    'red': 91, 'green': 92, 'yellow': 93, 'blue': 94, 'purple': 95, 'cyan': 96, 'white': 37,

    'bold': 1, 'dim': 2, 'underlined': 4, 'blink': 5, 'invert': 7, 
    'nobold': 21, 'nodim': 22, 'nounderlined': 24, 'noblink': 25, 'noinvert': 27, 
    'normal':0, 'special1':38, 'special2':5,
}

# compile _codemap
_changed = True
while _changed:
    _changed = False
    for key in _codemap:
        if isinstance(_codemap[key], str):
            _codemap[key] = _codemap[_codemap[key]]
            _changed = True

# {{{ ---------------------- messages ----------------------------

def error(text, doquit=True):
    _sew("%s%s%s\n" % (Color.error, text, Color.normal))
    if doquit:
        quit(1)


def warning(text):
    _sew("%s%s%s\n" % (Color.warning, text, Color.normal))


def infob(text):
    _sew("%s%s%s\n" % (Color.infob, text, Color.normal))


def infog(text):
    _sew("%s%s%s\n" % (Color.infog, text, Color.normal))


def info(text):
    _sew("%s\n" % text)


# }}}

def wide_str(width, side):
    return '{:%s%ss}' % (('','>','<')[side], width)


def table_row(color, columns, widths, alignments, header=False):
    for i in range(len(columns)):
        if header == True:
            columns[i] = wide_str(widths[i], alignments[i]).format(columns[i])
        elif isinstance(columns[i], Status):
            status = columns[i]
            columns[i] = status.colored() + ' '*(widths[i]-len(str(status)))
            columns[i] += str(Color.table)
        else:
            columns[i] = wide_str(widths[i], alignments[i]).format(str(columns[i]))
            columns[i] = str(color) + columns[i] + str(Color.table)
    return '%s| %s |%s' % (str(Color.table), ' | '.join(columns), str(Color.normal))


def table_header(columns, widths, alignments):
    first_row = table_row(Color.table, columns, widths, alignments, True)
    second_row = '|'.join([str(Color.table)]+['-'*(w+2) for w in widths]+[str(Color.normal)])
    return '\n%s\n%s' % (first_row, second_row)
    

def color_test():
    args = lambda: None
    setattr(args, 'colorful', True)
    Color.setup(args)

    info("white")
    infob("blue")
    infog("green")
    warning("warning")
    error("error", doquit=False)
    _sew(''.join([s.colored() for s in Status])+'\n')
    for i in range(11):
        _sew('%s%s/%s%s\n' % (Color.score_color(i, 10), i, 10, Color.normal))

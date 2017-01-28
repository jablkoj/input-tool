# (c) 2014 jano <janoh@ksp.sk>
'''
Format of description files:
    One line - one input
        If you end line with '\\', you can continue on next line. This action
        ignores #,@,$,!,~... on the beginning of next line.
    Inputs inside batch are named 'a-z' or 'a...a-z...z', if there are many inputs.
    Empty line separates batches.
        Batches are named 1-9 or 0..01-9..99 if there are many batches
    # starting lines are comments
    @, $, ! are used for special request on the next lines.
            @ - all future lines.
            $ - all lines in this batch.
            ! - next line.
        Each of them overrides less specific ones, so only the most specific or
        last will be applied.
        You can use this commands in this lines, space separated
            rule=predefinedgenerator (not implemented yet)
            gen=othergenerator
            name=otherinputname
            class=prefixforname
            batch=otherbatchname
        It is your responsibility to not overwrite your inputs with this.
    ~ starting lines will have ~ removed and no special effect applyed on them.
        Effect of '\\' will be still applyed.
    {} you can use some special variables closed inside brackets.
        (none of them is implemented yet)
        {batch} - name of batch
        {name} - name of input
        {id} - 1 indexed number of this input
        {rand} - random integer from (0, MAXINT-1)
        Use {{ }} instead of single brackets or use ~ to turn of effects

'''
from random import randint

def _int_log(number, base):
    result = 1
    while number >= base:
        number //= base
        result += 1
    return result

def _create_name(number, base, length):
    result = ''
    start = ord('0') if base == 10 else ord('a')
    for i in range(length):
        result = chr(start + number % base) + result
        number //= base
    return result

class Input:
    maxbatch = 1
    maxid = 0
    MAXINT = 2 ** 31

    def __lt__(self, other):
        if self.batch != other.batch:
            return self.batch < other.batch
        return self.name < other.name

    def __init__(self, text, batchid, subid, inputid):
        self.text = text
        self.effects = True
        self.commands = {}
        self.batch = batchid
        self.name = subid
        self.id = inputid
        self.generator = None
        Input.maxbatch = max(Input.maxbatch, batchid)
        Input.maxid = max(Input.maxid, subid)
        self.compiled = False

    def _apply_commands(self):
        if not self.effects:
            return
        v = self.commands.get('batch', None)
        if v:
            self.batch = v
        v = self.commands.get('name', None)
        if v:
            self.name = v
        v = self.commands.get('class', None)
        if v:
            self.name = v + self.name
        v = self.commands.get('gen', None)
        if v:
            self.generator = v

    def _apply_format(self):
        if not self.effects:
            return
        self.text = self.text.format(**{
            'batch': self.batch,
            'name': self.name,
            'id': self.id,
            'rand': randint(0, Input.MAXINT - 1),
        })

    def compile(self):
        if self.compiled:
            return
        self.compiled = True
        if isinstance(self.batch, int):
            self.batch = _create_name(self.batch, 10,
                                      _int_log(Input.maxbatch, 10))
        if isinstance(self.name, int):
            if Input.maxid == 0:
                self.name = ''
            else:
                self.name = _create_name(self.name, 26,
                                         _int_log(Input.maxid, 26))
        self._apply_commands()
        self._apply_format()
        if self.name:
            self.name = '.%s' % self.name

    def get_name(self, path='', ext=''):
        return '%s%s%s.%s' % (path, self.batch, self.name, ext)

    def get_text(self):
        return self.text

class Sample(Input):

    def __init__(self, lines, path, batchname, id, ext):
        super().__init__(lines, 0, id, id)
        self.path = path + '/'
        self.ext = ext
        self.batch = batchname
        self.effects = False

    def save(self):
        open(self.get_name(self.path, self.ext), 'w').write(self.text)

class Recipe:

    def __init__(self, file):
        self.recipe = file.readlines()
        self.programs = []
        self.inputs = []

    def _parse_commands(self, line):
        commands = {}
        parts = line.split()
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                commands[k] = v
                if k == 'gen':
                    self.programs.append(v)
        return commands

    def _parse_recipe(self):
        continuingline = False
        all_commands, batch_commands, line_commands = {}, {}, {}
        batchid, subid, inputid = 1, 0, 1

        for line in self.recipe:
            line = line.strip()
            if continuingline:
                continuingline = line.endswith('\\')
                if continuingline:
                    line = line[:-1]
                self.inputs[-1].text += line
                continue
            continuingline = line.endswith('\\')
            if continuingline:
                line = line[:-1]

            if len(line) == 0:  # new batch
                batchid += 1
                subid = 0
                batch_commands = {}
                continue
            if line.startswith('#'):  # comment
                continue
            if line.startswith('@'):
                all_commands = self._parse_commands(line[1:])
                continue
            if line.startswith('$'):
                batch_commands = self._parse_commands(line[1:])
                continue
            if line.startswith('!'):
                line_commands = self._parse_commands(line[1:])
                continue
            effects = True
            if line.startswith('~'):  # effects off
                line = line[1:]
                effects = False

            self.inputs.append(Input(line, batchid, subid, inputid))
            subid += 1
            inputid += 1
            if effects:
                self.inputs[-1].commands = \
                    line_commands or batch_commands or all_commands
            else:
                self.inputs[-1].effects = False
            line_commands = {}

    def process(self):
        self._parse_recipe()
        for input in self.inputs:
            input.compile()

_cumberbatch = '''\
~~~~~~~~~~~~~~~~~~~+::=~:~=,~~~:=+=~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~:~==~:+::===::::,..,:~~+~~~~~~~~~~~~~:~:::~~~~
::~~~~~~~~~~~~==:~~~.::~~,~,~,:====~:~=~~~~~~~~~~~:::::::~~~
::~~~~~~~~~~~~:~:~~:,::~,,==::~:,.,,.~:~~:::~~~~~~~~~~~~~~~~
~~~~~::~~~~~::~~::::,,:,,:~~:::=~::~~~=::~~~:=~~~~~~~~~~~~~~
===~~~~~=~~~:~,:,::,,:,,:,,,,,:,:,,,,,:~,::,,,:~:==~~~~~~~~~
==~~~~~~~~~,~,:.,,,.:,,:,,:,,,...,,,,,,,,,,,,..,~=+=~~~~~~=~
~~~~~~~:::,::,,,,,~:::,,,.,,,,,,...,,,::,,.,.,.,:~:~~~~~~~~~
~~~::=:~:~~:,:.,,,,,,,.::,...,.,....,~??=..,..,.,~:=====~~~~
:~~~:~~:::~::,,,,..:.,,.:,,,,..,:===??II?+,..,.,.,::~=~~~~~~
:::::,:::,,,,......,,.,.,,....,~++??IIIII?=..,.,,,::~=~~~~~~
::::~~,,,,..,......,,,,,.,,...:++???IIIIIII:..,:,,::~+=~~~~~
~~~:~:,,,,.,......,:..,,~=,,,,~+????IIIII7I+,,.....,~+~~~~~~
~~~~:,,,,,.......,~+++====~~~~++????I?IIIII+:.,....,,,:=~~~~
~~~~:,,.......,.,~=+++++++++++++???I?I?III?+:.....,,,,,~~~~~
::~:,,,.....,.,,,~=+?????????????IIIIIIIII?+:......,:,,,~~~~
:~~:,......,...,~=++???????????IIII??II??II?=........,,:~~~~
~~~:,..........,==+?????????????I?????II???I+.......,,,~~~~~
~~~:,..........:=+=~~~====+++?=++===+=~~::~=+,......:::====~
~~~:::.........~=+=~=~~~:::::~~++~:::,,,,,~=?=,,...::~~~==~~
::::~:,,..,:,,,=++++==~::::,~~???+~:~~~==+?+?=,:...,~~~~~~~~
::::~:,...::,,:=++??+++=======?III=+===++????+,:,,::~~::~:::
:::::::,..,=:~,:++??????+++?+??III?+??++?????~+=::::::::::::
:::::::::..=++=~=+?????????????III?????????++++,~:::~~~~::~~
:::::::~:,..===+=+++????????+I?IIII?=+????+=++~,:~~~~~~~~~~~
::::::::::.,,.~~=====+????+~????????+=+?+++=:.:,~~~=========
::::::::::::,,:.++++=++++=~=~:,~~~,,==~=++++.::,~~~~~~~~~~~~
:~~~~~~~~~~~~~,.==++++++===++==~:~~=====++++.,,,:~~~~~~~~~~~
::~:::::~~::~~...+=+++++===+++=~~~===~===++?.,,,::,~~~~~~~~~
::::::::~:::::,..===+=++=~:~+++=+=~==::~==+:.:,,,,::~~~~~~~~
::::::~~~::::,,..=~~====~~====~,,~=++======.,::..,:,:::~~~~~
:::::~:~:::::,,,.:~~~~~~==++++?+++===++=~~:.,,:,..,,:,:,~~~~
~~:~~~~~~~~~:,,,,.~:::::~=++=~~:~:~~=====:.,,:::...,,,,,,=~~
~~~~~~~~~~~~,,,,,.:~:::~~=+===========+=~,.,,:::..,,.:.,~,:~
~~~:~~~~~~~~,,,,,.,:~,::~~=+++???+++++=~..,,,,::...,.,,,::,:
~~~~~~~~~~~~.,,,...:~~,,:::=++=====~==~...,,,,::,....,,,,,,,
~~~~:~~~~~~:,,,,....:~~:,,,:::~:::::,.....,,,,,:,..,,,,,,,,,
~~~~~~:~~~:,,,,,.....:~~~~:,,,,,,,,,.....,,,,,,,,..,,,,,,,:,
~~~~~~::::,::,.,.....:::~~:~::,,,,,.....,,,,,,,,,,,,,,,,,:,:'''

def prepare(args):
    # lol ;)
    if args.batchname.lower() == 'cumber':
        print(_cumberbatch)

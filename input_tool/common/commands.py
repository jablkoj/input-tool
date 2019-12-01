# (c) 2014 jano <janoh@ksp.sk>
'''
Basic behaviour you need to understand if you want to use this.
Don't use spaces in file names.

Naming conventions -- Type of file is determined by prefix.
  gen - generator  -- Gets one line on stdin, prints input on stdout.
  sol - solution   -- Gets input on stdin, prints output on stdout.
                      Can be restricted by time and memory.
                      Stderr is ignored.
  val - validator  -- Gets input on stdin, prints one line (optional)
                      and returns 0 (good input) / 1 (bad input).
                      Also gets input name as arguments split by '.',
                      example: ./validator 00 sample a in < 00.sample.a.in
  diff, check, ch_ito_, test - checker
                   -- Gets arguments with names of files.
  <other>          -- Anything. E.g. you can use arbitrary program as generator,
                      but dont use sol*, val*, diff*, ...
  Split parts of names by '-' not '_'.
  In solutions, parts can be score, author, algorithm, complexity
  in this order. E.g. sol-100-jano-n2.cpp, sol-jano.cpp, sol-40.cpp
  (if second part is an integer, it is treated as score).

Program types      -- What is recognized and smartly processed.
                      It is determined mainly by extension and number of words.
  multiple words   -- Run as it is.
  noextension      -- Check if binary should be compiled and maybe compile.
                      Then run ./noextension if file exists and noextension otherwise.
program.ext      -- If c/cc/c++/pas/java, compile and run binary.
program.ext      -- If .pyX, run as 'pythonX program.ext. py = py3

'''

import sys
import os
import subprocess
from input_tool.common.messages import *


def is_file_newer(file1, file2):
    if not os.path.exists(file1) or not os.path.exists(file2):
        return None
    return os.path.getctime(file1) > os.path.getctime(file2)


def to_base_alnum(s):
    s = s.split('/')[-1]
    return ''.join([x for x in s if str.isalnum(x)])


ext_c = ['cpp', 'cc', 'c']
ext_pas = ['pas']
ext_java = ['java']
ext_py3 = ['py', 'py3']
ext_py2 = ['py2']
ext_rust = ['rs']
all_ext = ext_c + ext_pas + ext_java + ext_py3 + ext_py2 + ext_rust
compile_ext = ext_c + ext_pas + ext_java + ext_rust
script_ext = ext_py3 + ext_py2


class Program:  # {{{

    def compare_mask(self):
        return (0, self.name)

    def __lt__(self, other):
        return self.compare_mask() < other.compare_mask()

    def _transform(self):
        name = self.name
        self.compilecmd = None
        self.source = None
        self.ext = None
        self.run_cmd = name
        self.filestoclear = []

        # if it is final command, dont do anything
        if self.forceexecute or len(name.split()) > 1:
            return

        # compute source, binary and extension
        if not '.' in name:
            for ext in all_ext:
                if os.path.exists(name + '.' + ext):
                    self.source = name + '.' + ext
                    self.ext = ext
                    break
        else:
            self.source = name
            self.run_cmd, self.ext = name.rsplit('.', 1)

        if not self.ext in all_ext:
            self.run_cmd = name
            return

        # compute run_cmd
        if self.ext in script_ext:
            self.run_cmd = self.source

        docompile = (
            self.cancompile and
            (self.ext in compile_ext) and
            (self.source == name or
            not os.path.exists(self.run_cmd) or
            is_file_newer(self.source, self.run_cmd))
        )
        if docompile:
            if self.ext in ext_c:
                self.compilecmd = 'make %s' % self.run_cmd
                self.filestoclear.append(self.run_cmd)
            elif self.ext in ext_pas:
                self.compilecmd = 'fpc -o%s %s' % (self.run_cmd, self.source)
                self.run_cmd = self.run_cmd
                self.filestoclear.append(self.run_cmd)
                self.filestoclear.append(self.run_cmd + '.o')
            elif self.ext in ext_java:
                self.compilecmd = 'javac %s' % self.source
                self.filestoclear.append(self.run_cmd + '.class')
            elif self.ext in ext_rust:
                self.compilecmd = 'rustc %s.rs' % self.run_cmd
                self.filestoclear.append(self.run_cmd)

        if not os.access(self.run_cmd, os.X_OK):
            if self.ext in ext_py3:
                self.run_cmd = 'python3 ' + self.source
            if self.ext in ext_py2:
                self.run_cmd = 'python2 ' + self.source
            if self.ext in ext_java:
                self.run_cmd = 'java ' + self.run_cmd

    def prepare(self):
        if self.compilecmd != None:
            so = subprocess.PIPE if self.quiet else None
            se = subprocess.STDOUT if self.quiet else None
            infob('Compiling: %s' % self.compilecmd)
            try:
                subprocess.check_call(self.compilecmd, shell=True,
                                    stdout=so, stderr=se)
            except:
                error('Compilation failed.')

        if (not self.forceexecute and
            os.access(self.run_cmd, os.X_OK) and
                self.run_cmd[0].isalnum()):
            self.run_cmd = './' + self.run_cmd

        if isinstance(self, Solution):
            Solution.cmd_maxlen = max(Solution.cmd_maxlen, len(self.run_cmd))
        self.ready = True

    def clear_files(self):
        for f in self.filestoclear:
            if os.path.exists(f):
                os.remove(f)
            else:
                warning('Not found %s' % f)

    def __init__(self, name, args):
        self.name = name
        self.quiet = args.quiet
        self.cancompile = args.compile
        self.forceexecute = args.execute
        self.ready = False

        # compute run_cmd, compilecmd and filestoclear
        self._transform()
#}}}


class Solution(Program):  # {{{
    cmd_maxlen = len('Solution')

    def updated_status(self, original, new):
        if original == Status.ok:
            return new
        if new == Status.ok:
            return original
        if original == Status.err or new == Status.err:
            return Status.err
        return original

    def compare_mask(self):
        filename = self.name.rsplit(' ', 1)[
            -1].rsplit('/', 1)[-1].rsplit('.', 1)[0]
        score = 0
        parts = filename.split('-')
        if 'vzorak' in parts or 'vzor' in parts:
            score += 2000
        if filename.startswith('sol'):
            if len(filename) == 3:
                score += 1000
            if len(parts) > 1 and parts[1].isnumeric():
                score += int(parts[1])
        return (-1, -score, self.name)

    def __init__(self, name, args):
        super().__init__(name, args)
        self.statistics = {
            'maxtime': 0,
            'sumtime': 0,
            'batchresults': {},
            'result': Status.ok,
        }

    def get_statistics_header(inputs):
        batches = set([x.rsplit('.', 2)[0] for x in inputs if not 'sample' in x])
        pts = len(batches)
        widths = [Solution.cmd_maxlen, 8, 9, 6, 6]
        colnames = ['Solution', 'Max time', 'Times sum', 'Pt %3d' % pts, 'Status']
        return table_header(colnames, widths, [-1,1,1,1,0])

    def get_statistics(self):
        points, maxpoints = 0, 0
        for key in self.statistics['batchresults']:
            if 'sample' in key:
                continue
            maxpoints += 1
            if self.statistics['batchresults'][key] == Status.ok:
                points += 1
        color = Color.score_color(points, maxpoints)
        widths = (Solution.cmd_maxlen, 8, 9, 6, 6)
        colnames = [self.run_cmd, self.statistics['maxtime'], self.statistics['sumtime'],
                    points, self.statistics['result']]

        return table_row(color, colnames, widths, [-1,1,1,1,0])

    def record(self, ifile, status, time):
        input = ifile.rsplit('/', 1)[1].rsplit('.', 1)[0]
        batch = input if input.endswith('sample') else input.rsplit('.', 1)[0]
        batchresults = self.statistics['batchresults']
        batchresults[batch] = self.updated_status(
            batchresults.get(batch, Status.ok),
            status)
        self.statistics['maxtime'] = max(
            self.statistics['maxtime'], int(time * 1000))
        self.statistics['sumtime'] += int(time * 1000)
        self.statistics['result'] = self.updated_status(
            self.statistics['result'], status)

    def time_cmd(self, timefile, timelimit=0):
        timekill = 'timeout %s' % timelimit if timelimit else ''
        return '/usr/bin/time -f "%s" -o %s -q %s' % ('%U', timefile, timekill)

    def run_args(self, ifile):
        return ''

    def run(self, ifile, ofile, tfile, checker, args):
        isvalidator = isinstance(self, Validator)
        if not self.ready:
            error('%s not prepared for execution' % self.name)
        so = subprocess.PIPE if self.quiet else None
        se = subprocess.PIPE if self.quiet else None
        timefile = '.temptime-%s-%s-%s.tmp' % (
            to_base_alnum(self.name),
            to_base_alnum(ifile),
            os.getpid(),
        )
        # run solution
        usertime = -1
        time_cmd = self.time_cmd(timefile, int(args.timelimit))

        cmd = '%s %s %s< %s > %s' % (time_cmd, self.run_cmd,
            self.run_args(ifile), ifile, tfile)
        try:
            result = subprocess.call(cmd, stdout=so, stderr=se, shell=True)
            if result == 0:
                status = Status.ok
            elif result == 124:
                status = Status.tle
            elif result > 0:
                status = Status.exc
            else:
                status = Status.err
            try:
                usertime = float(open(timefile, 'r').read().strip())
            except:
                usertime = -0.001
                if status == Status.ok:
                    status = Status.exc
            if status == Status.ok and not isvalidator:
                if checker.check(ifile, ofile, tfile):
                    status = Status.wa
        except Exception as e:
            result = -1
            status = Status.err
            warning(str(e))
        finally:
            if os.path.exists(timefile):
                os.remove(timefile)

        if isvalidator and (status in (Status.ok, Status.wa)):
            status = Status.valid

        # construct summary
        self.record(ifile, status, usertime)
        run_cmd = ('{:<' + str(Solution.cmd_maxlen) + 's}').format(self.run_cmd)
        time = '{:6d}'.format(int(usertime * 1000))

        if args.inside_oneline:
            input = ('{:' + str(args.inside_inputmaxlen) + 's}').format(
                (ifile.rsplit('/', 1)[1]))
            summary = '%s < %s %sms.' % (run_cmd, input, time)
        else:
            summary = '    %s  %sms.' % (run_cmd, time)

        print(Color.colorize(status, summary), status.colored())

        if status == Status.err:
            error('Internal error. Testing will not continue', doquit=True)
#}}}


class Validator(Solution):  # {{{

    def is_validator(filename):
        return filename.startswith('val');

    def compare_mask(self):
        return (-2, self.name)

    def updated_status(self, original, new):
        if original == Status.valid:
            return new
        if new == Status.valid:
            return original
        if original == Status.err or new == Status.err:
            return Status.err
        return original

    def get_statistics(self):
        color = Color.score_color(self.statistics['result']==Status.valid, 1)
        widths = (Solution.cmd_maxlen, 8, 9, 6, 6)
        colnames = [self.run_cmd, self.statistics['maxtime'], self.statistics['sumtime'],
                    '', self.statistics['result']]

        return table_row(color, colnames, widths, [-1,1,1,1,0])

    def run_args(self, ifile):
        return ' '.join(ifile.split('/')[-1].split('.')) + ' '

    def __init__(self, name, args):
        super().__init__(name, args)
        self.statistics['result'] = Status.valid

#}}}


class Checker(Program):  # {{{

    def compare_mask(self):
        return (-3, self.name)

    def __init__(self, name, args):
        super().__init__(name, args)
        if name == 'diff':
            self.run_cmd = 'diff'
            self.compilecmd = None
            self.forceexecute = True

    def diff_cmd(self, ifile, ofile, tfile):
        diff_map = {
            'diff': ' %s %s > /dev/null' % (ofile, tfile),
            'check': ' %s %s %s > /dev/null' % (ifile, ofile, tfile),
            'chito': ' %s %s %s > /dev/null' % (ifile, tfile, ofile),
            'test': ' %s %s %s %s %s' % ('./', './', ifile, ofile, tfile),
        }
        for key in diff_map:
            if to_base_alnum(self.name).startswith(key):
                return self.run_cmd + diff_map[key]
        return None

    def check(self, ifile, ofile, tfile):
        se = subprocess.PIPE if self.quiet else None
        result = subprocess.call(
            self.diff_cmd(ifile, ofile, tfile),
            shell=True, stderr=se)
        if not result in (0,1):
            warning('Checker exited with status %s' % checkres)
        return result
#}}}


class Generator(Program):  # {{{

    def compare_mask(self):
        return (-4, self.name)

    def generate(self, ifile, text):
        cmd = "%s > %s" % (self.run_cmd, ifile)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
        p.communicate(str.encode(text))

#}}}


'''
# compile the wrapper if turned on
wrapper_binary = None
if args.wrapper != False:
    path = args.wrapper or '$WRAPPER'
    if os.uname()[-1] == 'x86_64':
        wrapper_source='%s/wrapper-mj-amd64.c' % path
    else:
        wrapper_source='%s/wrapper-mj-x86.c' % path
    wrapper_binary='%s/wrapper' % path
    if os.system('gcc -O2 -o %s %s' % (wrapper_binary, wrapper_source)):
        error('Wrapper compile failed.')
        quit(1)
'''

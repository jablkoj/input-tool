# (c) 2014 jano <janoh@ksp.sk>
''' 
Basic behaviour you need to understand if you want to use this

Naming conventions -- Type of file is determined by prefix.
  gen - generator  -- Gets one line on stdin, prints input on stdout.
  sol - solution   -- Gets input on stdin, prints output on stdout.
                      Can be restricted by time and memory.
                      Stderr is ignored.
  val - validator  -- Gets input on stdin, prints one line (optional)
                      and returns 0 (good input) / 1 (bad input).
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

import sys, os, subprocess
from common.messages import *

def isfilenewer(file1, file2):
    if not os.path.exists(file1) or not os.path.exists(file2):
        return None
    return os.path.getctime(file1) > os.path.getctime(file2)

def tobasealnum(s):
    s = s.split('/')[-1]
    return ''.join([x for x in s if str.isalnum(x)])

    
ext_c = ['cpp', 'cc', 'c']
ext_pas = ['pas']
ext_java = ['java']
ext_py3 = ['py', 'py3']
ext_py2 = ['py2']
all_ext = ext_c + ext_pas + ext_java + ext_py3 + ext_py2
compile_ext = ext_c + ext_pas + ext_java
script_ext = ext_py3 + ext_py2

class Program:
    def compare_mask(self):
        return (0, self.name)

    def __lt__(self, other):
        return self.compare_mask() < other.compare_mask()

    def transform(self): #{{{
        name = self.name
        self.compilecmd = None
        self.source = None
        self.ext = None
        self.runcmd = name
        self.filestoclear = []
        
        # if it is final command, dont do anything
        if self.forceexecute or len(name.split())>1:
            return

        # compute source, binary and extension
        if not '.' in name:
            for ext in all_ext:
                if os.path.exists(name+'.'+ext):
                    self.source = name+'.'+ext
                    self.ext = ext
                    break
        else:
            self.source = name
            self.runcmd, self.ext = name.rsplit('.', 1)
        
        if not self.ext in all_ext:
            self.runcmd = name
            return
        
        # compute runcmd
        if self.ext in script_ext:
            self.runcmd = self.source

        docompile = (
            self.cancompile and 
            (self.ext in compile_ext) and 
            (self.source == name or 
             not os.path.exists(self.runcmd) or
             isfilenewer(self.source, self.runcmd))
        )
        if docompile:
            if self.ext in ext_c:
                self.compilecmd = 'make %s' % self.runcmd
                self.filestoclear.append(self.runcmd)
            elif self.ext in ext_pas:
                self.compilecmd = 'fpc -o%s %s' % (self.runcmd, self.source)
                self.runcmd = self.runcmd
                self.filestoclear.append(self.runcmd)
                self.filestoclear.append(self.runcmd + '.o')
            elif self.ext in ext_java:
                self.compilecmd = 'javac %s' % self.source
                self.filestoclear.append(self.runcmd + '.class')

        if not os.access(self.runcmd, os.X_OK):
            if self.ext in ext_py3:
                self.runcmd = 'python3 ' + self.source
            if self.ext in ext_py2:
                self.runcmd = 'python2 ' + self.source
            if self.ext in ext_java:
                self.runcmd = 'java ' + self.runcmd
    #}}}

    def prepare(self):
        if self.compilecmd != None:
            so = subprocess.PIPE if self.quiet else None
            se = subprocess.STDOUT if self.quiet else None
            infob('Compiling: %s' % self.compilecmd)
            try:
                subprocess.check_call(self.compilecmd, shell=True, 
                    stdout=so ,stderr=se)
            except:
                error('Compilation failed.')
        
        if (not self.forceexecute and 
            os.access(self.runcmd, os.X_OK) and 
            self.runcmd[0].isalnum()):
            self.runcmd = './'+self.runcmd

        if isinstance(self,Solution):
            Solution.cmd_maxlen = max(Solution.cmd_maxlen, len(self.runcmd))
        self.ready = True
    
    def clearfiles(self):
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

        # compute runcmd, compilecmd and filestoclear
        self.transform()

class Solution(Program):
    cmd_maxlen = len('Solution')

    def updated_status(original, new):
        if original == 'OK': return new
        if new == 'OK': return original
        if original == 'INT' or new == 'INT':
            return 'INT'
        return original
    
    def compare_mask(self):
        filename = self.name.rsplit(' ',1)[-1].rsplit('/',1)[-1].rsplit('.',1)[0]
        score = 0
        parts = filename.split('-')
        if 'vzorak' in parts or 'vzor' in parts:
            score+=2000
        if filename.startswith('sol'):
            if len(filename)==3: score+=1000
            if len(parts) > 1 and parts[1].isnumeric():
                score+=int(parts[1])
        return (-1, -score, self.name)
    
    def __init__(self, name, args):
        super().__init__(name, args)
        self.statistics = {
            'maxtime': 0,
            'sumtime': 0,
            'batchresults': {},
            'overallresult': 'OK',
        }
    
    def get_statistics_header(inputs):
        sol = ('{:'+str(Solution.cmd_maxlen)+'s}').format('Solution')
        batches = set([x.rsplit('.', 2)[0] 
                      for x in inputs if not 'sample' in x])
        pts = len(batches)

        return headercolor()+('\n'+
            '| %s | Max time | Times sum | Pt %3d | Status |\n' % (sol, pts) +
            '|-%s-|----------|-----------|--------|--------|' % ('-'*len(sol))
        )+resetcolor()


    def get_statistics(self):
        points, maxpoints = 0, 0
        for key in self.statistics['batchresults']:
            if 'sample' in key: continue
            maxpoints += 1
            if self.statistics['batchresults'][key] == 'OK':
                points += 1
        color = scorecolor(points, maxpoints)
        hcolor = headercolor()

        runcmd = ('{:'+str(Solution.cmd_maxlen)+'s}').format(self.runcmd)
        status = self.statistics['overallresult']
        status = colorize(status, '{:3s}'.format(status), True)
    
        line =  '|| %s || %8d || %9d ||    %3d ||   |<|%s|>|  |||<|' % (
            runcmd, self.statistics['maxtime'], self.statistics['sumtime'],
            points, status
        )
        line = line.replace('||', hcolor+'|'+color)
        line = line.replace('|<|', resetcolor())
        line = line.replace('|>|', color)

        return line
        

    def record(self, ifile, status, time):
        input = ifile.rsplit('/', 1)[1].rsplit('.', 1)[0]
        batch = input.rsplit('.', 1)[0]
        batchresults = self.statistics['batchresults']    
        batchresults[batch] = Solution.updated_status(
            batchresults.get(batch, 'OK'),
            status)
        self.statistics['maxtime'] = max(self.statistics['maxtime'], int(time*1000))
        self.statistics['sumtime'] += int(time*1000)
        self.statistics['overallresult'] = Solution.updated_status(
            self.statistics['overallresult'],status)

    def timecmd(self, timefile, timelimit=0):
        timekill = 'timeout %s' % timelimit if timelimit else ''
        return '/usr/bin/time -f "%s" -o %s -q %s' % ('%U', timefile, timekill)
    
    def run(self, ifile, ofile, tfile, checker, args):
        if not self.ready:
            error('%s not prepared for execution' % self.name)
        so = subprocess.PIPE if self.quiet else None
        se = subprocess.PIPE if self.quiet else None
        timefile = '.temptime-%s-%s-%s' % (
            tobasealnum(self.name),
            tobasealnum(ifile),
            os.getpid(),
        )
        # run solution
        usertime = -1
        timecmd = self.timecmd(timefile, int(args.timelimit))
        cmd = '%s %s < %s > %s' % (timecmd, self.runcmd, ifile, tfile)
        try:
            result = subprocess.call(cmd, stdout=so, stderr=se, shell=True)
            usertime = float(open(timefile,'r').read().strip())
            if result == 0:     status = 'OK'
            elif result == 124: status = 'TLE'
            elif result > 0:    status = 'EXC'
            else:               status = 'INT'

            if status == 'OK':
                checkres = checker.check(ifile, ofile, tfile)
                if checkres != 0:
                    status = 'WA'
                    if checkres != 1:
                        warning('Checker exited with status %s' % checkres)
        except Exception as e:
            result = -1
            status = 'INT'
            warning(str(e))
        finally:
            if os.path.exists(timefile):
                os.remove(timefile)

        # construct summary
        self.record(ifile, status, usertime)
        runcmd = ('{:<'+str(Solution.cmd_maxlen)+'s}').format(self.runcmd)
        time = '{:6d}'.format(int(usertime*1000))

        if args.inside_oneline:
            input = ('{:'+str(args.inside_inputmaxlen)+'s}').format(
                (ifile.rsplit('/', 1)[1]))
            summary = '%s < %s %sms.' % (runcmd,input,time)
        else:
            summary = '    %s  %sms.' % (runcmd,time)
       
        okwastatus = 'OK' if status == 'OK' else 'WA'
        print(colorize(okwastatus,summary), colorize(status,status,True))
        
        if status == 'INT':
            error('Internal error. Testing will not continue', doquit=True)

class Validator(Program):
    def compare_mask(self):
        return (-2, self.name)

class Checker(Program):
    def compare_mask(self):
        return (-3, self.name)
    
    def __init__(self, name, args):
        super().__init__(name, args)
        if name=='diff':
            self.runcmd = 'diff'
            self.compilecmd = None
            self.forceexecute = True

    def diff_cmd(self, ifile, ofile, tfile):
        diff_map = {
            'diff' : ' %s %s > /dev/null' % (ofile, tfile), 
            'check' : ' %s %s %s > /dev/null' % (ifile, ofile, tfile), 
            'chito' : ' %s %s %s > /dev/null' % (ifile, tfile, ofile), 
            'test' : ' %s %s %s %s %s' % ('./', './', ifile, ofile, tfile), 
        }
        for key in diff_map:
            if tobasealnum(self.name).startswith(key):
                return self.runcmd + diff_map[key]
        return None

    def check(self, ifile, ofile, tfile):
        se = subprocess.PIPE if self.quiet else None
        return subprocess.call(
            self.diff_cmd(ifile, ofile, tfile),
            shell=True, stderr=se) 

class Generator(Program):
    def compare_mask(self):
        return (-4, self.name)
    
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

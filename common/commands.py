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

Program types      -- What is recognized and smartly processed.
                      It is determined mainly by extension and number of words.
  multiple words   -- Run as it is.
  noextension      -- Check if binary should be compiled and maybe compile.
                      Then run ./noextension if file exists and noextension otherwise.
  program.ext      -- If c/cc/c++/pas/java, compile and run binary.
  program.ext      -- If .pyX, run as 'pythonX program.ext. py = py3
  
'''

import os, subprocess
from common.messages import error, warning, infob, infog

def isfilenewer(file1, file2):
    if not os.path.exists(file1) or not os.path.exists(file2):
        return None
    return os.path.getctime(file1) > os.path.getctime(file2)

def toalnum(s):
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
    def transform(self):
        name = self.name
        self.compilecmd = None
        self.source = None
        self.ext = None
        self.runcmd = name
        self.filestoclear = []
        
        # if it is final command, dont do anything
        if self.args.execute or len(name.split())>1:
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
            self.args.compile and 
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

        if os.access(self.runcmd, os.X_OK):
            if self.runcmd.isalnum():
                self.runcmd = './'+self.runcmd
        else:
            if self.ext in ext_py3:
                self.runcmd = 'python3 ' + self.source
            if self.ext in ext_py2:
                self.runcmd = 'python2 ' + self.source
            if self.ext in ext_java:
                self.runcmd = 'java ' + self.runcmd

    def prepare(self):
        so = subprocess.PIPE if self.args.quiet else None
        se = subprocess.STDOUT if self.args.quiet else None

        if self.compilecmd == None:
            ready = True
        else: 
            infob('Compiling: %s' % self.compilecmd)
            try:
                subprocess.check_call(self.compilecmd, shell=True, 
                    stdout=so ,stderr=se)
                ready = True
            except:
                error('Compile failed')
    
    def clearfiles(self):
        for f in self.filestoclear:
            if os.path.exists(f): 
                os.remove(f)
            else:
                warning('Not found %s' % f)

    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.ready = False

        # compute runcmd, compilecmd and filestoclear
        self.transform()

class Solution(Program):
    def timecmd(self, timelimit=0):
        timekill = 'timeout %s' % timelimit if timelimit else ''
        return '/usr/bin/time -f "%s" -q 2>&1 %s' % ('%U', timekill)
    
    def run(self, inputname):
        input_file = ''
        output_file = ''
        result_file = ''

        timecmd = self.timecmd(int(self.args.timelimit))
        cmd = '%s %s '

class Checker(Program):
    pass

class Generator(Program):
    pass
    
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

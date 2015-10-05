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

import sys, os, subprocess
from common.messages import error, warning, infob, infog, colorize

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
        so = subprocess.PIPE if self.quiet else None
        se = subprocess.STDOUT if self.quiet else None
        if self.compilecmd != None:
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
    cmd_maxlen = 0
    
    def __init__(self, name, args):
        super().__init__(name, args)
        self.statistics = {
            'maxtime': 0,
            'sumtime': 0,
            'batchresults': {},
        }
    
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
        usertime = ''
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


class Checker(Program):
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

# (c) 2014 jano <janoh@ksp.sk> 
import argparse, sys

class Parser:
    dest = 'dest'
    default = 'default'
    action = 'action'
    nargs = 'nargs'
    metavar = 'metavar'
    help = 'help'
    options = {
        # file names
        'indir' : (('-i', '--input'), {dest:'indir', default:'test',
            help:'directory with input files (default=test)'}),
        'outdir' : (('-o', '--output'), {dest:'outdir', default:'test',
            help:'directory for output and temporary files (default=test)'}),
        'inext' : (('-I',), {dest:'inext', default:'in',
            help:'extension of input files (default=in)'}),
        'outext' : (('-O',), {dest:'outext', default:'out',
            help:'extension of output files (default=out)'}),
        'tempext' : (('-T',), {dest:'tempext', default:'temp',
            help:'extension of temporary files (default=temp)'}),
        'reset' : (('-R', '--Reset'), {dest:'reset', action:'store_true',
            help:'recompute outputs, similar as -T out'}),

        # testing options
        'timelimit' : (('-t', '--time'), {dest:'timelimit', default:'0',
            help:'set timelimit (default=infinity)'}),
        'memorylimit' : (('-m', '--memory'), {dest:'memorylimit',
            help:'set memorylimit (default=infinity)', default:'0'}),
        'wrapper' : (('-w', '--wrapper'), {dest:'wrapper', nargs:'?',
            default:False, metavar:'PATH',
            help:'use wrapper, default PATH="$WRAPPER"'}),
        'diffcmd' : (('-d', '--diff'), {dest:'diffcmd', default:'diff',
            help:'program which checks correctness of output. '+
            'Arguments given to program depends of prefix: \n'+
            '  diff $our $theirs' +
            '  check $inp $our $theirs' +
            '  ch_ito $inp $theirs $our' +
            '  test $dir $name $i $o $t' +
            '  (default=diff)'}),

        # running options
        'compile' : (('-r', '--nocompile'), {dest:'compile', action:'store_false',
            help:'do not try to compile'}),
        'execute' : (('-x', '--execute'), {dest:'execute', action:'store_true',
            help:'treat programs as bash commands'}),

        # verbosing
        'colorful' : (('-b', '--boring', '--no-color'), {dest:'colorful', 
            action:'store_false', help:'turn colors off'}),
        'quiet' : (('-q', '--quiet'), {dest:'quiet', action:'store_true',
            help:'do let subprograms print stuff'}),
        'Quiet' : (('-Q', '--Quiet'), {dest:'Quiet', action:'store_true',
            help:'do not print anything'}),
        
        # cleanup
        'cleartemp' : (('-k', '--keep-temp'), {dest:'cleartemp', action:'store_false',
            help:'dont remove temporary files after finishing'}),
        'clearbin' : (('-K', '--keep-bin'), {dest:'clearbin', action:'store_false',
            help:'dont remove binary files after finishing'}),
        
        # what to do
        'programs' : (('programs',), {nargs:'+',
            help:'list of programs to be run'}),
        'description' : (('description',), {nargs:'?',
            help:'recipe for inputs. If not provided, read it from stdin'}),
    }


    def __init__(self, description, arguments):
        self.parser = argparse.ArgumentParser(description=description)
        for arg in arguments:
            args, kwargs = self.options.get(arg, (None, None))
            if args == None or kwargs == None:
                raise NameError('Unrecognized option %s' % arg)
            self.parser.add_argument(*args, **kwargs)
        
    def parse(self):
        self.args = self.parser.parse_args()
        return self.args

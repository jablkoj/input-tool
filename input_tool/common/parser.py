# (c) 2014 jano <janoh@ksp.sk>
import argparse

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
        'batchname': (('-b', '--batch'), {dest:'batchname', default:'00.sample',
            help:'batch name (default=00.sample)'}),
        'multi': (('-m', '--force-multi'), {dest:'multi', action:'store_true',
            help:'force batch (always print .a before extension)'}),

        # testing options
        'timelimit' : (('-t', '--time'), {dest:'timelimit', default:'0',
            help:'set timelimit (default=infinity), '+
            'can be set in optional per language format (example 1.5,py2=5,cxx=0.5,java=2)'}),
        'warntimelimit' : (('--wtime',), {dest:'warntimelimit', default:'0',
            help:'set warn timelimit (default=infinity) which issues warning but does not fail, '+
            'can be set in optional per language format (example 1.5,py2=5,cxx=0.5,java=2)'}),
        'memorylimit' : (('-m', '--memory'), {dest:'memorylimit',
            help:'set memorylimit (default=infinity)', default:'0'}),
        'wrapper' : (('-w', '--wrapper'), {dest:'wrapper', nargs:'?',
            default:False, metavar:'PATH',
            help:'use wrapper, default PATH="$WRAPPER"'}),
        'diffcmd' : (('-d', '--diff'), {dest:'diffcmd', default:'diff',
            help:'program which checks correctness of output. '+
            'Arguments given to program depends of prefix: '+
            "       diff $our $theirs," +
            "       check $inp $our $theirs," +
            "       ch_ito $inp $theirs $our," +
            "       test $dir $name $i $o $t," +
            "       (default=diff)"}),
        'fskip': (('--fskip',), {dest:'fskip', action:'store_true',
            help:'skip the rest of input files in the same batch after first fail'}),
        'dupprog': (('--dupprog',), {dest:'dupprog', action:'store_true',
            help:'keep duplicate programs'}),

        # running options
        'compile' : (('--no-compile',), {dest:'compile', action:'store_false',
            help:'do not try to compile'}),
        'sort' : (('--no-sort',), {dest:'sort', action:'store_false',
            help:'do not change order of programs'}),
        'execute' : (('-x', '--execute'), {dest:'execute', action:'store_true',
            help:'treat programs as bash commands. Dont try to do something smart '+
                  'as compiling'}),
        'pythoncmd' : (('--pythoncmd',), {dest:'pythoncmd', default:'python',
            help:'what command is used to execute python, e.g. python or pypy'}),

        # verbosing
        'colorful' : (('-b', '--boring'), {dest:'colorful',
            action:'store_false', help:'turn colors off'}),
        'Colorful' : (('-B', '--Boring'), {dest:'colorful',
            action:'store_false', help:'turn colors off'}),
        'colortest' : (('--colortest',), {dest:'colortest', action:'store_true',
            help:'test colors and exit'}),
        'quiet' : (('-q', '--quiet'), {dest:'quiet', action:'store_true',
            help:'dont let subprograms print stuff'}),
        'Quiet' : (('-Q', '--Quiet'), {dest:'Quiet', action:'store_true',
            help:'dont print anything'}),
        'stats' : (('-s', '--statistics'), {dest:'stats', action:'store_true',
            help:'print statistics'}),

        # cleanup
        'cleartemp' : (('-k', '--keep-temp'), {dest:'cleartemp', action:'store_false',
            help:'dont remove temporary files after finishing'}),
        'clearbin' : (('-K', '--keep-bin'), {dest:'clearbin', action:'store_false',
            help:'dont remove binary files after finishing'}),
        'clearinput' : (('-k', '--keep-inputs'), {dest:'clearinput', action:'store_false',
            help:'dont remove old input files. Samples are never removed'}),

        # what to do
        'programs' : (('programs',), {nargs:'+',
            help:'list of programs to be run'}),
        'description' : (('description',), {nargs:'?',
            help:'recipe for inputs. If not provided, read it from stdin.'}),
        'gencmd' : (('-g', '--gen'), {dest:'gencmd', default:'gen',
            help:'generator used for generating inputs (default=gen)'}),
        'task' : (('task',), {nargs:'?',
            help:'task statement. If not provided, read it from stdin.'}),
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

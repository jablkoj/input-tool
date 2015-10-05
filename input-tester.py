#!/usr/bin/python3
# (c) 2014 jano <janoh@ksp.sk> 
# Complex script that can test solutions
description = '''
Input tester.
Test all given solutions on all inputs.
By default, if outputs dont exits, use the first solution to generate them.
By default, automatically decide, how to compile and run solution.
'''
options = [
    'indir', 'outdir', 'inext', 'outext', 'tempext', 'reset',
    'timelimit', 'diffcmd',
    'compile', 'execute',
    'colorful', 'quiet', 
    'cleartemp', 'clearbin', 
    'programs',
]

from common.parser import Parser
from common.commands import Solution, Checker
from common.messages import messages_setup, error, warning, \
    info, infob, infog, colorize
import atexit, os

parser = Parser(description, options)
args =  parser.parse()
messages_setup(args)


# ----------- prepare programs ---------------- 

programs = []
solutions = []
checker = Checker(args.diffcmd, args)
for p in args.programs:
    solutions.append(Solution(p, args))
programs += solutions
programs.append(checker) 

def cleanup():
    if args.clearbin:
        for p in programs:
            p.clearfiles() 
atexit.register(cleanup)

for p in programs:
    p.prepare()

# ------------ prepare inputs ----------------

inputs = sorted(filter( lambda x: x.endswith(args.inext),
                        os.listdir(args.indir) ))

if args.outext != args.tempext and not args.reset:
    outputs = sorted(filter( lambda x: x.endswith(args.outext),
                             os.listdir(args.outdir) ))
    if len(outputs) > 0 and len(outputs) < len(inputs):
        warning("Incomplete output files.")
else:
    infob("Outputs will be regenerated")

def get_result_file(out_file, temp_file):
    if args.reset: return out_file
    if os.path.exists(out_file): return temp_file
    else: 
        infob("File %s not found. Will be created now." % out_file)
        return out_file

def temp_clear():
    tempfiles = sorted(filter( lambda x: x.endswith(args.tempext),
                            os.listdir(args.outdir) ))
    if len(tempfiles):
        info("Deleting all .%s files" % args.tempext);
        for tempfile in tempfiles:
            os.remove(args.outdir+'/'+tempfile);

temp_clear()

setattr(args, 'inside_oneline', len(solutions) <= 1)
setattr(args, 'inside_inputmaxlen', max(map(len, inputs)))

# ------------ test solutions ----------------

for input in inputs: 
    input_file = args.indir + '/' + input
    output_file = args.outdir + '/' + input.rsplit('.', 1)[0] + '.' + args.outext
    temp_file = args.outdir + '/' + input.rsplit('.', 1)[0] + '.' + args.tempext
    
    if len(solutions) > 1:
        print("%s >" % (input))

    for sol in solutions:
        result_file = get_result_file(output_file, temp_file)
        sol.run(input_file,output_file,result_file,checker,args) 
        
        '''exc = os.system(cmd)
        time = open(time_file,'r').read()
        os.remove(time_file)

        if time.startswith('Command exited with non-zero status 124'):
            time = time.strip().rsplit('\n', 1)[-1]
            status = 'TLE'
        if status == 'OK' and exc:
            status = 'EXC'
        if status == 'OK' and diffResult(input_file,output_file,result_file):
            status = 'WA'
        time = time.strip()

        if args.clear:
            os.remove(result_file)

        if not args.Quiet:
            if len(commands) == 1:
                colorful(status, "%s < %s: %ss. %s" % (command, input, time, status))
            else:
                colorful(status, "    %-20s %10ss. %s" % (command, time, status))
        '''

# ------------ print sumary ------------------



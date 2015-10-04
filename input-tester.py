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
    'timelimit', 'memorylimit', 'diffcmd',
    'compile', 'execute',
    'colorful', 'quiet', 
    'cleartemp', 'clearbin', 
    'programs',
]

from common.parser import Parser
from common.commands import Solution, Checker
from common.messages import messages_setup, error, warning, \
    message, infob, infog, colorful
import atexit

parser = Parser(description, options)
args =  parser.parse()
messages_setup(args)


# ----------- prepare programs ---------------- 

programs = []
solutions = []
for p in args.programs:
    solutions.append(Solution(p, args))
programs += solutions

def cleanup():
    if args.clearbin:
        for p in programs:
            p.clearfiles() 
atexit.register(cleanup)

for p in programs:
    p.prepare()


# ------------ prepare inputs ----------------


# ------------ test solutions ----------------


# ------------ print sumary ------------------



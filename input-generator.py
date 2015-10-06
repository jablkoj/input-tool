#!/usr/bin/python3
# (c) 2014 jano <janoh@ksp.sk> 
# Script that helps generating inputs for contests
description = '''
Input generator.
Generate inputs based on input description file. Each line is provided as input to
generator. Empty lines separate batches.
'''
options = [
    'indir', 'inext', 
    'compile', 'execute', 'gencmd',
    'colorful', 'quiet',
    'clearinput', 'clearbin',
    'description',
]

from common.parser import Parser
from common.recipes import Recipe
from common.commands import Generator
from common.messages import *
import atexit, os, sys

parser = Parser(description, options)
args =  parser.parse()
messages_setup(args)

if args.description:
    recipe = Recipe(open(args.description, 'r'))
else:
    recipe = Recipe(sys.stdin)

recipe.process()
programs = recipe.programs

# {{{ ----------- prepare programs -------------------
generator = Generator(args.gencmd, args)
programs = [generator]

def cleanup():
    if args.clearbin:
        for p in programs:
            p.clearfiles() 
atexit.register(cleanup)

for p in programs:
    p.prepare()
# }}}

indir = args.indir
if not os.path.exists(indir):
    infob("Creating directory '%s'" % indir)
    os.makedirs(indir)

filestoclear = os.listdir(indir)
if len(filestoclear):
    infob("Cleaning directory '%s:'" % indir)
    for file in filestoclear:
        if file.endswith(args.inext) and 'sample' in file:
            info("  ommiting file '%s'" % file)
        else:
            os.remove('%s/%s' % (indir, file))
    

infob('Generating:')
recipe.inputs.sort()
leftw = max([len(i.get_name(ext=args.inext)) for i in recipe.inputs])
prev = None

for input in recipe.inputs:
    ifile = input.get_name(path=indir + '/', ext=args.inext)
    short = ('{:>'+str(leftw)+'s}').format(input.get_name(ext=args.inext))
    text = input.get_text()
    
    generator.generate(ifile, text)
    
    if prev and prev.batch != input.batch:
        print(' '*(leftw+4)+'.')
    prev = input

    print('  %s  <  %s' % (short, text))

infob('Done')

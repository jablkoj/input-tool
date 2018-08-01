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
    'clearinput', 'clearbin', 'cleanup',
    'description',
]

from common.parser import Parser
from common.recipes import Recipe
from common.commands import Generator
from common.messages import *
import atexit
import os
import sys

parser = Parser(description, options)
args = parser.parse()
Color.setup(args)

filestoclear = os.listdir(args.indir)
if len(filestoclear) and args.clearinput:
    infob("Cleaning directory '%s:'" % args.indir)
    # delete only following files
    exttodel = ['in', 'out', 'temp', args.inext]
    for file in filestoclear:
        if file.endswith(args.inext) and 'sample' in file:
            info("  ommiting file '%s'" % file)
        elif file.rsplit('.',1)[-1] not in exttodel:
            info("  not deleting file '%s'" % file)
        else:
            os.remove('%s/%s' % (args.indir, file))

if args.cleanup:
    infob('Done')
    exit(0)
elif args.description:
    recipe = Recipe(open(args.description, 'r'))
else:
    recipe = Recipe(sys.stdin)

recipe.process()
programs = {x:Generator(x,args) for x in recipe.programs}

# {{{ ----------- prepare programs -------------------
gencmd = args.gencmd
programs[gencmd] = Generator(gencmd, args)

def cleanup():
    if args.clearbin:
        for p in programs:
            programs[p].clear_files()
atexit.register(cleanup)

for p in sorted(programs):
    programs[p].prepare()
# }}}

infob('Generating:')
recipe.inputs.sort()
leftw = max([len(i.get_name(ext=args.inext)) for i in recipe.inputs])
prev = None

for input in recipe.inputs:
    ifile = input.get_name(path=args.indir + '/', ext=args.inext)
    short = ('{:>' + str(leftw) + 's}').format(input.get_name(ext=args.inext))

    programs[input.generator or gencmd].generate(
        ifile,
        input.get_generation_text(),
    )

    if prev and prev.batch != input.batch:
        print(' ' * (leftw + 4) + '.')
    prev = input

    print('  %s  <  %s' % (short, input.get_info_text(len(short)+4)))

infob('Done')

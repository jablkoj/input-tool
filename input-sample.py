#!/usr/bin/python3
# (c) 2014 jano <janoh@ksp.sk>
# Script that creates sample inputs from task statements or vice versa
description = '''
Input sample.
Given task statement, create sample input and output files. 
'''
#TODO Can be used in opposite direction.
#TODO smart -- detect prefix and multi. 
options = [
    'indir', 'outdir',  'inext', 'outext',
    'Colorful',
    'batchname', 'multi',
    'task',
]

from common.parser import Parser
from common.recipes import Input, Sample, prepare
from common.messages import *
import sys

parser = Parser(description, options)
args = parser.parse()
Color.setup(args)
prepare(args)

samples_in = []
samples_out = []

if args.task:
    lines = open(args.task, 'r').readlines()
else:
    lines = sys.stdin.readlines()

if args.multi:
    Input.maxid = 1

active = None

warning_messages = {
    'noend': 'In %s some line does not end with \\n',
    'empty': '%s is empty',
    'emptyline': '%s is just an empty line',
    'ws-start': 'In %s some line starts with a whitespace',
    'ws-end': 'In %s some line ends with a whitespace',
    'bl-start': '%s starts with blank line',
    'bl-end': '%s ends with blank line',
}

tips = []

def check_line(line):
    if line != '\n' and line.lstrip() != line: tips.append('ws-start')
    if line[-1] != '\n': tips.append('noend')
    else:
        if line.rstrip() != line[:-1].rstrip(): tips.append('ws-end')

def check_text(text):
    if text == '': 
        tips.append('empty')
        return
    if text == '\n':
        tips.append('emptyline')
        return
    if text[0] == '\n': tips.append('bl-start')
    if text[-1] == '\n' and text[-2] == '\n': tips.append('bl-end')

for line in lines:
    if line.strip() == '```vstup':
        active = samples_in
        active_lines = ''
        continue
    if line.strip() == '```vystup':
        active = samples_out
        active_lines = ''
        continue
    if line.strip() == '```':
        if active != None: 
            active.append(active_lines)
        active = None
    elif active != None:
        check_line(line)
        active_lines += line

if len(samples_in) != len(samples_out):
    error('Number of inputs and outputs must be the same.')
if len(samples_in) == 0:
    warning('No inputs found in task statements.')

samples = []

for i in range(len(samples_in)):
    samples.append(
        Sample(samples_in[i], args.indir, args.batchname, i, args.inext),
    ); 
    samples.append(
        Sample(samples_out[i], args.outdir, args.batchname, i, args.outext),
    );

for sample in samples:
    check_text(sample.text)
    sample.compile()

tips = sorted(list(set(tips)))
for w in tips:
    message = warning_messages[w] % 'some input/output'
    message = message[0].upper() + message[1:]
    warning(message)

import os
indir = args.indir
for d in (args.indir, args.outdir):
    if not os.path.exists(d):
        infob("Creating directory '%s'" % d)
        os.makedirs(d)

for sample in samples:
    sample.save()

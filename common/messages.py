# (c) 2014 jano <janoh@ksp.sk> 
# Various types of messages, with colors
import sys

__sow = sys.stdout.write
__sew = sys.stderr.write

def messages_setup(args):
    global red,green,yellow,blue,normal
    global Bred,Bgreen,Byellow,Bblue
    if args.colorful:
        red = '\033[31m'
        green = '\033[32m'
        yellow = '\033[33m'
        blue = '\033[34m'
        normal = '\033[0m'
        
        Bred = '\033[31;1m'
        Bgreen = '\033[32;1m'
        Byellow = '\033[33;1m'
        Bblue = '\033[34;1m'
    else:
        red, green, yellow, blue, normal = ('')*5
        Bred, Bgreen, Byellow, Bblue= ('')*4

def test():
    message("message")
    infob("blue")
    infog("green")
    warning("warning")
    error("error", quit=False)
    colorful('OK', 'ok')
    colorful('WA', 'wa')
    colorful('TLE', 'tle')
    colorful('EXC', 'exc')
    
def error(text, doquit=True):
    __sew("%s%s%s\n" % (red, text, normal))
    if doquit: quit(1)
def warning(text):
    __sew("%s%s%s\n" % (red, text, normal))
def infob(text):
    __sew("%s%s%s\n" % (blue, text, normal))
def infog(text):
    __sew("%s%s%s\n" % (green, text, normal))
def message(text):
    __sew("%s\n" % text)

def colorful(status, text):
    if status=='OK':
        __sow("%s%s%s\n" % (Bgreen, text, normal))
    elif status=='TLE':
        __sow("%s%s%s\n" % (Bblue, text, normal))
    elif status=='EXC':
        __sow("%s%s%s\n" % (Byellow, text, normal))
    elif status=='WA':
        __sow("%s%s%s\n" % (Bred, text, normal))
    

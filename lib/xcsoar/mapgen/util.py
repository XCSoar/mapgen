import subprocess

def slurp(file):
    f = open(file, 'r')
    try:
        return f.read()
    finally:
        f.close()

def spew(file, content):
    f = open(file, 'w')
    try:
        f.write(str(content))
    finally:
        f.close()

def command(args):
    try:
        subprocess.Popen(args).wait()
    except Exception as e:
        print("Executing " + str(args) + " failed")
        raise

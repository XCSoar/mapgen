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

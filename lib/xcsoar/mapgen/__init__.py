import sys

if sys.hexversion < 0x02070000:
    print('At least Python 2.7 is required')
    sys.exit(1)

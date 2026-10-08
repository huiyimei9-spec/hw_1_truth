import sys
import random

name = sys.argv[1]
with open(name) as file:

name_file = sys.argv[1]
with open(name_file) as file:

    for line in file:
        if random.random() < 0.01:
            print(line)
